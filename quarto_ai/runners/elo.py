class EloSystem:
    """
    Computes Elo ratings for players.
    Acts as a pure math utility, taking raw scores and returning new ratings.
    """

    K_FACTOR: float = 32.0
    INITIAL_RATING: float = 1500.0

    @classmethod
    def calculate_new_ratings(
        cls, rating_a: float, rating_b: float, a_wins: int, b_wins: int, draws: int
    ) -> tuple[float, float]:
        """
        Calculates the new Elo ratings for two players based on a set of games.

        :returns: A tuple of (new_rating_a, new_rating_b)
        """
        n_games = a_wins + b_wins + draws
        if n_games == 0:
            return rating_a, rating_b

        # Expected score total for the matchup
        expected_a = cls.expected_score(rating_a, rating_b) * n_games
        expected_b = n_games - expected_a

        # Actual score total for the matchup
        actual_a = a_wins + (0.5 * draws)
        actual_b = b_wins + (0.5 * draws)

        # New ratings
        new_rating_a = rating_a + cls.K_FACTOR * (actual_a - expected_a)
        new_rating_b = rating_b + cls.K_FACTOR * (actual_b - expected_b)

        return new_rating_a, new_rating_b

    @staticmethod
    def expected_score(rating_a: float, rating_b: float) -> float:
        """Calculates the expected score (win probability) for player A against player B."""
        return float(1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0)))
