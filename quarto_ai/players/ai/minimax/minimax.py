from quarto_ai.game.piece import Piece
from quarto_ai.game.state import GameState
from quarto_ai.game.types import Player
from quarto_ai.players.ai.minimax.evaluator import BaseEvaluator
from quarto_ai.players.base import BaseModel


class Minimax(BaseModel):
    """
    Minimax AI Player with Alpha-Beta pruning.

    Uses dependency injection for the evaluation function, allowing the same
    search algorithm to be benchmarked with different heuristics.
    """

    def __init__(
        self,
        evaluator: BaseEvaluator,
        depth: int,
        use_alpha_beta: bool = True,
        name: str = "Minimax",
    ) -> None:
        """
        :param evaluator: The heuristic evaluation function.
        :param depth: The search depth in plies (half-steps).
        :param use_alpha_beta: If True, uses Alpha-Beta pruning. If False, uses naive Minimax.
        :param name: The display name of the agent.
        """
        super().__init__(name)
        self.evaluator = evaluator
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta

    def choose_position(self, state: GameState, piece: Piece) -> tuple[int, int]:
        """
        Searches the game tree to find the best placement for the given piece.

        :param state: The current game state.
        :param piece: The piece to place (already assigned to state.next_piece).
        TODO: remove this piece parameter
        :returns: The (x, y) coordinates for the optimal placement.
        """
        best_score = float("-inf")
        best_position = None
        maximizing_player = state.current_player

        for pos in state.board.get_available_positions():
            clone = state.clone()
            clone.place_piece(*pos)

            if self.use_alpha_beta:
                score = self._minimax_alpha_beta(
                    clone, self.depth - 1, float("-inf"), float("inf"), maximizing_player
                )
            else:
                score = self._minimax_naive(clone, self.depth - 1, maximizing_player)

            if best_position is None or score > best_score:
                best_score = score
                best_position = pos

        if not isinstance(best_position, tuple):
            raise TypeError(f"Expected tuple, got {type(best_position).__name__}")
        return best_position

    def choose_piece(self, state: GameState) -> Piece:
        """
        Searches the game tree to find the best piece to give to the opponent.

        :param state: The current game state.
        :returns: The optimal Piece to give.
        """
        best_score = float("-inf")
        best_piece = None
        maximizing_player = state.current_player

        for piece in state.get_remaining_pieces():
            clone = state.clone()
            clone.select_piece(piece)

            if self.use_alpha_beta:
                score = self._minimax_alpha_beta(
                    clone, self.depth - 1, float("-inf"), float("inf"), maximizing_player
                )
            else:
                score = self._minimax_naive(clone, self.depth - 1, maximizing_player)

            if best_piece is None or score > best_score:
                best_score = score
                best_piece = piece

        if not isinstance(best_piece, Piece):
            raise TypeError(f"Expected Piece, got {type(best_piece).__name__}")
        return best_piece

    def _minimax_naive(self, state: GameState, depth: int, maximizing_player: Player) -> float:
        """
        Recursive Minimax search WITHOUT pruning. (Used for benchmarking).

        :param state: The current state node in the search tree.
        :param depth: The remaining depth to search (in plies).
        :param maximizing_player: The player whose score we are trying to maximize.
        :returns: The heuristic score of the node from the maximizing_player's perspective.
        """
        if state.result is not None or depth == 0:
            return self._evaluate_for_maximizer(state, maximizing_player)

        is_maximizing = state.current_player == maximizing_player
        best_score = float("-inf") if is_maximizing else float("inf")

        for move in state.get_legal_moves():
            clone = state.clone()
            clone.apply_move(move)

            score = self._minimax_naive(clone, depth - 1, maximizing_player)
            if is_maximizing:
                best_score = max(best_score, score)
            else:
                best_score = min(best_score, score)

        return best_score

    def _minimax_alpha_beta(
        self,
        state: GameState,
        depth: int,
        alpha: float,
        beta: float,
        maximizing_player: Player,
    ) -> float:
        """
        Recursive Minimax search with Alpha-Beta pruning.

        :param state: The current state node in the search tree.
        :param depth: The remaining depth to search (in plies).
        :param alpha: The alpha bound for pruning (best score guaranteed for maximizer).
        :param beta: The beta bound for pruning (best score guaranteed for minimizer).
        :param maximizing_player: The player whose score we are trying to maximize.
        :returns: The heuristic score of the node from the maximizing_player's perspective.
        """
        if state.result is not None or depth == 0:
            return self._evaluate_for_maximizer(state, maximizing_player)

        is_maximizing = state.current_player == maximizing_player
        best_score = float("-inf") if is_maximizing else float("inf")

        for move in state.get_legal_moves():
            clone = state.clone()
            clone.apply_move(move)

            score = self._minimax_alpha_beta(clone, depth - 1, alpha, beta, maximizing_player)

            if is_maximizing:
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            else:
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break

        return best_score

    def _evaluate_for_maximizer(self, state: GameState, maximizing_player: Player) -> float:
        """
        Helper to convert the absolute PLAYER_1 score from the evaluator
        into a relative score for the maximizing player.
        """
        absolute_score = self.evaluator.evaluate(state)
        return absolute_score if maximizing_player == Player.PLAYER_1 else -absolute_score
