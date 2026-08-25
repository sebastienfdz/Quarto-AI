import pytest

from quarto_ai.players.ai.random_ai import RandomAI
from quarto_ai.runners.tournament_runner import TournamentRunner


@pytest.fixture
def runner() -> TournamentRunner:
    """Fixture for TournamentRunner instance."""
    return TournamentRunner()


@pytest.fixture
def player_a() -> RandomAI:
    """Fixture for first RandomAI player."""
    return RandomAI("AI-A")


@pytest.fixture
def player_b() -> RandomAI:
    """Fixture for second RandomAI player."""
    return RandomAI("AI-B")


@pytest.mark.parametrize("parallel", [True, False])
def test_run_matchup_success(
    runner: TournamentRunner, player_a: RandomAI, player_b: RandomAI, parallel: bool
) -> None:
    """Verify that a matchup runs the correct number of games and aggregates stats."""
    games_per_side = 2
    results = runner.run_matchup(player_a, player_b, games_per_side, parallel=parallel)

    assert results["player_a_name"] == "AI-A"
    assert results["player_b_name"] == "AI-B"
    assert results["games_per_side"] == games_per_side
    assert results["total_games"] == games_per_side * 2

    total_outcomes = results["a_wins"] + results["b_wins"] + results["draws"]
    assert total_outcomes == results["total_games"]

    total_bias_outcomes = results["starter_wins"] + results["follower_wins"] + results["draws"]
    assert total_bias_outcomes == results["total_games"]


def test_run_matchup_invalid_inputs(
    runner: TournamentRunner, player_a: RandomAI, player_b: RandomAI
) -> None:
    """Verify that invalid games_per_side input raises a ValueError."""
    with pytest.raises(ValueError, match="games_per_side must be at least 1"):
        runner.run_matchup(player_a, player_b, 0)


@pytest.mark.parametrize("parallel", [True, False])
def test_run_championship_success(
    runner: TournamentRunner, player_a: RandomAI, player_b: RandomAI, parallel: bool
) -> None:
    """Verify that a championship runs matches between all pairs and sorts the leaderboard."""
    player_c = RandomAI("AI-3")
    players = [player_a, player_b, player_c]
    games_per_matchup = 3

    leaderboard = runner.run_championship(players, games_per_matchup, parallel=parallel)

    assert len(leaderboard) == 3
    for entry in leaderboard:
        assert entry["total_games"] == 12

    for i in range(len(leaderboard) - 1):
        current_entry, next_entry = leaderboard[i], leaderboard[i + 1]

        assert current_entry["elo"] >= next_entry["elo"]
        if current_entry["elo"] == next_entry["elo"]:
            assert current_entry["points"] >= next_entry["points"]
            if current_entry["points"] == next_entry["points"]:
                assert current_entry["wins"] >= next_entry["wins"]


def test_run_championship_invalid_inputs(runner: TournamentRunner, player_a: RandomAI) -> None:
    """Verify that championship with less than 2 players raises a ValueError."""
    with pytest.raises(ValueError, match="Championship requires at least 2 players"):
        runner.run_championship([player_a], 1)
