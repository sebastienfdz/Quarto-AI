import logging

from quarto_benchmark.game.state import GameState
from quarto_benchmark.game.types import GameResult
from quarto_benchmark.players.base import BaseModel


class GameRunner:
    """Game engine runner that orchestrates a match between two players."""

    def __init__(self, player0: BaseModel, player1: BaseModel) -> None:
        self.game = GameState()
        self.players = [player0, player1]
        self.logger = logging.getLogger("quarto_benchmark.game_runner")

    def _display_board(self) -> None:
        """Logs the current board and indicates the active player."""
        self.logger.info("\n" + str(self.game))
        if self.game.result is None:
            current_idx = self.game.current_player
            current_player = self.players[current_idx].name
            self.logger.info(f"{current_player} (Player {current_idx}) to move.\n")

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
        self.logger.info("=== Quarto Game ===")
        self.logger.info(
            f"Player 0: {self.players[0].name}\n" + f"Player 1: {self.players[1].name}\n"
        )

        next_piece = self.players[0].choose_piece(self.game)
        self.game.select_piece(next_piece)

        self._display_board()
        while self.game.result is None:
            self._play_turn()
            self._display_board()

        if self.game.result == GameResult.DRAW:
            self.logger.info("Draw.")
        else:
            winner = self.game.result
            self.logger.info(f"🏆 Player {winner} ({self.players[winner].name}) wins!")
