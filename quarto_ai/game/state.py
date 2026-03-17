from .piece import Piece, generate_all_pieces
from .board import Board
from .types import Player, GamePhase, GameResult
from .exceptions import (
    InvalidPieceError,
    GameEndedError,
    InvalidPhaseError
)


class GameState:
    """Complete game state of a game of Quarto."""

    def __init__(self) -> None:
        self.board = Board()
        self.remaining_pieces: dict[int, Piece] = {p.to_bits(): p for p in generate_all_pieces()}
        self.current_player: Player = Player.PLAYER_1
        self.phase: GamePhase = GamePhase.SELECTION
        self.next_piece: Piece | None = None
        self.result: GameResult | None = None

    def _update_state(self) -> None:
        """Update game state after a turn."""
        if self.board.check_victory():
            self.result = GameResult(self.current_player.value)
        elif self.board.is_full():
            self.result = GameResult.DRAW

    def select_piece(self, piece: Piece) -> None:
        """
        Select a piece from the available ones.

        :raises GameEndedError: If the game is already over.
        :raises InvalidPhaseError: If it is the wrong game phase.
        :raises InvalidPieceError: If the piece is unavailable.
        """
        if self.result is not None:
            raise GameEndedError("The game is already over.")
        if self.phase != GamePhase.SELECTION:
            raise InvalidPhaseError("Invalid phase.")
        if self.next_piece is not None:
            raise InvalidPieceError("Next piece was already chosen.")
        if piece not in self.get_remaining_pieces_list():
            raise InvalidPieceError("Piece already played.")

        self.next_piece = piece
        self.remaining_pieces.pop(self.next_piece.to_bits(), None)

        self.current_player = self.current_player.opponent
        self.phase = self.phase.change_phase

    def place_piece(self, x: int, y: int) -> None:
        """
        Place the given piece on the board.

        :raises GameEndedError: If the game is already over.
        :raises InvalidPhaseError: If it is the wrong game phase.
        :raises InvalidPieceError: If the piece is unavailable.
        :raises InvalidSquareError: If the square is unavailable.
        """
        if self.result is not None:
            raise GameEndedError("The game is already over.")
        if self.phase != GamePhase.PLACEMENT:
            raise InvalidPhaseError("Invalid phase.")
        if self.next_piece is None:
            raise InvalidPieceError("No piece selected to be placed.")

        self.board.place_piece(x, y, self.next_piece)
        self.next_piece = None

        self.phase = self.phase.change_phase
        self._update_state()

    def get_available_positions(self) -> list[tuple[int, int]]:
        """Returns the list of available squares."""
        positions = []
        for i in range(4):
            for j in range(4):
                if self.board.game_board[i, j] is None:
                    positions.append((i, j))
        return positions

    def get_remaining_pieces_list(self) -> list[Piece]:
        """Returns the list of available pieces."""
        return list(self.remaining_pieces.values())

    def get_remaining_pieces(self) -> dict[int, Piece]:
        """Returns the list of available pieces."""
        return self.remaining_pieces


    def __str__(self) -> str:
        """Simple display of the game state."""
        text = f"Current player: {self.current_player}\n"
        text += f"Phase: {self.phase}\n"
        text += str(self.board)
        return text
