import pytest

from quarto_ai.game.state import GameState
from quarto_ai.players.ai.minimax.evaluator import SimpleEvaluator
from quarto_ai.players.ai.minimax.minimax import Minimax


# Fixture GameState
@pytest.fixture
def new_game() -> GameState:
    """Create a new game of Quarto (Phase = SELECTION)"""
    game = GameState()
    return game


@pytest.fixture
def winning_game() -> GameState:
    """
    Create a new game of Quarto with a winning move (Phase = SELECTION).
    Adding the piece (0, 0, 0, 0) in the square (0, 0) is winning.
    """
    game = GameState()
    pieces = game.get_remaining_pieces()

    for x in range(1, 4):
        game.select_piece(pieces[x])
        game.place_piece(x, 0)

    assert game.result is None
    return game


# Fixture Minimax
@pytest.fixture
def minimax_player() -> Minimax:
    """A naive Minimax player with a simple evaluator."""
    evaluator = SimpleEvaluator()
    return Minimax(evaluator=evaluator, depth=2, use_alpha_beta=False)


def test_choose_piece_valid(new_game: GameState, minimax_player: Minimax):
    """The AI should select a valid available piece from the pool."""
    piece = minimax_player.choose_piece(new_game)
    assert piece in new_game.get_remaining_pieces()


def test_choose_piece_not_winning(winning_game: GameState, minimax_player: Minimax):
    """
    In a situation where the opponent could win, the AI
    must not choose the piece that completes the Quarto.
    """
    loosing_piece = winning_game.get_remaining_pieces()[0]
    chosen_piece = minimax_player.choose_piece(winning_game)
    assert chosen_piece != loosing_piece


def test_choose_position_valid(new_game: GameState, minimax_player: Minimax):
    """The AI should select an valid empty square on the board."""
    piece = new_game.get_remaining_pieces()[0]
    new_game.select_piece(piece)

    x, y = minimax_player.choose_position(new_game, piece)
    assert (x, y) in new_game.board.get_available_positions()


def test_choose_position_winning(winning_game: GameState, minimax_player: Minimax):
    """The AI must select the winning square when handed a winning piece."""
    winning_piece = winning_game.get_remaining_pieces()[0]
    winning_game.select_piece(winning_piece)

    x, y = minimax_player.choose_position(winning_game, winning_piece)
    assert (x, y) == (0, 0)
