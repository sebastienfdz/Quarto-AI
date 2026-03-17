import pytest
from quarto_ai.game.piece import Piece
from quarto_ai.game.state import GameState
from quarto_ai.players.ai.random_ai import RandomAI


@pytest.fixture
def new_game() -> GameState:
    """Create a new game of Quarto."""
    game = GameState()
    return game


@pytest.fixture
def winning_game() -> GameState:
    """
    Create a new game of Quarto with a winning move.
    Adding the piece (0, 0, 0, 0) in the square (0, 0) is winning.
    """
    game = GameState()
    pieces = game.get_remaining_pieces()

    for x in range(1, 4):
        game.select_piece(pieces[x])
        game.place_piece(x, 0)

    assert game.result is None
    return game


def test_choose_piece_valid(new_game: GameState):
    """Return a piece that is still available in the game state."""
    player = RandomAI()
    piece = player.choose_piece(new_game)
    assert piece in new_game.get_remaining_pieces_list()


def test_choose_position_valid(new_game: GameState):
    """Return a valid and currently available board position."""
    player = RandomAI()
    piece = new_game.get_remaining_pieces_list()[0]
    new_game.select_piece(piece)
    x, y = player.choose_position(new_game, piece)
    assert (x, y) in new_game.get_available_positions()


def test_choose_position_winning(winning_game: GameState):
    """Select the winning move when one is immediately available."""
    player = RandomAI()
    piece = winning_game.get_remaining_pieces_list()[0]
    winning_game.select_piece(piece)

    x, y = player.choose_position(winning_game, piece)
    assert (x, y) == (0, 0)

    winning_game.place_piece(x, y)
    assert winning_game.result is not None
    assert winning_game.board.check_victory()


def test_is_winning_move_false(new_game: GameState):
    """Return False when placing the piece doesn't results in a victory."""
    player = RandomAI()
    piece = Piece(0, 0, 0, 0)
    is_winning = player._is_winning_move(new_game.board, 0, 0, piece)
    assert not is_winning


def test_is_winning_move_true(winning_game: GameState):
    """Return True when placing the piece results in a victory."""
    player = RandomAI()
    piece = Piece(0, 0, 0, 0)
    is_winning = player._is_winning_move(winning_game.board, 0, 0, piece)
    assert is_winning


def test_is_winning_move_unavailable(winning_game: GameState):
    """Return False when placing the piece is not possible."""
    player = RandomAI()
    piece = Piece(0, 0, 0, 0)
    is_winning = player._is_winning_move(winning_game.board, 1, 0, piece)
    assert not is_winning


def test_is_winning_move_not_modify_board(new_game: GameState):
    """Ensure the board state remains unchanged after simulating a move."""
    board = new_game.board
    player = RandomAI()
    piece = Piece(0, 0, 0, 0)
    is_winning = player._is_winning_move(new_game.board, 0, 0, piece)
    assert not is_winning
    assert board == new_game.board
