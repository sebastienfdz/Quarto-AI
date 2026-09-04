import pytest

from quarto_benchmark.game.piece import Piece
from quarto_benchmark.game.state import GameState
from quarto_benchmark.game.types import GameResult
from quarto_benchmark.players.ai.minimax.evaluator import SimpleEvaluator, evaluate_line


# Fixture Evaluator
@pytest.fixture
def new_game() -> GameState:
    """A fresh game in SELECTION phase, current player: PLAYER_1."""
    return GameState()


@pytest.fixture
def simple_evaluator() -> SimpleEvaluator:
    return SimpleEvaluator()


# Evaluate Line Tests
def test_evaluate_line_empty():
    """An empty line should return 0."""
    assert evaluate_line([None, None, None, None]) == 0


def test_evaluate_line_one_piece():
    """A line with one piece trivially shares all its attributes, returning 1."""
    assert evaluate_line([Piece(0, 0, 0, 0), None, None, None]) == 1


def test_evaluate_line_two_pieces_shared():
    """Two pieces sharing at least one attribute should return 2."""
    assert evaluate_line([Piece(0, 1, 1, 1), Piece(0, 0, 0, 0), None, None]) == 2
    assert evaluate_line([Piece(0, 1, 0, 0), Piece(1, 1, 1, 1), None, None]) == 2


def test_evaluate_line_two_pieces_not_shared():
    """Two pieces with no shared attributes should return 0 (dead line)."""
    assert evaluate_line([Piece(0, 0, 0, 0), Piece(1, 1, 1, 1), None, None]) == 0


def test_evaluate_line_three_pieces_shared():
    """Three pieces sharing at least one attribute should return 3."""
    line = [Piece(1, 0, 0, 0), Piece(1, 1, 1, 1), Piece(1, 1, 0, 0), None]
    assert evaluate_line(line) == 3


def test_evaluate_line_three_pieces_not_shared():
    """Three pieces where no single attribute is shared by ALL of them should return 0."""
    line = [Piece(0, 0, 0, 0), Piece(1, 1, 1, 1), Piece(1, 1, 0, 0), None]
    assert evaluate_line(line) == 0


def test_evaluate_line_four_pieces_shared():
    """Four pieces sharing an attribute constitutes a Quarto and should return 4."""
    line: list[Piece | None] = [
        Piece(0, 0, 0, 0),
        Piece(1, 0, 0, 0),
        Piece(0, 1, 0, 0),
        Piece(1, 1, 0, 0),
    ]
    assert evaluate_line(line) == 4


def test_evaluate_line_four_pieces_not_shared():
    """Four pieces with no shared attribute should return 0 (dead line)."""
    line: list[Piece | None] = [
        Piece(0, 0, 0, 0),
        Piece(0, 0, 1, 1),
        Piece(1, 1, 0, 0),
        Piece(1, 1, 1, 1),
    ]
    assert evaluate_line(line) == 0


# SimpleEvaluator Tests
def test_simple_evaluator_empty_board(new_game: GameState, simple_evaluator: SimpleEvaluator):
    """An empty board has no threats: score must be exactly 0.0."""
    assert simple_evaluator.evaluate(new_game) == 0.0


def test_simple_evaluator_terminal_win_p1(new_game: GameState, simple_evaluator: SimpleEvaluator):
    """PLAYER_1 win should return positive infinity."""
    new_game.result = GameResult.PLAYER_1
    assert simple_evaluator.evaluate(new_game) == float("inf")


def test_simple_evaluator_terminal_win_p2(new_game: GameState, simple_evaluator: SimpleEvaluator):
    """PLAYER_2 win should return negative infinity."""
    new_game.result = GameResult.PLAYER_2
    assert simple_evaluator.evaluate(new_game) == float("-inf")


def test_simple_evaluator_terminal_draw(new_game: GameState, simple_evaluator: SimpleEvaluator):
    """A draw should return 0.0."""
    new_game.result = GameResult.DRAW
    assert simple_evaluator.evaluate(new_game) == 0.0


def test_simple_evaluator_threat_placement_p1(
    new_game: GameState, simple_evaluator: SimpleEvaluator
):
    """
    If there is a threat and PLAYER_1 is about to place, it benefits PLAYER_1 (positive).
    """
    new_game.select_piece(new_game.remaining_pieces[0])  # P1 selects
    new_game.place_piece(0, 0)  # P2 places
    new_game.select_piece(new_game.remaining_pieces[2])  # P2 selects
    new_game.place_piece(0, 1)  # P1 places
    new_game.select_piece(new_game.remaining_pieces[4])  # P1 selects
    new_game.place_piece(0, 2)  # P2 places
    new_game.select_piece(new_game.remaining_pieces[6])  # P2 selects, P1 to place

    score = simple_evaluator.evaluate(new_game)
    assert score > 0


def test_simple_evaluator_threat_placement_p2(
    new_game: GameState, simple_evaluator: SimpleEvaluator
):
    """
    If there is a threat and PLAYER_2 is about to place, it benefits PLAYER_2 (negative).
    """
    new_game.select_piece(new_game.remaining_pieces[0])  # P1 selects
    new_game.place_piece(0, 0)  # P2 places
    new_game.select_piece(new_game.remaining_pieces[2])  # P2 selects
    new_game.place_piece(0, 1)  # P1 places
    new_game.select_piece(new_game.remaining_pieces[4])  # P1 selects, P2 to place

    score = simple_evaluator.evaluate(new_game)
    assert score < 0


def test_simple_evaluator_threat_selection_p1(
    new_game: GameState, simple_evaluator: SimpleEvaluator
):
    """
    If there is a threat and PLAYER_1 is selecting, PLAYER_2 will place. Score should be negative.
    """
    new_game.select_piece(new_game.remaining_pieces[0])  # P1 selects
    new_game.place_piece(0, 0)  # P2 places
    new_game.select_piece(new_game.remaining_pieces[2])  # P2 selects
    new_game.place_piece(0, 1)  # P1 places, P1 to select

    score = simple_evaluator.evaluate(new_game)
    assert score < 0
