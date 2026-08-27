import itertools
import logging
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import TypedDict

from tqdm import tqdm

from quarto_ai.game.types import GameResult
from quarto_ai.players.base import BaseModel
from quarto_ai.runners.elo import EloSystem
from quarto_ai.runners.game_runner import GameRunner

logger = logging.getLogger("quarto_ai.tournament")


class MatchupResult(TypedDict):
    player_a_name: str
    player_b_name: str
    games_per_side: int
    total_games: int
    a_wins: int
    b_wins: int
    draws: int
    starter_wins: int
    follower_wins: int


class LeaderboardEntry(TypedDict):
    player: BaseModel
    wins: int
    draws: int
    losses: int
    total_games: int
    elo: float


class ChampionshipResult(TypedDict):
    leaderboard: list[LeaderboardEntry]
    matchups: list[MatchupResult]


def _run_single_game_worker(args: tuple[BaseModel, BaseModel]) -> tuple[bool, bool, bool]:
    """
    Worker function executed by ProcessPoolExecutor in child processes.
    Takes a tuple (p0, p1) and runs a single game.

    :return: Tuple of (is_p0_win, is_p1_win, is_draw).
    """
    p0, p1 = args
    logging.getLogger("quarto_ai").setLevel(logging.WARNING)
    runner = GameRunner(p0, p1)
    runner.run()
    res = runner.game.result
    return (
        res == GameResult.PLAYER_1,
        res == GameResult.PLAYER_2,
        res == GameResult.DRAW,
    )


class TournamentRunner:
    """Runner that schedules matches between different AIs and collects statistics."""

    def _record_game_outcome(
        self,
        results: MatchupResult,
        p0: BaseModel,
        player_a: BaseModel,
        is_p0_win: bool,
        is_p1_win: bool,
        is_draw: bool,
    ) -> None:
        """Helper to record the outcome of a single game in results dictionary."""
        if is_draw:
            results["draws"] += 1
        elif is_p0_win:
            results["starter_wins"] += 1
            if p0.name == player_a.name:
                results["a_wins"] += 1
            else:
                results["b_wins"] += 1
        elif is_p1_win:
            results["follower_wins"] += 1
            if p0.name == player_a.name:
                results["b_wins"] += 1
            else:
                results["a_wins"] += 1

    def run_matchup(
        self,
        player_a: BaseModel,
        player_b: BaseModel,
        games_per_side: int,
        max_workers: int | None = None,
        parallel: bool = True,
    ) -> MatchupResult:
        """
        Runs a series of games between two players.
        Each player gets to start (Player 0) exactly games_per_side times.

        :param player_a: First player model.
        :param player_b: Second player model.
        :param games_per_side: Number of games each player starts.
        :param max_workers: Maximum process pool workers (None for default CPU count).
        :param parallel: Whether to use multiprocessing.
        :return: Dict of results.
        """
        if games_per_side <= 0:
            raise ValueError("games_per_side must be at least 1.")

        tasks = [(player_a, player_b)] * games_per_side + [(player_b, player_a)] * games_per_side

        results: MatchupResult = {
            "player_a_name": player_a.name,
            "player_b_name": player_b.name,
            "games_per_side": games_per_side,
            "total_games": len(tasks),
            "a_wins": 0,
            "b_wins": 0,
            "draws": 0,
            "starter_wins": 0,
            "follower_wins": 0,
        }

        desc = f"Matchup: {player_a.name} vs {player_b.name}"

        engine_logger = logging.getLogger("quarto_ai")
        original_level = engine_logger.level
        engine_logger.setLevel(logging.WARNING)

        with tqdm(total=len(tasks), desc=desc, unit="game") as pbar:
            if parallel:
                with ProcessPoolExecutor(max_workers=max_workers) as executor:
                    future_to_task_idx = {
                        executor.submit(_run_single_game_worker, task): i
                        for i, task in enumerate(tasks)
                    }

                    for future in as_completed(future_to_task_idx):
                        i = future_to_task_idx[future]
                        p0, _ = tasks[i]
                        is_p0_win, is_p1_win, is_draw = future.result()
                        self._record_game_outcome(
                            results, p0, player_a, is_p0_win, is_p1_win, is_draw
                        )
                        pbar.update(1)
            else:
                for task in tasks:
                    p0, _ = task
                    is_p0_win, is_p1_win, is_draw = _run_single_game_worker(task)
                    self._record_game_outcome(results, p0, player_a, is_p0_win, is_p1_win, is_draw)
                    pbar.update(1)

        engine_logger.setLevel(original_level)
        return results

    def _update_leaderboard_stats(
        self,
        leaderboard: dict[str, LeaderboardEntry],
        player_a: BaseModel,
        player_b: BaseModel,
        results: MatchupResult,
    ) -> None:
        """Helper to update championship stats for a pair of players after a matchup."""
        a_name, b_name = player_a.name, player_b.name
        wins_a = results["a_wins"]
        wins_b = results["b_wins"]
        draws = results["draws"]
        total = results["total_games"]

        leaderboard[a_name]["wins"] += wins_a
        leaderboard[a_name]["draws"] += draws
        leaderboard[a_name]["losses"] += wins_b
        leaderboard[a_name]["total_games"] += total

        leaderboard[b_name]["wins"] += wins_b
        leaderboard[b_name]["draws"] += draws
        leaderboard[b_name]["losses"] += wins_a
        leaderboard[b_name]["total_games"] += total

        # Update Elo ratings
        new_elo_a, new_elo_b = EloSystem.calculate_new_ratings(
            leaderboard[a_name]["elo"],
            leaderboard[b_name]["elo"],
            wins_a,
            wins_b,
            draws,
        )
        leaderboard[a_name]["elo"] = new_elo_a
        leaderboard[b_name]["elo"] = new_elo_b

    def run_championship(
        self,
        players: Sequence[BaseModel],
        games_per_matchup: int,
        max_workers: int | None = None,
        parallel: bool = True,
    ) -> ChampionshipResult:
        """
        Runs a round-robin tournament where every player plays every other player once.
        Each pair matchup runs games_per_matchup per side.

        :param players: List of AI players.
        :param games_per_matchup: Games per side for each unique player pair.
        :param max_workers: Maximum process pool workers.
        :param parallel: Whether to use multiprocessing.
        :return: Sorted leaderboard list.
        """
        if len(players) < 2:
            raise ValueError("Championship requires at least 2 players.")

        leaderboard: dict[str, LeaderboardEntry] = {
            p.name: {
                "player": p,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "total_games": 0,
                "elo": EloSystem.INITIAL_RATING,
            }
            for p in players
        }

        all_matchups: list[MatchupResult] = []

        for p_a, p_b in itertools.combinations(players, 2):
            results = self.run_matchup(
                p_a, p_b, games_per_matchup, max_workers=max_workers, parallel=parallel
            )
            all_matchups.append(results)
            self._update_leaderboard_stats(leaderboard, p_a, p_b, results)

        sorted_leaderboard = sorted(
            leaderboard.values(), key=lambda x: (x["elo"], x["wins"]), reverse=True
        )
        return {"leaderboard": sorted_leaderboard, "matchups": all_matchups}
