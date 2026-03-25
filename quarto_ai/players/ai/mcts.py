import copy
import math
import random

from quarto_ai.players.base import BaseModel
from quarto_ai.game.state import GameState
from quarto_ai.game.piece import Piece
from ...game.types import Player, GamePhase, GameResult

MoveType = tuple[int, int] | Piece | None


class MCTSNode:
    """
    A node in the Monte Carlo Tree Search tree.

    :param parent: Parent node in the tree (None if root).
    :param move: Last move made (None for the initial root).
    :param player_who_moved: Player who made the last move (None for the initial root).
    :param unexplored_moves: List of unexplored possible moves.
    """
    def __init__(self,
                 parent: "MCTSNode",
                 move: MoveType,
                 player_who_moved: Player | None,
                 unexplored_moves: list[MoveType]) -> None:
        self.move: MoveType = move
        self.player_who_moved: Player | None = player_who_moved

        self.parent: "MCTSNode" = parent
        self.children: list[MCTSNode] = []
        self.unexplored_moves: list[MoveType] = unexplored_moves

        self.visits: int = 0
        self.wins: int = 0

    def is_fully_expanded(self):
        """
        Checks if the node is fully expanded or can create child nodes.

        :returns boolean: True if the node is fully expanded, False otherwise.
        """
        return not self.unexplored_moves

    def ucb1(self, exploration_weight) -> float:
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

    def best_child_selection(self, exploration_weight) -> "MCTSNode":
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

    def best_child_play_ratio(self) -> "MCTSNode":
        """
        Return the child node to play according to win/loss ratio.

        :returns MCTSNode: The child node with the maximum number of visits.
        """
        return max(self.children, key=lambda node: node.wins/node.visits if node.visits > 0 else 0)






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

    def __init__(self, simulations: int, exploration_weight: float, name: str = "MCTS"):
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
            unexplored_moves=self._get_legal_moves(game)
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
            self._apply_move(game, node.move)

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
        self._apply_move(game, child_move)


        new_node = MCTSNode(
            parent=node,
            move=child_move,
            player_who_moved=child_player,
            unexplored_moves=self._get_legal_moves(game)
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
            moves = self._get_legal_moves(game)
            move = random.choice(moves)
            self._apply_move(game, move)
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
            if current_node.player_who_moved == result:
                current_node.wins += 1
            if current_node.parent is None:
                break
            current_node = current_node.parent


    def _get_legal_moves(self, game: GameState) -> list[MoveType]:
        """
        Find every legal moves from a game state position.

        :param game: Game state to generate the legal moves from.
        """
        moves: list[MoveType] = []

        if game.phase == GamePhase.PLACEMENT:
            moves = game.get_available_positions()
        elif game.phase == GamePhase.SELECTION:
            moves = game.get_remaining_pieces_list()

        return moves

    def _apply_move(self, game: GameState, move: MoveType) -> None:
        """
        Apply a single move to the given game state.

        :param game: Game state to apply a move from.
        :param move: Move to apply to the current game state.
        """
        if game.phase == GamePhase.PLACEMENT:
            game.place_piece(move[0], move[1])
        elif game.phase == GamePhase.SELECTION:
            game.select_piece(move)
