import abc
import math
from typing import ClassVar

from quarto_ai.game.piece import Piece
from quarto_ai.game.state import GameState
from quarto_ai.game.types import GamePhase, GameResult, Player


def evaluate_line(line: list[Piece | None]) -> int:
    """
    Returns the threat level of a single line (row, column, or diagonal).

    A line is "alive" if all placed pieces share at least one binary attribute,
    meaning a Quarto could still theoretically be formed along it. Uses bitwise
    operations for O(n) detection of shared attributes.

    :param line: A list of exactly 4 elements (Pieces or None).
    :returns: The number of placed pieces if the line is alive, 0 if dead or empty.
              3 means a one-move Quarto threat. 4 means a Quarto has been formed.
    """
    pieces = [p for p in line if p is not None]
    if not pieces:
        return 0

    shared_ones = 0b1111
    shared_zeros = 0b1111
    for p in pieces:
        bits = p.to_bits()
        shared_ones &= bits
        shared_zeros &= ~bits & 0b1111

    return len(pieces) if (shared_ones | shared_zeros) > 0 else 0


class BaseEvaluator(abc.ABC):
    """
    Abstract base class for Minimax position evaluators.

    Follows the Strategy pattern: a MinimaxPlayer accepts any BaseEvaluator,
    enabling benchmarking of different evaluation functions against each other.
    """

    @abc.abstractmethod
    def evaluate(self, state: GameState) -> float:
        """
        Scores the game state from PLAYER_1's absolute perspective.

        Positive values favour PLAYER_1; negative values favour PLAYER_2.
        The Minimax tree is responsible for sign interpretation — this method
        must not be aware of who is the maximizing player.

        :param state: The current game state to evaluate. Must not be mutated.
        :returns: A float score in the range (-inf, +inf). Terminal wins return
                  math.inf or -math.inf.
        """


class SimpleEvaluator(BaseEvaluator):
    """
    A basic heuristic evaluator based on alive-line threat counts.

    Scores a board by summing weighted threat levels across all lines.
    Only 2-piece and 3-piece alive lines contribute to the score.
    """
    _THREE_THREAT_WEIGHT: ClassVar[float] = 5.0
    _TWO_THREAT_WEIGHT: ClassVar[float] = 1.0

    def evaluate(self, state: GameState) -> float:
        if state.result == GameResult.PLAYER_1:
            return math.inf
        if state.result == GameResult.PLAYER_2:
            return -math.inf
        if state.result == GameResult.DRAW:
            return 0.0

        if state.phase == GamePhase.PLACEMENT:
            placer = state.current_player
        else:
            placer = state.current_player.opponent
        sign = 1.0 if placer == Player.PLAYER_1 else -1.0
        score = 0.0

        for line in state.board.get_lines():
            threat = evaluate_line(line)
            if threat == 3:
                score += self._THREE_THREAT_WEIGHT
            elif threat == 2:
                score += self._TWO_THREAT_WEIGHT

        return sign * score
