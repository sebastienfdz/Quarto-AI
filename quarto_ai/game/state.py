from .piece import Piece, generate_all_pieces
from .board import Board
from .exceptions import InvalidPieceError, GameEndedError


class GameState:
    """Complete game state of a game of Quarto."""

    def __init__(self):
        self.board = Board()
        self.remaining_pieces: dict[int, Piece] = {p.to_bits(): p for p in generate_all_pieces()}
        self.current_player: int = 0            # 0 = Player 1 ; 1 = Player 2
        self.next_piece: Piece | None = None
        self.winner: int | None = None          # None -> ongoing ; -1 -> draw ; 0/1 -> winner

    def play_move(self, x: int, y: int, piece: Piece) -> None:
        """
        Place a piece on the board, and update the game state.
        
        :raises GameEndedError: If the game is already over.
        :raises InvalidePieceError: If the piece is unavailable.
        :raises InvalidSquareError: If the square is unavailable.
        """
        if self.winner is not None:
            raise GameEndedError("The game is already over.")
        if piece.to_bits() not in self.remaining_pieces:
            raise InvalidPieceError("Piece already played.")

        self.board.place_piece(x, y, piece)

        self.remaining_pieces.pop(piece.to_bits(), None)
        self._update_state()

    def _update_state(self):
        """Update game state after a move."""
        if self.board.check_victory():
            self.winner = self.current_player
        elif self.board.is_full():
            self.winner = -1
        else:
            self.current_player = 1 - self.current_player

    def get_available_positions(self):
        """Returns the list of available squares."""
        positions = []
        for i in range(4):
            for j in range(4):
                if self.board.game_board[i, j] is None:
                    positions.append((i, j))
        return positions

    def get_remaining_pieces_list(self):
        """Returns the list of available pieces."""
        return list(self.remaining_pieces.values())

    def get_remaining_pieces(self):
        """Returns the list of available pieces."""
        return self.remaining_pieces


    def __str__(self):
        """Simple display of the game state."""
        text = f"Current player: {self.current_player}\n"
        text += str(self.board)
        return text
