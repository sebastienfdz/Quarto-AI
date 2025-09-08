import numpy as np
from .piece import Piece
from .exceptions import InvalidSquareError


class Board:

    def __init__(self):
        self.game_board: np.ndarray = np.full(shape=(4, 4), fill_value=None, dtype=object)

    def place_piece(self, x: int, y: int, piece: Piece):
        """
        Places a piece on the board.

        :raises InvalidSquareError: If the square is unavailable.
        """
        if self.game_board[x, y] is not None:
            raise InvalidSquareError(f"Square ({x}, {y}) not available.")
        self.game_board[x, y] = piece

    def is_full(self) -> bool:
        """Checks if the board is full"""
        return all(cell is not None for row in self.game_board for cell in row)

    def get_lines(self) -> list[list[Piece | None]]:
        """Returns all rows, columns, and diagonals."""
        rows = [list(self.game_board[i, :]) for i in range(4)]
        cols = [list(self.game_board[:, j]) for j in range(4)]
        diags = [list(self.game_board.diagonal()), list(np.fliplr(self.game_board).diagonal())]
        return rows + cols + diags

    def has_quarto(self, line: list[Piece]) -> bool:
        """Checks if a line forms a Quarto (at least 1 common attribute)"""
        if any(p is None for p in line):
            return False

        for bit in range(4):
            values = [(p.to_bits() >> bit) & 1 for p in line]
            if all(v == values[0] for v in values):
                return True
        return False

    def check_victory(self) -> bool:
        """Returns True if a win condition is met, False otherwise"""
        return any(self.has_quarto(line) for line in self.get_lines())


    def __str__(self) -> str:
        """Simple display of the board."""
        rows = []
        for i in range(4):
            row = []
            for j in range(4):
                piece = self.game_board[i, j]
                row.append(str(piece) if piece else " . ")
            rows.append(" | ".join(row))
        return "\n".join(rows)
