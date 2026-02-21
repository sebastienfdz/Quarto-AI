import re
import pytest
from quarto_ai.game.piece import Piece
from quarto_ai.game.state import GameState
from quarto_ai.game.exceptions import GameEndedError, InvalidSquareError, InvalidPieceError


@pytest.fixture
def new_game() -> GameState:
    """Create a new game of Quarto."""
    game = GameState()
    assert game.winner is None
    assert not game.board.is_full()
    assert not game.board.check_victory()
    return game


@pytest.fixture
def game_draw() -> GameState:
    """Create a draw game of Quarto."""
    ordered_pieces = [
        [ 0,  2,  1, 15],
        [ 5,  4,  3, 12],
        [10, 13, 11,  7],
        [14,  8,  6,  9]
    ]
    game = GameState()
    remaining = game.get_remaining_pieces()

    for x in range(4):
        for y in range(4):
            piece = remaining[ordered_pieces[x][y]]
            game.play_move(x, y, piece)

    assert game.winner == -1
    assert game.board.is_full()
    assert not game.board.check_victory()
    return game


def test_game_victory():
    """Create a game of Quarto with a winner."""
    game = GameState()
    remaining = game.get_remaining_pieces()
    for x in range(4):
        game.play_move(x, 0, remaining[x])

    assert game.winner >= 0
    assert not game.board.is_full()
    assert game.board.check_victory()


def test_play_move_valid(new_game: GameState):
    """Playing a valid move should switch the current player."""
    remaining = new_game.get_remaining_pieces()
    assert new_game.current_player == 0
    new_game.play_move(0, 0, remaining[0])
    assert new_game.current_player == 1
    new_game.play_move(1, 1, remaining[1])
    assert new_game.current_player == 0
    assert len(new_game.get_remaining_pieces()) == 14


def test_play_move_game_ended_raises(game_draw: GameState):
    """Playing after the game ended should raise GameEndedError."""
    piece = Piece(0, 0, 0, 0)

    with pytest.raises(GameEndedError, match="The game is already over."):
        game_draw.play_move(0, 0, piece)


def test_play_move_invalid_piece_raises(new_game: GameState):
    """Replaying an already used piece should raise InvalidPieceError."""
    piece = Piece(0, 0, 0, 0)
    new_game.play_move(0, 0, piece)

    with pytest.raises(InvalidPieceError, match="Piece already played."):
        new_game.play_move(1, 1, piece)


def test_play_move_invalid_square_raises(new_game: GameState):
    """Playing on an occupied square should raise InvalidSquareError."""
    remaining = new_game.get_remaining_pieces()
    new_game.play_move(0, 0, remaining[0])

    with pytest.raises(InvalidSquareError, match=r"Square .* not available"):
        new_game.play_move(0, 0, remaining[1])


def test_play_move_wining(new_game: GameState):
    """
    Playing a winning move should make a victory,
    trying to play again should raise GameEndedError.
    """
    remaining = new_game.get_remaining_pieces()
    for x in range(4):
        new_game.play_move(x, 0, remaining[x])

    assert new_game.winner >= 0
    assert not new_game.board.is_full()
    assert new_game.board.check_victory()

    with pytest.raises(GameEndedError, match="The game is already over."):
        new_game.play_move(3, 3, remaining[5])


def test_get_available_positions_empty(new_game: GameState):
    """A new game should have 16 unique available positions."""
    pos = new_game.get_available_positions()
    assert len(pos) == 16
    assert len(pos) == len(set(pos))


def test_get_available_positions_full(game_draw: GameState):
    """A full game should have no available positions."""
    pos = game_draw.get_available_positions()
    assert len(pos) == 0


def test_get_available_positions_one_move(new_game: GameState):
    """After one move, 15 available positions should remain."""
    remaining = new_game.get_remaining_pieces()
    new_game.play_move(0, 0, remaining[0])
    pos = new_game.get_available_positions()
    assert len(pos) == 15


def test_get_remaining_pieces_list_new_game(new_game: GameState):
    """A new game should have 16 unique remaining pieces."""
    pieces = new_game.get_remaining_pieces_list()
    assert len(pieces) == 16
    assert len(pieces) == len(set(pieces))


def test_get_remaining_pieces_new_game(new_game: GameState):
    """A new game should have 16 unique remaining pieces."""
    pieces = new_game.get_remaining_pieces()
    assert len(pieces) == 16
    assert len(pieces) == len(set(pieces))


def test_get_remaining_pieces_one_move(new_game: GameState):
    """After one move, 15 available pieces should remain."""
    piece = Piece(0, 0, 0, 0)
    new_game.play_move(0, 0, piece)
    assert len(new_game.get_remaining_pieces()) == 15


def test_get_remaining_pieces_full(game_draw: GameState):
    """A full game should have no remaining pieces."""
    assert len(game_draw.get_remaining_pieces()) == 0


def test_new_game_to_str(new_game: GameState):
    """The string representation of a new game should match the expected layout."""
    printed_game = (
        "Current player: 0\n"
        ".. | .. | .. | ..\n"
        ".. | .. | .. | ..\n"
        ".. | .. | .. | ..\n"
        ".. | .. | .. | .."
    )
    assert str(new_game) == printed_game


def test_full_board_to_str(game_draw: GameState):
    """The string representation of a full game should match the expected structure."""
    regex = re.compile(r"\d\d \| \d\d \| \d\d \| \d\d")
    lines = str(game_draw).splitlines()
    assert len(lines) == 5

    printed_player = lines.pop(0)
    assert printed_player.startswith("Current player: ")
    for l in lines:
        assert regex.match(l) is not None
