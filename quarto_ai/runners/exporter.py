import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quarto_ai.runners.tournament_runner import (
        ChampionshipResult,
        LeaderboardEntry,
        MatchupResult,
    )

logger = logging.getLogger("quarto_ai.exporter")


class ConsoleExporter:
    """Exports tournament results to the standard console logger."""

    @staticmethod
    def print_matchup_report(results: "MatchupResult") -> None:
        """Logs a formatted summary of a 1v1 matchup."""
        total = results["total_games"]
        a_pct = (results["a_wins"] / total) * 100 if total > 0 else 0
        b_pct = (results["b_wins"] / total) * 100 if total > 0 else 0
        draw_pct = (results["draws"] / total) * 100 if total > 0 else 0

        starter_pct = (results["starter_wins"] / total) * 100 if total > 0 else 0
        follower_pct = (results["follower_wins"] / total) * 100 if total > 0 else 0

        logger.info("\n" + "=" * 50)
        logger.info(f"MATCHUP REPORT: {results['player_a_name']} vs {results['player_b_name']}")
        logger.info("=" * 50)
        logger.info(f"Total Games: {total}")
        logger.info(f"{results['player_a_name']} Wins: {results['a_wins']} ({a_pct:.1f}%)")
        logger.info(f"{results['player_b_name']} Wins: {results['b_wins']} ({b_pct:.1f}%)")
        logger.info(f"Draws: {results['draws']} ({draw_pct:.1f}%)")
        logger.info("-" * 50)
        logger.info("Starting Bias Analysis:")
        logger.info(f"Player 0 (Starter) Wins:  {results['starter_wins']} ({starter_pct:.1f}%)")
        logger.info(f"Player 1 (Follower) Wins: {results['follower_wins']} ({follower_pct:.1f}%)")
        logger.info(f"Draws:                     {results['draws']} ({draw_pct:.1f}%)")
        logger.info("=" * 50 + "\n")

    @staticmethod
    def print_championship_report(leaderboard: list["LeaderboardEntry"]) -> None:
        """Logs a formatted leaderboard table for a championship."""
        logger.info("\n" + "=" * 70)
        logger.info("CHAMPIONSHIP LEADERBOARD")
        logger.info("=" * 70)
        logger.info(
            f"{'Rank':<5} | {'Player':<20} | {'Elo':<6} | "
            f"{'Wins':<6} | {'Draws':<6} | {'Losses':<6} | {'Win Rate':<8}"
        )
        logger.info("-" * 70)

        for rank, entry in enumerate(leaderboard, 1):
            total = entry["total_games"]
            win_rate = (entry["wins"] / total) * 100 if total > 0 else 0.0

            logger.info(
                f"{rank:<5} | {entry['player'].name:<20} | {int(entry['elo']):<6} | "
                f"{entry['wins']:<6} | {entry['draws']:<6} | "
                f"{entry['losses']:<6} | {win_rate:.1f}%"
            )
        logger.info("=" * 70 + "\n")


