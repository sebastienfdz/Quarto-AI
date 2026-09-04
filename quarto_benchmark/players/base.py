import abc

from quarto_benchmark.game.piece import Piece
from quarto_benchmark.game.state import GameState


class BaseModel(abc.ABC):
    """
    Abstract base class for all Quarto AI models.
    Defines the standard interface every AI must implement.
    """

    def __init__(self, name: str = "BaseModel") -> None:
        self.name = name

    @abc.abstractmethod
    def choose_position(self, state: GameState, piece: Piece) -> tuple[int, int]:
        """
        Decide where to place the given piece on the board.

        :param state: Current GameState
        :param piece: Piece to place
        :return: (row, col) coordinates of the move
        """

    @abc.abstractmethod
    def choose_piece(self, state: GameState) -> Piece:
        """
        Decide which piece to give to the opponent.

        :param state: Current GameState
        :return: Piece object chosen
        """
