from quarto_ai.game.piece import Piece
from quarto_ai.game.state import GameState
from quarto_ai.game.exceptions import (
    InvalidPieceError,
    InvalidSquareError,
    GameEndedError,
)


class QuartoCLI:
    """Command Line Interface for playing Quarto in Player vs Player mode."""

    def __init__(self):
        self.game = GameState()


    def display_board(self) -> None:
        """Displays the current board and active player."""
        print("\n" + str(self.game))
        print(f"Player {self.game.current_player}'s turn.\n")
        if self.game.next_piece:
            print(f"Must place piece: {self.game.next_piece}\n")


    def select_position(self) -> tuple[int, int]:
        """Asks the player to choose an available board position (row, col)."""
        while True:
            try:
                raw_input = input("Select a position (format: row,col): ")
                x_str, y_str = raw_input.strip().split(",")
                x, y = int(x_str), int(y_str)

                if (x, y) in self.game.get_available_positions():
                    return x, y
                print("❌ Position unavailable. Try again.")

            except ValueError:
                print("⚠️ Invalid format. Try again with format: 'row,col' (e.g.: 0,3).")
            except Exception as e:
                print(f"⚠️ Error: {e}")

    def select_piece(self) -> Piece | None:
        """Asks the player to choose a piece to give to the opponent."""
        remaining = self.game.get_remaining_pieces()

        print("Available pieces:")
        print(" ".join(f"{piece_id:02d}" for piece_id in remaining.keys()))

        while True:
            try:
                choice = int(input("Choose the piece number (0–15): "))
                return remaining[choice]
            except KeyError:
                print("❌ Invalid piece. Choose again from the available ones.")
            except ValueError:
                print("⚠️ Invalid input. Enter an integer.")


    def play_turn(self) -> None:
        """Executes one turn: place the given piece, then choose the next piece."""
        try:
            if self.game.next_piece is None:
                self.game.next_piece = self.select_piece()
                return

            x, y = self.select_position()
            self.game.play_move(x, y, self.game.next_piece)

            if self.game.winner is not None:
                return

            self.game.next_piece = self.select_piece()

        except InvalidSquareError:
            print("❌ Invalid move at ({x}, {y}). Try again.")
        except InvalidPieceError:
            print("❌ Invalid piece. Try again.")
        except GameEndedError:
            print("The game is already over.")
        except Exception as e:
            print(f"Unexpected error: {e}")


    def run(self) -> None:
        """Main game loop."""
        print("=== Quarto CLI: Player vs Player ===")
        while self.game.winner is None:
            self.display_board()
            self.play_turn()

        self.display_board()
        if self.game.winner == -1:
            print("🤝 Draw.")
        else:
            print(f"🏆 Player {self.game.winner} wins!")


if __name__ == "__main__":
    QuartoCLI().run()
