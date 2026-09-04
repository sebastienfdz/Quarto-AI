import copy
import random

from quarto_benchmark.game.board import Board
from quarto_benchmark.game.piece import Piece
from quarto_benchmark.game.state import GameState
from quarto_benchmark.players.base import BaseModel


class RandomAI(BaseModel):
    """
    A simple AI that:
    - Plays a winning move if available
    - Otherwise, plays a random legal move
    - Chooses a random piece to give to the opponent
    """

    def __init__(self, name: str = "RandomAI") -> None:
        super().__init__(name)

    def choose_piece(self, state: GameState) -> Piece:
        """Choose a random available piece to give to the opponent."""
        return random.choice(state.get_remaining_pieces())

    def choose_position(self, state: GameState, piece: Piece) -> tuple[int, int]:
        """
        Choose where to place the given piece.
        If possible choose a winning move, if not choose a random position.
        """
        positions = state.board.get_available_positions()
        board_copy = copy.deepcopy(state.board)

        for x, y in positions:
            if self._is_winning_move(board_copy, x, y, piece):
                return (x, y)
        return random.choice(positions)

    def _is_winning_move(self, board: Board, x: int, y: int, piece: Piece) -> bool:
        """Temporarily play a move, check victory, and undo it."""
        if board.game_board[x, y] is not None:
            return False

        board.game_board[x, y] = piece
        is_win = board.check_victory()
        board.game_board[x, y] = None
        return is_win
