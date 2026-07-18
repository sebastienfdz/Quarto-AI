import pytest

from quarto_ai.game.piece import Piece
from quarto_ai.game.state import GameState
from quarto_ai.players.human import HumanPlayer


@pytest.fixture
def new_game() -> GameState:
    """Create a new game of Quarto."""
    game = GameState()
    return game


def test_choose_position_valid(new_game: GameState):
    """Returns the correct coordinates when the user provides a valid position."""
    inputs = iter(["0, 0"])
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=lambda _: None,
    )
    piece = new_game.get_remaining_pieces_list()[0]
    new_game.select_piece(piece)

    x, y = player.choose_position(new_game, piece)
    assert (x, y) == (0, 0)


def test_choose_position_retry(new_game: GameState):
    """Retry after invalid format input and eventually return a valid position."""
    inputs = iter(["invalid position", "0, 0"])
    outputs: list[str] = []
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=outputs.append,
    )
    piece = new_game.get_remaining_pieces_list()[0]
    new_game.select_piece(piece)

    x, y = player.choose_position(new_game, piece)
    assert (x, y) == (0, 0)
    assert any("Invalid format." in msg for msg in outputs)


def test_choose_position_unavailable_square(new_game: GameState):
    """Retry when the chosen position is already occupied."""
    inputs = iter(["0, 0", "1, 1"])
    outputs: list[str] = []
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=outputs.append,
    )

    piece = new_game.get_remaining_pieces_list()[0]
    new_game.select_piece(piece)
    new_game.place_piece(0, 0)
    piece = new_game.get_remaining_pieces_list()[0]
    new_game.select_piece(piece)

    # The player tries squares "0, 0" (occupied), then "1, 1" (available)
    x, y = player.choose_position(new_game, piece)
    assert (x, y) == (1, 1)
    assert any("Position unavailable." in msg for msg in outputs)


def test_choose_piece_valid(new_game: GameState):
    """Return the correct piece when the user selects a valid piece ID."""
    inputs = iter(["0"])
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=lambda _: None,
    )

    piece = player.choose_piece(new_game)
    assert piece == Piece(0, 0, 0, 0)


def test_choose_piece_retry_value_error(new_game: GameState):
    """Retry when the user enters a non-integer piece ID."""
    inputs = iter(["invalid piece", "0"])
    outputs: list[str] = []
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=outputs.append,
    )

    piece = player.choose_piece(new_game)
    assert piece == Piece(0, 0, 0, 0)
    assert any("Invalid input." in msg for msg in outputs)


def test_choose_piece_retry_key_error(new_game: GameState):
    """Retry when the user selects a piece that is not available."""
    inputs = iter(["-100", "0"])
    outputs: list[str] = []
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=outputs.append,
    )

    piece = player.choose_piece(new_game)
    assert piece == Piece(0, 0, 0, 0)
    assert any("Invalid piece." in msg for msg in outputs)


def test_parse_position_valid():
    """Correctly parse a well-formatted 'row,col' input string."""
    player = HumanPlayer()
    assert player._parse_position("0, 0") == (0, 0)


def test_parse_position_invalid():
    """Raise ValueError when the input format is invalid."""
    player = HumanPlayer()
    with pytest.raises(ValueError):
        player._parse_position("invalid raw input")
