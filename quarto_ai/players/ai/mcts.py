import copy
import math
import random

from quarto_ai.game.piece import Piece
from quarto_ai.game.state import GameState, MoveType
from quarto_ai.players.base import BaseModel

from ...game.types import GameResult, Player


class MCTSNode:
    """
    A node in the Monte Carlo Tree Search tree.

    :param parent: Parent node in the tree (None if root).
    :param move: Last move made (None for the initial root).
    :param player_who_moved: Player who made the last move (None for the initial root).
    :param unexplored_moves: List of unexplored possible moves.
    """

    def __init__(
        self,
        parent: "MCTSNode | None",
        move: MoveType,
        player_who_moved: Player | None,
        unexplored_moves: list[MoveType],
    ) -> None:
        self.move: MoveType = move
        self.player_who_moved: Player | None = player_who_moved

        self.parent: MCTSNode | None = parent
        self.children: list[MCTSNode] = []
        self.unexplored_moves: list[MoveType] = unexplored_moves

        self.visits: int = 0
        self.wins: int = 0

    def is_fully_expanded(self) -> bool:
        """
        Checks if the node is fully expanded or can create child nodes.

        :returns boolean: True if the node is fully expanded, False otherwise.
        """
        return not self.unexplored_moves

    def ucb1(self, exploration_weight: float) -> float:
        """
        Compute the UCB1 score for a node.

        :param exploration_weight: Exploration parameter C of the UCB1 formula.
        :returns float: UCB1 score.
        """
        if self.visits == 0 or not self.parent:
            return math.inf

        exploitation = self.wins / self.visits
        exploration = math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + (exploration_weight * exploration)

    def best_child_selection(self, exploration_weight: float) -> "MCTSNode":
        """
        Return the child node to select according to node UCB1 score.

        :param exploration_weight: Exploration parameter C of the UCB1 formula.
        :returns MCTSNode: The child node with maximum UCB1 value.
        :raises ValueError: If the node is not fully expanded, or is terminal (no possible moves).
        """
        if not self.is_fully_expanded() or not self.children:
            raise ValueError("Node is not fully expanded.")
        return max(self.children, key=lambda node: node.ucb1(exploration_weight))

    def best_child_play(self) -> "MCTSNode":
        """
        Return the child node to play according to node visits.

        :returns MCTSNode: The child node with the maximum number of visits.
        """
        return max(self.children, key=lambda node: node.visits)


class MCTS(BaseModel):
    """
    Monte Carlo Tree Search AI for Quarto.

    Implements the standard MCTS algorithm:
    1. Selection
    2. Expansion
    3. Simulation
    4. Backpropagation

    :param name: AI identifier.
    :param simulations: Number of simulations per move.
    :param exploration_weight: Exploration factor for UCB1.
    """

    def __init__(
        self, simulations: int = 1_000, exploration_weight: float = 1.414, name: str = "MCTS"
    ) -> None:
        super().__init__(name)
        self.simulations: int = simulations
        self.exploration_weight: float = exploration_weight
        self.root: MCTSNode | None = None

    def choose_piece(self, state: GameState) -> Piece:
        """
        Select a piece to give to the opponent.

        :param state: Current game state.
        :returns: A randomly selected available piece.
        """
        best_node = self._mcts_loop(state)
        piece = best_node.move
        if not isinstance(piece, Piece):
            raise TypeError(f"Expected Piece, got {type(piece).__name__}")
        return piece

    def choose_position(self, state: GameState, piece: Piece) -> tuple[int, int]:
        """
        Choose a position to play the given piece using MCTS.

        :param state: Current game state.
        :param piece: The piece to be placed.
        :returns: (row, col) coordinates of the chosen position.
        """
        best_node = self._mcts_loop(state)
        position = best_node.move
        if not isinstance(position, tuple):
            raise TypeError(f"Expected tuple, got {type(position).__name__}")
        return position

    def _mcts_loop(self, game: GameState) -> MCTSNode:
        """
        Main loop of the MCTS algorithm.

        :param game: Game state of the root node.
        """
        i = 0
        self.root = MCTSNode(
            parent=None,
            move=None,
            player_who_moved=None,
            unexplored_moves=game.get_legal_moves(),
        )

        while i < self.simulations:
            current_game = copy.deepcopy(game)
            node = self.root

            node, current_game = self._select(node, current_game)
            if current_game.result is None:
                node, current_game = self._expand(node, current_game)
                result = self._simulate(current_game)
            else:
                result = current_game.result
            self._backpropagate(node, result)
            i += 1

        return self.root.best_child_play()

    def _select(self, node: MCTSNode, game: GameState) -> tuple[MCTSNode, GameState]:
        """
        Traverse the tree from the root to a leaf node.

        :param node: Root node to select from.
        :param game: Game state of the root node.
        :returns: A leaf node to expand or simulate from and the newly updated game state.
        """
        while node.is_fully_expanded() and node.children:
            node = node.best_child_selection(self.exploration_weight)
            game.apply_move(node.move)

        return node, game

    def _expand(self, node: MCTSNode, game: GameState) -> tuple[MCTSNode, GameState]:
        """
        Expand one unexplored child node from the given node.

        :param node: Node to expand.
        :param game: Game state of the node to expand.
        :returns: The newly created child node and the newly updated game state.
        """
        child_player: Player = game.current_player
        child_move: MoveType = random.choice(node.unexplored_moves)
        game.apply_move(child_move)

        new_node = MCTSNode(
            parent=node,
            move=child_move,
            player_who_moved=child_player,
            unexplored_moves=game.get_legal_moves(),
        )
        node.children.append(new_node)
        node.unexplored_moves.remove(child_move)

        return new_node, game

    def _simulate(self, game: GameState) -> GameResult:
        """
        Simulate a random playout until the game ends.

        :param game: Game state to simulate from.
        :returns: Result of the simulated game.
        """
        while game.result is None:
            moves = game.get_legal_moves()
            move = random.choice(moves)
            game.apply_move(move)
        return game.result

    def _backpropagate(self, node: MCTSNode, result: GameResult) -> None:
        """
        Update visit and win counts from the node up to the root.

        :param node: Node reached at the end of selection/expansion.
        :param result: Result of the simulated game.
        """
        current_node = node

        while True:
            current_node.visits += 1
            if (
                current_node.player_who_moved is not None
                and current_node.player_who_moved.value == result.value
            ):
                current_node.wins += 1
            if current_node.parent is None:
                break
            current_node = current_node.parent
