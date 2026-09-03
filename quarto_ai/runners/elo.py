import logging
from collections.abc import Sequence
from typing import ClassVar, TypedDict

logger = logging.getLogger("quarto_ai.elo")


class EloMatchupResult(TypedDict):
    """Minimal matchup result required by EloSystem.

    Any superset (e.g. MatchupResult from TournamentRunner) is accepted.
    """

    player_a_name: str
    player_b_name: str
    a_wins: int
    b_wins: int
    draws: int
    total_games: int


class EloSystem:
    """
    Stateless pure-math utility for computing Elo ratings across tournament matchups.

    Uses an Iterative Batch Gradient Descent approach inspired by the Bradley-Terry model
    to ensure order-invariance, numerical stability across arbitrary game volumes, and strict
    conservation of the zero-sum rating invariant.
    """

    K_FACTOR: ClassVar[float] = 8.0
    INITIAL_RATING: ClassVar[float] = 1500.0
    CONVERGENCE_THRESHOLD: ClassVar[float] = 0.01
    MAX_EPOCHS: ClassVar[int] = 1000

    @classmethod
    def calculate_ratings(
        cls,
        matchups: Sequence[EloMatchupResult],
    ) -> dict[str, float]:
        """
        Computes stable Elo ratings by iterating over all matchup results
        until convergence, eliminating match-order bias.

        All player ratings are updated simultaneously at the end of each epoch
        (batch gradient descent), guaranteeing full order-invariance and strict
        conservation of the zero-sum invariant across the entire player pool.

        :param matchups: Sequence of completed matchup statistics.
        :returns: A dictionary mapping each player name to their converged Elo rating.
        """
        player_names = {
            name
            for matchup in matchups
            for name in (matchup["player_a_name"], matchup["player_b_name"])
        }
        ratings: dict[str, float] = dict.fromkeys(player_names, cls.INITIAL_RATING)

        for epoch in range(cls.MAX_EPOCHS):
            deltas: dict[str, float] = dict.fromkeys(player_names, 0.0)

            for matchup in matchups:
                player_a = matchup["player_a_name"]
                player_b = matchup["player_b_name"]
                delta = cls._calculate_matchup_delta(
                    ratings[player_a],
                    ratings[player_b],
                    matchup["a_wins"],
                    matchup["b_wins"],
                    matchup["draws"],
                    matchup["total_games"],
                )
                deltas[player_a] += delta
                deltas[player_b] -= delta

            max_delta = 0.0
            for name in player_names:
                ratings[name] += deltas[name]
                max_delta = max(max_delta, abs(deltas[name]))

            if max_delta < cls.CONVERGENCE_THRESHOLD:
                logger.info("Elo converged after %d epochs.", epoch + 1)
                break
        else:
            logger.warning(
                "Elo did not converge within %d epochs (max_delta=%.4f).",
                cls.MAX_EPOCHS,
                max_delta,
            )

        return ratings

    @classmethod
    def _calculate_matchup_delta(
        cls,
        rating_a: float,
        rating_b: float,
        a_wins: int,
        b_wins: int,
        draws: int,
        total_games: int,
    ) -> float:
        """
        Calculates the Elo delta for player A from a single matchup.

        Uses win-rate normalization: delta = K * (actual_rate - expected_rate).
        Normalizing by ``total_games`` bounds the per-epoch delta to [-K, +K]
        regardless of batch size, preventing score explosion in large tournaments.
        The delta for player B is always -delta (zero-sum invariant).

        :param rating_a: Current Elo rating of player A.
        :param rating_b: Current Elo rating of player B.
        :param a_wins: Number of games won by player A.
        :param b_wins: Number of games won by player B.
        :param draws: Number of drawn games.
        :param total_games: Total number of games played (a_wins + b_wins + draws).
        :returns: Signed Elo delta for player A. Returns 0.0 if no games were played.
        """
        if total_games == 0:
            return 0.0

        expected_a = cls.expected_score(rating_a, rating_b)
        actual_rate_a = (a_wins + 0.5 * draws) / total_games
        return cls.K_FACTOR * (actual_rate_a - expected_a)

    @staticmethod
    def expected_score(rating_a: float, rating_b: float) -> float:
        """
        Calculates the expected score (win probability) for player A against player B.

        :param rating_a: Elo rating of player A.
        :param rating_b: Elo rating of player B.
        :returns: Expected score in range (0.0, 1.0).
        """
        return float(1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0)))
