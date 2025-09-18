from quarto_ai.players.base import BaseModel
from quarto_ai.game.state import GameState
from quarto_ai.game.piece import Piece


class HumanPlayer(BaseModel):
    """A human-controlled player using CLI input."""

    def choose_position(self, state: GameState, piece: Piece) -> tuple[int, int]:
        """Ask the user for a valid position (row, col)."""
        while True:
            try:
                raw_input = input(f"Place piece {piece.to_bits():02d} (format: row,col): ")
                x_str, y_str = raw_input.strip().split(",")
                x, y = int(x_str), int(y_str)

                if (x, y) in state.get_available_positions():
                    return x, y
                print("❌ Position unavailable. Try again.")
            except ValueError:
                print("⚠️ Invalid format. Use format 'row,col' (e.g.: 0,3).")
            except Exception as e:
                print(f"⚠️ Error: {e}")

    def choose_piece(self, state: GameState) -> Piece:
        """Ask the user to select a piece for the opponent."""
        remaining = state.get_remaining_pieces()

        print("Available pieces:")
        print(" ".join(f"{piece_id:02d}" for piece_id in remaining.keys()))

        while True:
            try:
                choice = int(input("Choose the piece number (0–15): "))
                return remaining[choice]
            except KeyError:
                print("❌ Invalid piece. Choose from the available ones.")
            except ValueError:
                print("⚠️ Invalid input. Enter an integer.")
