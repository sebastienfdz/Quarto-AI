import logging
import sys

from quarto_benchmark.players.ai.mcts import MCTS
from quarto_benchmark.players.ai.minimax.evaluator import SimpleEvaluator
from quarto_benchmark.players.ai.minimax.minimax import Minimax
from quarto_benchmark.players.ai.random_ai import RandomAI
from quarto_benchmark.players.base import BaseModel
from quarto_benchmark.players.human import HumanPlayer
from quarto_benchmark.runners.game_runner import GameRunner

logger = logging.getLogger("quarto_benchmark.cli")

MCTS_SIMULATION = 1_000
GAME_MODES: dict[int, tuple[str, tuple[BaseModel, BaseModel]]] = {
    1: ("Human vs Human", (HumanPlayer("Human 1"), HumanPlayer("Human 2"))),
    2: ("Human vs RandomAI", (HumanPlayer("Human"), RandomAI("RandomAI"))),
    3: ("Human vs MCTS", (HumanPlayer("Human"), MCTS(simulations=MCTS_SIMULATION, name="MCTS"))),
    4: (
        "Human vs Minimax",
        (
            HumanPlayer("Human"),
            Minimax(evaluator=SimpleEvaluator(), depth=3, use_alpha_beta=False, name="Minimax"),
        ),
    ),
    5: ("RandomAI vs MCTS", (RandomAI("RandomAI"), MCTS(simulations=MCTS_SIMULATION, name="MCTS"))),
    6: (
        "RandomAI vs Minimax",
        (
            RandomAI("RandomAI"),
            Minimax(evaluator=SimpleEvaluator(), depth=3, use_alpha_beta=False, name="Minimax"),
        ),
    ),
    7: (
        "MCTS-100 vs MCTS-1000",
        (
            MCTS(simulations=100, name="MCTS-100"),
            MCTS(simulations=1000, name="MCTS-1000"),
        ),
    ),
    8: (
        "MCTS vs Minimax",
        (
            MCTS(simulations=MCTS_SIMULATION, name="MCTS"),
            Minimax(evaluator=SimpleEvaluator(), depth=3, use_alpha_beta=False, name="Minimax"),
        ),
    ),
    9: (
        "Minimax-d2 vs Minimax-d3",
        (
            Minimax(evaluator=SimpleEvaluator(), depth=2, use_alpha_beta=False, name="Minimax-d2"),
            Minimax(evaluator=SimpleEvaluator(), depth=3, use_alpha_beta=False, name="Minimax-d3"),
        ),
    ),
}


def display_menu() -> None:
    """Display available game modes."""
    logger.info("=== Quarto CLI ===")
    logger.info("Select a game mode:")
    for key, (label, _) in GAME_MODES.items():
        logger.info(f"{key}. {label}")


def main() -> None:
    """CLI entry point for Quarto."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    display_menu()

    try:
        choice = int(input("Enter your choice: ").strip())
        label, players = GAME_MODES[choice]
    except (ValueError, KeyError):
        logger.error("Invalid choice. Exiting.")
        sys.exit(1)

    logger.info(f"Starting game: {label}\n")
    runner = GameRunner(*players)
    runner.run()


if __name__ == "__main__":
    main()
