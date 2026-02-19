import re
import pytest
from quarto_ai.game.board import Board
from quarto_ai.game.piece import Piece, generate_all_pieces
from quarto_ai.game.exceptions import InvalidSquareError


@pytest.fixture
def empty_board() -> Board:
    """Create a new empty Quarto board."""
    board = Board()
    return board


@pytest.fixture
def full_board() -> Board:
    """Create a board fully filled with valid pieces."""
    board = Board()
    pieces = generate_all_pieces()
    for x in range(4):
        for y in range(4):
            board.place_piece(x, y, pieces.pop())
    return board



def test_place_piece_valid(empty_board: Board):
    """A piece can be placed on an empty square."""
    piece = Piece(0, 0, 0, 0)
    empty_board.place_piece(0, 0, piece)


def test_place_piece_invalid_square_raises(empty_board: Board):
    """Placing a piece on an occupied square raises an error."""
    piece = Piece(0, 0, 0, 0)
    piece2 = Piece(1, 0, 1, 0)
    empty_board.place_piece(0, 0, piece)

    with pytest.raises(InvalidSquareError, match=r".* not available"):
        empty_board.place_piece(0, 0, piece2)


def test_is_full_false(empty_board: Board):
    """An empty board is not full."""
    assert not empty_board.is_full()


def test_is_full_true(full_board: Board):
    """A fully filled board is reported as full."""
    assert full_board.is_full()


def test_get_lines(full_board: Board):
    """The board returns all rows(4), columns(4) and diagonals(2)."""
    lines = full_board.get_lines()
    assert len(lines) == 10


def test_has_quarto_false(empty_board: Board):
    """A line containing an empty square cannot form a Quarto."""
    lines = empty_board.get_lines()
    assert not empty_board.has_quarto(lines[0])


def test_has_quarto_true(full_board: Board):
    """A full line with shared attributes forms a Quarto."""
    lines = full_board.get_lines()
    assert full_board.has_quarto(lines[0])


def test_check_victory_false(empty_board: Board):
    """An empty board does not trigger a victory."""
    assert not empty_board.check_victory()


def test_check_victory_true(full_board: Board):
    """A board with a full line sharing attributes forms a Quarto and a victory."""
    assert full_board.check_victory()


def test_empty_board_to_str(empty_board: Board):
    """The string representation of an empty board should match the expected layout."""
    printed_board = (
        ".. | .. | .. | ..\n"
        ".. | .. | .. | ..\n"
        ".. | .. | .. | ..\n"
        ".. | .. | .. | .."
    )
    assert str(empty_board) == printed_board


def test_full_board_to_str(full_board: Board):
    """The string representation of a full board should match the expected structure."""
    regex = re.compile(r"\d\d \| \d\d \| \d\d \| \d\d")
    lines = str(full_board).splitlines()
    assert len(lines) == 4
    for l in lines:
        assert regex.match(l) is not None
