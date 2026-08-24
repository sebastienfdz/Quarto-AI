import pytest

from quarto_ai.runners.elo import EloSystem


def test_expected_score_equal_rating():
    """Equal ratings should yield exactly 0.5 expected score."""
    assert EloSystem.expected_score(1500.0, 1500.0) == 0.5


def test_expected_score_symmetry():
    """The sum of expected scores for both players should always be 1.0."""
    e_a = EloSystem.expected_score(1600.0, 1400.0)
    e_b = EloSystem.expected_score(1400.0, 1600.0)
    assert e_a + e_b == pytest.approx(1.0)


def test_expected_score_difference():
    """A 400 point difference means a 10:1 odds ratio, so expected score is ~0.909."""
    e_a = EloSystem.expected_score(1900.0, 1500.0)
    assert e_a == pytest.approx(10 / 11, rel=1e-5)


def test_calculate_new_ratings_single_win():
    """A single win against an equally rated opponent awards K/2 points."""
    new_a, new_b = EloSystem.calculate_new_ratings(
        rating_a=1500.0, rating_b=1500.0, a_wins=1, b_wins=0, draws=0
    )

    assert new_a == EloSystem.INITIAL_RATING + EloSystem.K_FACTOR / 2
    assert new_b == EloSystem.INITIAL_RATING - EloSystem.K_FACTOR / 2


def test_calculate_new_ratings_batch_draws():
    """Batch of 10 draws against equal opponent leaves ratings unchanged."""
    new_a, new_b = EloSystem.calculate_new_ratings(
        rating_a=1500.0, rating_b=1500.0, a_wins=0, b_wins=0, draws=10
    )

    assert new_a == 1500.0
    assert new_b == 1500.0


def test_calculate_new_ratings_zero_sum():
    """The total number of rating points in the system should remain constant."""
    rating_a = 1600.0
    rating_b = 1400.0

    new_a, new_b = EloSystem.calculate_new_ratings(
        rating_a=rating_a, rating_b=rating_b, a_wins=8, b_wins=2, draws=0
    )

    initial_sum = rating_a + rating_b
    final_sum = new_a + new_b

    assert initial_sum == pytest.approx(final_sum, rel=1e-5)


def test_calculate_new_ratings_zero_games():
    """Zero games played should return the exact same ratings without doing any math."""
    new_a, new_b = EloSystem.calculate_new_ratings(
        rating_a=1500.0, rating_b=1600.0, a_wins=0, b_wins=0, draws=0
    )

    assert new_a == 1500.0
    assert new_b == 1600.0
