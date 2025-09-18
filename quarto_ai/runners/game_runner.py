from quarto_ai.players.base import BaseModel
from quarto_ai.game.state import GameState


class GameRunner:
    """Game engine runner that orchestrates a match between two players."""

    def __init__(self, player0: BaseModel, player1: BaseModel):
        self.game = GameState()
        self.players = [player0, player1]

    def _display_board(self) -> None:
        """Prints the current board and indicates the active player."""
        current_idx = self.game.current_player
        current_player = self.players[current_idx].name
        print("\n" + str(self.game))
        print(f"{current_player} (Player {current_idx + 1}) to move.\n")

    def _play_turn(self) -> None:
        """Executes a single turn of the game."""
        current = self.players[self.game.current_player]

        if self.game.next_piece is None:
            self.game.next_piece = current.choose_piece(self.game)
            return 

        x, y = current.choose_position(self.game, self.game.next_piece)
        self.game.play_move(x, y, self.game.next_piece)

        if self.game.winner is None:
            self.game.next_piece = current.choose_piece(self.game)


    def run(self) -> None:
        """Main game loop."""
        print("=== Quarto Game ===")
        print(f"Player 0: {self.players[0].name}\n" + f"Player 1: {self.players[1].name}\n")
        self._display_board()

        while self.game.winner is None:
            self._play_turn()
            self._display_board()

        if self.game.winner == -1:
            print("Draw.")
        else:
            winner = self.game.winner
            print(f"🏆 Player {winner} ({self.players[winner].name}) wins!")
