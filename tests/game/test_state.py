import re

import pytest

from quarto_ai.game.exceptions import (
    GameEndedError,
    InvalidPhaseError,
    InvalidPieceError,
    InvalidSquareError,
)
from quarto_ai.game.piece import Piece
from quarto_ai.game.state import GameState
from quarto_ai.game.types import GamePhase, GameResult, Player


@pytest.fixture
def new_game() -> GameState:
    """Create a new game of Quarto."""
    game = GameState()
    assert game.result is None
    assert not game.board.is_full()
    assert not game.board.check_victory()
    assert game.current_player == Player.PLAYER_1
    assert game.phase == GamePhase.SELECTION
    return game


@pytest.fixture
def game_draw() -> GameState:
    """Create a draw game of Quarto."""
    ordered_pieces = [
        [0, 2, 1, 15],
        [5, 4, 3, 12],
        [10, 13, 11, 7],
        [14, 8, 6, 9],
    ]
    game = GameState()
    pieces = game.get_remaining_pieces()

    for x in range(4):
        for y in range(4):
            piece = pieces[ordered_pieces[x][y]]
            game.select_piece(piece)
            game.place_piece(x, y)

    assert game.result == GameResult.DRAW
    assert game.board.is_full()
    assert not game.board.check_victory()
    return game


def test_initial_state(new_game: GameState):
    """At the beginning, Player 1 must select a piece for Player 2."""
    assert new_game.current_player == Player.PLAYER_1
    assert new_game.phase == GamePhase.SELECTION
    assert new_game.next_piece is None


def test_standard_turn_flow(new_game: GameState):
    """Test the state machine transitions (Selection -> Placement -> Selection)."""
    # Action 1: Player 1 selects a piece
    piece = new_game.get_remaining_pieces()[0]
    new_game.select_piece(piece)
    assert new_game.current_player == Player.PLAYER_2
    assert new_game.phase == GamePhase.PLACEMENT
    assert new_game.next_piece == piece

    # Action 2: Player 2 places the piece
    new_game.place_piece(0, 0)
    assert new_game.current_player == Player.PLAYER_2
    assert new_game.phase == GamePhase.SELECTION  # type: ignore[comparison-overlap]

    # Action 3: Player 2 selects the next piece
    piece = new_game.get_remaining_pieces()[0]
    new_game.select_piece(piece)
    assert new_game.current_player == Player.PLAYER_1
    assert new_game.phase == GamePhase.PLACEMENT
    assert new_game.next_piece == piece


def test_game_victory(new_game: GameState):
    """Create a game of Quarto with a winner."""
    pieces = new_game.get_remaining_pieces()
    for i in range(4):
        new_game.select_piece(pieces[i])
        new_game.place_piece(i, 0)

    assert new_game.result in (GameResult.PLAYER_1, GameResult.PLAYER_2)
    assert not new_game.board.is_full()
    assert new_game.board.check_victory()


def test_select_piece_invalid_phase_raises(new_game: GameState):
    """Calling select_piece during PLACEMENT phase should raise InvalidPhaseError."""
    assert new_game.phase == GamePhase.SELECTION
    piece = new_game.get_remaining_pieces()[0]
    new_game.select_piece(piece)
    assert new_game.phase == GamePhase.PLACEMENT  # type: ignore[comparison-overlap]

    with pytest.raises(InvalidPhaseError, match="Invalid phase."):
        new_game.select_piece(new_game.get_remaining_pieces()[0])


def test_place_piece_invalid_phase_raises(new_game: GameState):
    """Calling place_piece during SELECTION phase should raise InvalidPhaseError."""
    assert new_game.phase == GamePhase.SELECTION
    with pytest.raises(InvalidPhaseError, match="Invalid phase."):
        new_game.place_piece(0, 0)


def test_select_piece_game_ended_raises(game_draw: GameState):
    """Playing after the game ended should raise GameEndedError."""
    with pytest.raises(GameEndedError, match="The game is already over."):
        game_draw.select_piece(Piece(0, 0, 0, 0))


def test_place_piece_game_ended_raises(game_draw: GameState):
    """Playing after the game ended should raise GameEndedError."""
    with pytest.raises(GameEndedError, match="The game is already over."):
        game_draw.place_piece(0, 0)


def test_select_piece_invalid_piece_raises(new_game: GameState):
    """Selecting an already used piece should raise InvalidPieceError."""
    piece = new_game.get_remaining_pieces()[0]
    new_game.select_piece(piece)
    new_game.place_piece(0, 0)

    with pytest.raises(InvalidPieceError, match="Piece already played."):
        new_game.select_piece(piece)


def test_place_piece_invalid_square_raises(new_game: GameState):
    """Playing on an occupied square should raise InvalidSquareError."""
    pieces = new_game.get_remaining_pieces()
    new_game.select_piece(pieces[0])
    new_game.place_piece(0, 0)

    new_game.select_piece(pieces[1])
    with pytest.raises(InvalidSquareError, match=r"Square .* not available"):
        new_game.place_piece(0, 0)


def test_play_move_winning(new_game: GameState):
    """
    Playing a winning move should make a victory,
    trying to play again should raise GameEndedError.
    """
    pieces = new_game.get_remaining_pieces()
    for i in range(4):
        new_game.select_piece(pieces[i])
        new_game.place_piece(0, i)

    assert new_game.board.check_victory()

    with pytest.raises(GameEndedError, match="The game is already over."):
        new_game.select_piece(pieces[-1])


def test_get_available_positions_empty(new_game: GameState):
    """A new game should have 16 unique available positions."""
    pos = new_game.board.get_available_positions()
    assert len(pos) == 16
    assert len(pos) == len(set(pos))


def test_get_available_positions_full(game_draw: GameState):
    """A full game should have no available positions."""
    assert len(game_draw.board.get_available_positions()) == 0


def test_get_available_positions_one_move(new_game: GameState):
    """After one placement, 15 available positions should remain."""
    piece = new_game.get_remaining_pieces()[0]
    new_game.select_piece(piece)
    new_game.place_piece(0, 0)
    assert len(new_game.board.get_available_positions()) == 15


def test_get_remaining_pieces_new_game(new_game: GameState):
    """A new game should have 16 unique remaining pieces."""
    pieces = new_game.get_remaining_pieces()
    assert len(pieces) == 16
    assert len(pieces) == len(set(pieces))


def test_get_remaining_pieces_one_selection(new_game: GameState):
    """After one selection, 15 available pieces should remain."""
    piece = new_game.get_remaining_pieces()[0]
    new_game.select_piece(piece)
    assert len(new_game.get_remaining_pieces()) == 15


def test_get_remaining_pieces_full(game_draw: GameState):
    """A full game should have no remaining pieces."""
    assert len(game_draw.get_remaining_pieces()) == 0


def test_new_game_to_str(new_game: GameState):
    """The string representation of a new game should match the expected layout."""
    printed_game = (
        f"Current player: {Player.PLAYER_1}\n"
        f"Phase: {GamePhase.SELECTION}\n"
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
    assert len(lines) >= 6

    printed_player = lines.pop(0)
    assert printed_player.startswith("Current player: ")
    printed_phase = lines.pop(0)
    assert printed_phase.startswith("Phase: ")
    for line in lines:
        assert regex.match(line) is not None
