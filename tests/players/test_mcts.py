import copy
import math
import pytest
import random

from quarto_ai.game.state import GameState
from quarto_ai.game.types import Player, GamePhase, GameResult
from quarto_ai.players.ai.mcts import MCTS, MCTSNode


# Fixture GameState
@pytest.fixture
def new_game() -> GameState:
    """Create a new game of Quarto. Synchronized with `root_node` (Phase = SELECTION)."""
    game = GameState()
    return game

@pytest.fixture
def game_with_selected_piece() -> GameState:
    """Create a new game of Quarto. Synchronized with `new_mcts_node` (Phase = PLACEMENT)."""
    game = GameState()
    piece = game.get_remaining_pieces_list()[0]
    game.select_piece(piece)
    return game

@pytest.fixture
def winning_game() -> GameState:
    """
    Create a new game of Quarto with a winning move (Phase = SELECTION).
    Adding the piece (0, 0, 0, 0) in the square (0, 0) is winning.
    """
    game = GameState()
    pieces = game.get_remaining_pieces()

    for x in range(1, 4):
        game.select_piece(pieces[x])
        game.place_piece(x, 0)

    assert game.result is None
    return game


# Fixture MCTSNode
@pytest.fixture
def root_node(new_game: GameState) -> MCTSNode:
    """
    A root node with a visit to allow children UCB1 calculation.
    Synchronized with `new_game` (Phase = SELECTION).
    """
    pieces = new_game.get_remaining_pieces_list()
    node = MCTSNode(parent=None, move=None, player_who_moved=None, unexplored_moves=pieces)
    node.visits = 1
    return node

@pytest.fixture
def new_mcts_node(root_node: MCTSNode, game_with_selected_piece: GameState) -> MCTSNode:
    """
    A new MCTS Node, synchronized with `game_with_selected_piece` (Phase = PLACEMENT).
    It has unexplored moves and no current children.
    """
    piece = game_with_selected_piece.next_piece
    node = MCTSNode(
        parent=root_node,
        move=piece,
        player_who_moved=Player.PLAYER_1,
        unexplored_moves=[(1, 1), (2, 2)]
    )
    return node

@pytest.fixture
def expanded_mcts_node(root_node: MCTSNode, game_with_selected_piece: GameState) -> MCTSNode:
    """
    An expanded MCTS Node, synchronized with `game_with_selected_piece` (Phase = PLACEMENT).
    It has no unexplored moves, but has children.
    """
    piece = game_with_selected_piece.next_piece
    node = MCTSNode(
        parent=root_node,
        move=piece,
        player_who_moved=Player.PLAYER_1,
        unexplored_moves=[]
    )
    node.visits = 5

    child1 = MCTSNode(
        parent=node,
        move=(1, 1),
        player_who_moved=Player.PLAYER_2,
        unexplored_moves=[]
    )
    child1.visits = 2
    child1.wins = 1

    child2 = MCTSNode(
        parent=node,
        move=(2, 2),
        player_who_moved=Player.PLAYER_2,
        unexplored_moves=[]
    )
    child2.visits = 3
    child2.wins = 0

    node.children = [child1, child2]
    return node

@pytest.fixture
def terminal_mcts_node(root_node: MCTSNode, new_game) -> MCTSNode:
    """A terminal MCTS Node: a node in a finished state and without any unexplored moves."""
    piece = new_game.get_remaining_pieces_list()[0]
    node = MCTSNode(parent=root_node,
                         move=piece,
                         player_who_moved=Player.PLAYER_1,
                         unexplored_moves=[])
    node.visits = 4
    node.wins = 2
    return node


# Fixture MCTS
@pytest.fixture
def new_mcts() -> MCTS:
    mcts = MCTS(exploration_weight=1.414, simulations=1000)
    return mcts



# Test MCTSNode
def test_ucb1_zero_visits(new_mcts_node: MCTSNode):
    """A MCTSNode that has not been visited should have an UCB1 score of infinity (div by 0)."""
    assert new_mcts_node.ucb1(exploration_weight=1.414) == math.inf


def test_ucb1(expanded_mcts_node: MCTSNode):
    """A MCTSNode that has been visited should have a positive real number as UCB1 score."""
    assert expanded_mcts_node.ucb1(exploration_weight=1.414) >= 0


def test_is_fully_expanded_true(expanded_mcts_node: MCTSNode):
    """A MCTSNode with no unexplored_moves should be fully expanded."""
    assert expanded_mcts_node.is_fully_expanded()


