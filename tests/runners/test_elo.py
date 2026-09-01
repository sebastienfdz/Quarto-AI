import pytest

from quarto_ai.runners.elo import EloMatchupResult, EloSystem


@pytest.fixture
def standard_matchups() -> list[EloMatchupResult]:
    """Standard 3-player round-robin tournament matchup results."""
    return [
        {
            "player_a_name": "A",
            "player_b_name": "B",
            "a_wins": 60,
            "b_wins": 30,
            "draws": 10,
            "total_games": 100,
        },
        {
            "player_a_name": "B",
            "player_b_name": "C",
            "a_wins": 40,
            "b_wins": 50,
            "draws": 10,
            "total_games": 100,
        },
        {
            "player_a_name": "A",
            "player_b_name": "C",
            "a_wins": 70,
            "b_wins": 20,
            "draws": 10,
            "total_games": 100,
        },
    ]


def test_expected_score_equal_rating() -> None:
    """Equal ratings should yield exactly 0.5 expected score."""
    assert EloSystem.expected_score(1500.0, 1500.0) == 0.5


def test_expected_score_symmetry() -> None:
    """The sum of expected scores for both players should always be 1.0."""
    e_a = EloSystem.expected_score(1600.0, 1400.0)
    e_b = EloSystem.expected_score(1400.0, 1600.0)
    assert e_a + e_b == pytest.approx(1.0)


def test_expected_score_difference() -> None:
    """A 400 point difference means a 10:1 odds ratio, so expected score is ~0.909."""
    e_a = EloSystem.expected_score(1900.0, 1500.0)
    assert e_a == pytest.approx(10 / 11, rel=1e-5)


def test_calculate_matchup_delta_equal_win() -> None:
    """Single win against an equal opponent gives K/2 delta."""
    delta = EloSystem._calculate_matchup_delta(
        1500.0, 1500.0, a_wins=1, b_wins=0, draws=0, total_games=1
    )
    assert delta == EloSystem.K_FACTOR / 2


def test_calculate_matchup_delta_equal_draws() -> None:
    """Pure draws against an equal opponent leave the delta at zero."""
    delta = EloSystem._calculate_matchup_delta(
        1500.0, 1500.0, a_wins=0, b_wins=0, draws=5, total_games=5
    )
    assert delta == 0.0


def test_calculate_matchup_delta_zero_games() -> None:
    """Zero games played yields a delta of 0.0 (no division by zero)."""
    delta = EloSystem._calculate_matchup_delta(
        1500.0, 1500.0, a_wins=0, b_wins=0, draws=0, total_games=0
    )
    assert delta == 0.0


def test_calculate_matchup_delta_bounded_by_k() -> None:
    """Win-rate normalization must bound the delta to [-K, +K] regardless of game volume."""
    delta_small = EloSystem._calculate_matchup_delta(
        1500.0, 1500.0, a_wins=10, b_wins=0, draws=0, total_games=10
    )
    delta_large = EloSystem._calculate_matchup_delta(
        1500.0, 1500.0, a_wins=200, b_wins=0, draws=0, total_games=200
    )
    assert delta_small == delta_large
    assert abs(delta_small) <= EloSystem.K_FACTOR


def test_calculate_ratings_convergence() -> None:
    """After a decisive tournament, the stronger player must rank above the initial rating."""
    matchups: list[EloMatchupResult] = [
        {
            "player_a_name": "Strong",
            "player_b_name": "Weak",
            "a_wins": 90,
            "b_wins": 10,
            "draws": 0,
            "total_games": 100,
        },
    ]
    ratings = EloSystem.calculate_ratings(matchups)
    assert ratings["Strong"] > EloSystem.INITIAL_RATING
    assert ratings["Weak"] < EloSystem.INITIAL_RATING


def test_calculate_ratings_zero_sum(
    standard_matchups: list[EloMatchupResult],
) -> None:
    """The total Elo in the system must be conserved (zero-sum property)."""
    ratings = EloSystem.calculate_ratings(standard_matchups)
    expected_total = 3 * EloSystem.INITIAL_RATING
    assert sum(ratings.values()) == pytest.approx(expected_total, rel=1e-5)


def test_calculate_ratings_order_invariance(
    standard_matchups: list[EloMatchupResult],
) -> None:
    """Elo ratings must be identical regardless of the order matchups are provided."""
    reversed_matchups = list(reversed(standard_matchups))

    ratings_forward = EloSystem.calculate_ratings(standard_matchups)
    ratings_reversed = EloSystem.calculate_ratings(reversed_matchups)

    for name in ["A", "B", "C"]:
        assert ratings_forward[name] == pytest.approx(ratings_reversed[name], abs=1e-7)


def test_calculate_ratings_cyclic_dominance() -> None:
    """Symmetric cyclic dominance (A > B > C > A) must converge to equal ratings of 1500."""
    matchups: list[EloMatchupResult] = [
        {
            "player_a_name": "A",
            "player_b_name": "B",
            "a_wins": 10,
            "b_wins": 0,
            "draws": 0,
            "total_games": 10,
        },
        {
            "player_a_name": "B",
            "player_b_name": "C",
            "a_wins": 10,
            "b_wins": 0,
            "draws": 0,
            "total_games": 10,
        },
        {
            "player_a_name": "C",
            "player_b_name": "A",
            "a_wins": 10,
            "b_wins": 0,
            "draws": 0,
            "total_games": 10,
        },
    ]
    ratings = EloSystem.calculate_ratings(matchups)
    for player_name in ["A", "B", "C"]:
        assert ratings[player_name] == pytest.approx(1500.0, abs=1e-3)
