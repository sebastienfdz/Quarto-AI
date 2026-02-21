import pytest
from quarto_ai.game.piece import Piece
from quarto_ai.game.state import GameState
from quarto_ai.players.human import HumanPlayer


@pytest.fixture
def new_game() -> GameState:
    """Create a new game of Quarto."""
    game = GameState()
    assert game.winner is None
    assert not game.board.is_full()
    assert not game.board.check_victory()
    return game


def test_choose_position_valid(new_game: GameState):
    inputs = iter(["0, 0"])
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=lambda _: None,
    )
    piece = Piece(0, 0, 0, 0)

    x, y = player.choose_position(new_game, piece)
    assert (x, y) == (0, 0)


def test_choose_position_retry(new_game: GameState):
    inputs = iter(["invalid position", "0, 0"])
    outputs = []
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=outputs.append,
    )
    piece = Piece(0, 0, 0, 0)

    x, y = player.choose_position(new_game, piece)
    assert (x, y) == (0, 0)
    assert any("Invalid format." in msg for msg in outputs)


def test_choose_position_invalid_square(new_game: GameState):
    inputs = iter(["0, 0", "1, 1"])
    outputs = []
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=outputs.append,
    )
    piece = Piece(0, 0, 0, 0)
    new_game.play_move(0, 0, piece)

    x, y = player.choose_position(new_game, piece)
    assert (x, y) == (1, 1)
    assert any("Position unavailable." in msg for msg in outputs)


def test_choose_piece_valid(new_game: GameState):
    inputs = iter(["0"])
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=lambda _: None,
    )

    piece = player.choose_piece(new_game)
    assert piece == Piece(0, 0, 0, 0)


def test_choose_piece_retry_value_error(new_game: GameState):
    inputs = iter(["invalid piece", "0"])
    outputs = []
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=outputs.append,
    )

    piece = player.choose_piece(new_game)
    assert piece == Piece(0, 0, 0, 0)
    assert any("Invalid input." in msg for msg in outputs)


def test_choose_piece_retry_key_error(new_game: GameState):
    inputs = iter(["-100", "0"])
    outputs = []
    player = HumanPlayer(
        input_func=lambda _: next(inputs),
        output_func=outputs.append,
    )

    piece = player.choose_piece(new_game)
    assert piece == Piece(0, 0, 0, 0)
    assert any("Invalid piece." in msg for msg in outputs)


def test_parse_position_valid():
    player = HumanPlayer()
    assert player._parse_position("0, 0") == (0, 0)


def test_parse_position_invalid():
    player = HumanPlayer()
    with pytest.raises(ValueError):
        player._parse_position("invalid raw input")
