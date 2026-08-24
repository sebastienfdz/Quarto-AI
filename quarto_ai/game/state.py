from .board import Board
from .exceptions import GameEndedError, InvalidPhaseError, InvalidPieceError
from .piece import Piece, generate_all_pieces
from .types import GamePhase, GameResult, Player

MoveType = tuple[int, int] | Piece | None


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
        if piece not in self.get_remaining_pieces():
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

    def get_remaining_pieces(self) -> list[Piece]:
        """Returns the list of available pieces."""
        return list(self.remaining_pieces.values())

    def clone(self) -> "GameState":
        """
        Creates a fast copy of the game state for tree search algorithms.

        Bypasses the overhead of copy.deepcopy() by manually duplicating only
        the mutable containers.
        """
        new_state = GameState.__new__(GameState)

        new_state.board = Board.__new__(Board)
        new_state.board.game_board = self.board.game_board.copy()

        new_state.remaining_pieces = self.remaining_pieces.copy()
        new_state.current_player = self.current_player
        new_state.phase = self.phase
        new_state.next_piece = self.next_piece
        new_state.result = self.result

        return new_state

    def get_legal_moves(self) -> list[MoveType]:
        """Find every legal moves from a game state position."""
        moves: list[MoveType] = []

        if self.phase == GamePhase.PLACEMENT:
            moves = list(self.board.get_available_positions())
        elif self.phase == GamePhase.SELECTION:
            moves = list(self.get_remaining_pieces())
        return moves

    def apply_move(self, move: MoveType) -> None:
        """
        Apply a single move to the given game state.

        :param move: Move to apply to the current game state.
        """
        if self.phase == GamePhase.PLACEMENT:
            if not isinstance(move, tuple):
                raise TypeError(f"Expected tuple for placement, got {type(move).__name__}")
            self.place_piece(move[0], move[1])
        elif self.phase == GamePhase.SELECTION:
            if not isinstance(move, Piece):
                raise TypeError(f"Expected Piece for selection, got {type(move).__name__}")
            self.select_piece(move)

    def __str__(self) -> str:
        """Simple display of the game state."""
        text = f"Current player: {self.current_player}\n"
        text += f"Phase: {self.phase}\n"
        text += str(self.board)
        return text