class MarkdownExporter:
    """Exports tournament results to a Markdown file."""

    @classmethod
    def generate_report(
        cls, results: "ChampionshipResult", filepath: str | Path, methodology: str = ""
    ) -> None:
        """Main entry point. Orchestrates the file creation and writes all sections."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        content = []
        content.append(cls._generate_header())
        if methodology:
            content.append(f"## Methodology\n\n{methodology}\n")
        content.append(cls._generate_leaderboard(results["leaderboard"]))
        content.append(cls._generate_head_to_head_matrix(results["matchups"]))
        content.append(cls._generate_head_to_head(results["matchups"]))
        content.append(cls._generate_bias_analysis(results["matchups"]))

        path.write_text("\n".join(content), encoding="utf-8")
        logger.info(f"Benchmark report generated successfully at: {path.absolute()}")

    @classmethod
    def _generate_header(cls) -> str:
        """Generates title and date of execution."""
        date_str = datetime.now().strftime("%B %d, %Y")
        return f"# Quarto AI Benchmark Results\n\n*Generated on: {date_str}*\n"

    @classmethod
    def _generate_leaderboard(cls, leaderboard: list["LeaderboardEntry"]) -> str:
        """Formats the Elo leaderboard as a Markdown table."""
        lines = [
            "## Championship Leaderboard\n",
            "| Rank | Player | Elo | Wins | Draws | Losses |",
            "|:----:|:-------|----:|-----:|------:|-------:|",
        ]

        for rank, entry in enumerate(leaderboard, 1):
            total = entry["total_games"]

            wins = entry["wins"]
            draws = entry["draws"]
            losses = entry["losses"]

            win_rate = (wins / total) * 100 if total > 0 else 0.0
            draw_rate = (draws / total) * 100 if total > 0 else 0.0
            loss_rate = (losses / total) * 100 if total > 0 else 0.0

            elo = int(entry["elo"])
            elo_diff = elo - 1500
            elo_str = (
                f"{elo} ({'+' if elo_diff > 0 else ''}{elo_diff})"
                if elo_diff != 0
                else f"{elo} (=)"
            )

            row = (
                f"| {rank} | **{entry['player'].name}** | {elo_str} | "
                f"{wins} ({win_rate:.1f}%) | {draws} ({draw_rate:.1f}%) | "
                f"{losses} ({loss_rate:.1f}%) |"
            )
            lines.append(row)

        return "\n".join(lines) + "\n"

    @classmethod
    def _generate_head_to_head_matrix(cls, matchups: list["MatchupResult"]) -> str:
        """Creates a cross-matrix summarizing win rates between all pairs."""
        player_names = set()
        win_rates: dict[str, dict[str, float]] = defaultdict(dict)

        for m in matchups:
            player_a, player_b = m["player_a_name"], m["player_b_name"]
            player_names.update([player_a, player_b])

            total = m["total_games"]
            if total > 0:
                win_rates[player_a][player_b] = (m["a_wins"] / total) * 100
                win_rates[player_b][player_a] = (m["b_wins"] / total) * 100

        players = sorted(player_names)

        lines = [
            "## Head-to-Head Win Rate Matrix\n",
            "*(Row player's win rate against Column player)*\n",
            f"| Player | {' | '.join(players)} |",
            f"|:---|{'|'.join(['---:' for _ in players])}|",
        ]

        for row_p in players:
            row_str = f"| **{row_p}** |"
            for col_p in players:
                if row_p == col_p:
                    row_str += " - |"
                else:
                    rate = win_rates.get(row_p, {}).get(col_p)
                    row_str += f" {rate:.1f}% |" if rate is not None else " N/A |"
            lines.append(row_str)

        return "\n".join(lines) + "\n"

    @classmethod
    def _generate_head_to_head(cls, matchups: list["MatchupResult"]) -> str:
        """Creates a table summarizing each 1v1 matchup."""
        lines = [
            "## Head-to-Head Matchups\n",
            "| Matchup | Games Played | Player A Wins | Player B Wins | Draws |",
            "|:--------|:------------:|:-------------:|:-------------:|:-----:|",
        ]

        for m in matchups:
            total = m["total_games"]
            a_name = m["player_a_name"]
            b_name = m["player_b_name"]

            a_wins = m["a_wins"]
            b_wins = m["b_wins"]
            draws = m["draws"]

            a_pct = (a_wins / total) * 100 if total > 0 else 0.0
            b_pct = (b_wins / total) * 100 if total > 0 else 0.0
            d_pct = (draws / total) * 100 if total > 0 else 0.0

            row = (
                f"| {a_name} vs {b_name} | {total} | {a_wins} ({a_pct:.1f}%) | "
                f"{b_wins} ({b_pct:.1f}%) | {draws} ({d_pct:.1f}%) |"
            )
            lines.append(row)

        return "\n".join(lines) + "\n"

    @classmethod
    def _generate_bias_analysis(cls, matchups: list["MatchupResult"]) -> str:
        """
        Aggregates all starter_wins and follower_wins to compute the global
        First-Player Advantage.
        """
        total_starter = sum(m["starter_wins"] for m in matchups)
        total_follower = sum(m["follower_wins"] for m in matchups)
        total_draws = sum(m["draws"] for m in matchups)
        total_games = sum(m["total_games"] for m in matchups)

        if total_games == 0:
            return ""

        starter_pct = (total_starter / total_games) * 100
        follower_pct = (total_follower / total_games) * 100
        draw_pct = (total_draws / total_games) * 100

        lines = [
            "## Starting-Player Bias Analysis\n",
            "| Role | Total Wins | Global Win Rate |",
            "|:-----|-----------:|----------------:|",
            f"| Player 1 (Starter) | {total_starter} | {starter_pct:.1f}% |",
            f"| Player 2 (Follower) | {total_follower} | {follower_pct:.1f}% |",
            f"| Draws | {total_draws} | {draw_pct:.1f}% |",
            "\n",
        ]
        return "\n".join(lines) + "\n"