def test_is_fully_expanded_new_false(new_mcts_node: MCTSNode):
    """A new MCTSNode with unexplored_moves should not be fully expanded."""
    assert not new_mcts_node.is_fully_expanded()


def test_is_fully_expanded_terminal_true(terminal_mcts_node: MCTSNode):
    """A terminal MCTSNode should be fully expanded."""
    assert terminal_mcts_node.is_fully_expanded()


def test_terminal_node(terminal_mcts_node):
    """If a MCTSNode represents an end of game, there should be no unexplored_moves."""
    assert len(terminal_mcts_node.unexplored_moves) == 0


def test_best_child_selection_new(new_mcts_node):
    """A MCTSNode child selection should raise if it is not fully expanded."""
    with pytest.raises(ValueError, match="Node is not fully expanded."):
        new_mcts_node.best_child_selection(exploration_weight=1.414)


def test_best_child_selection_expanded(expanded_mcts_node):
    """A fully expanded MCTSNode should select the best child according to UCB1 scores."""
    best_node = expanded_mcts_node.best_child_selection(exploration_weight=1.414)
    ucb1_list = [node.ucb1(exploration_weight=1.414) for node in expanded_mcts_node.children]
    assert max(ucb1_list) == best_node.ucb1(exploration_weight=1.414)


def test_best_child_selection_terminal(terminal_mcts_node):
    """A terminal MCTSNode child selection should raise if it is terminal."""
    with pytest.raises(ValueError, match="Node is not fully expanded."):
        terminal_mcts_node.best_child_selection(exploration_weight=1.414)


def test_best_child_play(expanded_mcts_node):
    """A fully expanded MCTSNode should choose the best child according to win/loss ratio."""
    best_node = expanded_mcts_node.best_child_play()
    visits_list = [node.visits for node in expanded_mcts_node.children]
    assert max(visits_list) == best_node.visits



# Test MCTS
def test_choose_piece_valid(new_game: GameState, new_mcts: MCTS):
    """The AI should select a valid available piece from the pool."""
    piece = new_mcts.choose_piece(new_game)
    assert piece in new_game.get_remaining_pieces_list()


def test_choose_piece_not_winning(winning_game: GameState, new_mcts: MCTS):
    """
    In a situation where the opponent could win, the AI
    must not choose the piece that completes the Quarto.
    """
    loosing_piece = winning_game.get_remaining_pieces_list()[0]
    chosen_piece = new_mcts.choose_piece(winning_game)
    assert chosen_piece != loosing_piece


def test_choose_position_valid(new_game: GameState, new_mcts: MCTS):
    """The AI should select an valid empty square on the board."""
    piece = new_game.get_remaining_pieces_list()[0]
    new_game.select_piece(piece)

    x, y = new_mcts.choose_position(new_game, piece)
    assert (x, y) in new_game.get_available_positions()


def test_choose_position_winning(winning_game: GameState, new_mcts: MCTS):
    """The AI must select the winning square when handed a winning piece."""
    winning_piece = winning_game.get_remaining_pieces_list()[0]
    winning_game.select_piece(winning_piece)

    x, y = new_mcts.choose_position(winning_game, winning_piece)
    assert (x, y) == (0, 0)



def test_select(game_with_selected_piece: GameState, new_mcts_node: MCTSNode, new_mcts: MCTS):
    """
    Selection should traverse the tree using UCB1 until it finds a node
    that is not fully expanded, returning that node.
    """
    selected_node, selected_game = new_mcts._select(new_mcts_node, game_with_selected_piece)
    assert isinstance(selected_node, MCTSNode)
    assert not selected_node.is_fully_expanded() or not selected_node.children


def test_select_clones_game_states(game_with_selected_piece: GameState, new_mcts: MCTS, expanded_mcts_node: MCTSNode):
    """
    Selection must deep copy the GameState, apply moves along the path,
    and return a non-fully expanded node.
    """
    leaf_move = game_with_selected_piece.get_remaining_pieces_list()[0]
    leaf_node = MCTSNode(parent=expanded_mcts_node.children[0], move=leaf_move,
                         player_who_moved=Player.PLAYER_1, unexplored_moves=[(3, 3)])
    expanded_mcts_node.children[0].children = [leaf_node]

    selected_node, selected_game = new_mcts._select(expanded_mcts_node, game_with_selected_piece)

    assert not selected_node.is_fully_expanded() or not selected_node.children
    assert selected_node == leaf_node
    assert leaf_move not in selected_game.get_remaining_pieces_list()


