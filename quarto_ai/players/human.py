from typing import Callable
from quarto_ai.players.base import BaseModel
from quarto_ai.game.state import GameState
from quarto_ai.game.piece import Piece


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
            output_func: Callable[[str], None] = print):
        super().__init__(name)
        self.input_func = input_func
        self.output_func = output_func

    def choose_position(self, state: GameState, piece: Piece) -> tuple[int, int]:
        """Ask the user for a valid position (row, col)."""
        while True:
            try:
                raw = self.input_func(f"Place piece {piece.to_bits():02d} (format: row,col): ")
                x_str, y_str = raw.strip().split(",")
                x, y = int(x_str), int(y_str)

                if (x, y) in state.get_available_positions():
                    return x, y
                self.output_func("❌ Position unavailable. Try again.")
            except ValueError:
                self.output_func("⚠️ Invalid format. Use format 'row,col' (e.g.: 0,3).")
            except Exception as e:
                self.output_func(f"⚠️ Error: {e}")

    def choose_piece(self, state: GameState) -> Piece:
        """Ask the user to select a piece for the opponent."""
        remaining = state.get_remaining_pieces()

        self.output_func("Available pieces:")
        self.output_func(" ".join(f"{piece_id:02d}" for piece_id in remaining.keys()))

        while True:
            try:
                choice = int(self.input_func("Choose the piece number (0–15): "))
                return remaining[choice]
            except KeyError:
                self.output_func("❌ Invalid piece. Choose from the available ones.")
            except ValueError:
                self.output_func("⚠️ Invalid input. Enter an integer.")
