from quarto_ai.game.state import GameState
from quarto_ai.game.types import GameResult
from quarto_ai.players.base import BaseModel


class GameRunner:
    """Game engine runner that orchestrates a match between two players."""

    def __init__(self, player0: BaseModel, player1: BaseModel) -> None:
        self.game = GameState()
        self.players = [player0, player1]

    def _display_board(self) -> None:
        """Prints the current board and indicates the active player."""
        print("\n" + str(self.game))
        if self.game.result is None:
            current_idx = self.game.current_player
            current_player = self.players[current_idx].name
            print(f"{current_player} (Player {current_idx}) to move.\n")

    def _play_turn(self) -> None:
        """Executes a single turn of the game."""
        current = self.players[self.game.current_player]
        if self.game.next_piece is None:
            raise ValueError("No piece selected to be placed.")

        x, y = current.choose_position(self.game, self.game.next_piece)
        self.game.place_piece(x, y)

        if self.game.result is None:
            next_piece = current.choose_piece(self.game)
            self.game.select_piece(next_piece)

    def run(self) -> None:
        """Main game loop."""
        print("=== Quarto Game ===")
        print(f"Player 0: {self.players[0].name}\n" + f"Player 1: {self.players[1].name}\n")

        next_piece = self.players[0].choose_piece(self.game)
        self.game.select_piece(next_piece)

        self._display_board()
        while self.game.result is None:
            self._play_turn()
            self._display_board()

        if self.game.result == GameResult.DRAW:
            print("Draw.")
        else:
            winner = self.game.result
            print(f"🏆 Player {winner} ({self.players[winner].name}) wins!")
