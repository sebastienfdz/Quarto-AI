from collections.abc import Callable

from quarto_ai.game.piece import Piece
from quarto_ai.game.state import GameState
from quarto_ai.players.base import BaseModel


class HumanPlayer(BaseModel):
    """
    A human-controlled player using CLI input.

    :param input_func: Function used to get user input.
    :param output_func: Function used to display output.
    """

    def __init__(
        self,
        name: str = "Human",
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
    ) -> None:
        super().__init__(name)
        self.input_func = input_func
        self.output_func = output_func

    def choose_position(self, state: GameState, piece: Piece) -> tuple[int, int]:
        """Ask the user for a valid position (row, col)."""
        prompt = f"Place piece {piece.to_bits():02d} (format: row,col): "

        while True:
            raw = self.input_func(prompt)
            try:
                x, y = self._parse_position(raw)
                if (x, y) in state.board.get_available_positions():
                    return x, y
                self.output_func("❌ Position unavailable. Try again.")
            except ValueError:
                self.output_func("⚠️ Invalid format. Use format 'row,col' (e.g.: 0,3).")

    def choose_piece(self, state: GameState) -> Piece:
        """Ask the user to select a piece for the opponent."""
        remaining = state.remaining_pieces

        self.output_func("Available pieces:")
        self.output_func(" ".join(f"{piece_id:02d}" for piece_id in remaining.keys()))

        while True:
            raw = self.input_func("Choose the piece number (0–15): ")
            try:
                choice = int(raw)
                return remaining[choice]
            except KeyError:
                self.output_func("❌ Invalid piece. Choose from the available ones.")
            except ValueError:
                self.output_func("⚠️ Invalid input. Enter an integer.")

    def _parse_position(self, raw: str) -> tuple[int, int]:
        x_str, y_str = raw.strip().split(",")
        return int(x_str), int(y_str)