def test_expand(game_with_selected_piece: GameState, new_mcts: MCTS, new_mcts_node: MCTSNode):
    """Expansion should create exactly one new child node for the given leaf node."""
    initial_unexplored_moves = copy.deepcopy(new_mcts_node.unexplored_moves)

    child_node, updated_game = new_mcts._expand(new_mcts_node, game_with_selected_piece)

    assert isinstance(child_node, MCTSNode)
    assert child_node.parent == new_mcts_node
    assert child_node in new_mcts_node.children
    assert child_node.move in initial_unexplored_moves
    assert not child_node.children


def test_expand_removes_unexplored(game_with_selected_piece: GameState, new_mcts: MCTS, new_mcts_node: MCTSNode):
    """
    The move used to create the new child node must be
    removed from the parent's unexplored_moves list.
    """
    initial_unexplored_count = len(new_mcts_node.unexplored_moves)
    initial_children_count = len(new_mcts_node.children)

    random.seed(42)
    child_node, updated_game = new_mcts._expand(new_mcts_node, game_with_selected_piece)

    assert len(new_mcts_node.children) == initial_children_count + 1
    assert len(new_mcts_node.unexplored_moves) == initial_unexplored_count - 1
    assert child_node.move not in new_mcts_node.unexplored_moves


def test_simulate(new_game: GameState, new_mcts: MCTS):
    """
    Simulation should play random moves until the game reaches a terminal state,
    returning a valid GameResult without modifying the input node.
    """
    random.seed(42)
    result = new_mcts._simulate(new_game)

    assert isinstance(result, GameResult)
    assert result is not None
    assert new_game.result is not None


def test_backpropagate(new_mcts: MCTS, new_game: GameState):
    """
    Backpropagation should increment the visit count of all nodes
    in the path from the expanded node up to the root.
    """
    pieces = new_game.get_remaining_pieces_list()

    root = MCTSNode(parent=None, move=None, player_who_moved=None, unexplored_moves=[])
    child1 = MCTSNode(parent=root, move=pieces.pop(0), player_who_moved=Player.PLAYER_1, unexplored_moves=[(0, 0), (1, 1)])
    child2 = MCTSNode(parent=child1, move=(0, 0), player_who_moved=Player.PLAYER_2, unexplored_moves=[pieces[0]])
    child3 = MCTSNode(parent=child2, move=pieces.pop(0), player_who_moved=Player.PLAYER_2, unexplored_moves=[(1, 1)])
    child4 = MCTSNode(parent=child3, move=(1, 1), player_who_moved=Player.PLAYER_1, unexplored_moves=None)
    root.visits = 4 ; child1.visits = 3 ; child2.visits = 2 ; child3.visits = 1

    new_mcts._backpropagate(child4, GameResult.PLAYER_1)

    assert child4.visits == 1
    assert child3.visits == 2
    assert child2.visits == 3
    assert child1.visits == 4
    assert root.visits == 5


def test_backpropagate_credit_assignement(new_mcts: MCTS, new_game: GameState):
    """
    A win for Player X should only increase the win count of
    nodes where the player_who_moved was Player X..
    """
    pieces = new_game.get_remaining_pieces_list()

    root = MCTSNode(parent=None, move=None, player_who_moved=None, unexplored_moves=[])
    child1 = MCTSNode(parent=root, move=pieces.pop(0), player_who_moved=Player.PLAYER_1, unexplored_moves=[(0, 0), (1, 1)])
    child2 = MCTSNode(parent=child1, move=(0, 0), player_who_moved=Player.PLAYER_2, unexplored_moves=[pieces[0]])
    child3 = MCTSNode(parent=child2, move=pieces.pop(0), player_who_moved=Player.PLAYER_2, unexplored_moves=[(1, 1)])
    child4 = MCTSNode(parent=child3, move=(1, 1), player_who_moved=Player.PLAYER_1, unexplored_moves=None)
    root.visits = 4 ; child1.visits = 3 ; child2.visits = 2 ; child3.visits = 1

    new_mcts._backpropagate(child4, GameResult.PLAYER_1)

    assert child4.visits == 1 and child4.wins == 1
    assert child3.visits == 2 and child3.wins == 0
    assert child2.visits == 3 and child2.wins == 0
    assert child1.visits == 4 and child1.wins == 1
    assert root.visits == 5 and root.wins == 0
