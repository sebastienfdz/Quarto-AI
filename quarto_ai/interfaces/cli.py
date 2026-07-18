import sys

from quarto_ai.players.ai.mcts import MCTS
from quarto_ai.players.ai.random_ai import RandomAI
from quarto_ai.players.base import BaseModel
from quarto_ai.players.human import HumanPlayer
from quarto_ai.runners.game_runner import GameRunner

MCTS_SIMULATION = 1_000
GAME_MODES: dict[int, tuple[str, tuple[BaseModel, BaseModel]]] = {
    1: ("Human vs Human", (HumanPlayer("Human 1"), HumanPlayer("Human 2"))),
    2: ("Human vs RandomAI", (HumanPlayer("Human"), RandomAI("RandomAI"))),
    3: ("Human vs MCTS", (HumanPlayer("Human"), MCTS(simulations=MCTS_SIMULATION, name="MCTS"))),
    4: ("RandomAI vs RandomAI", (RandomAI("RandomAI-1"), RandomAI("RandomAI-2"))),
    5: ("RandomAI vs MCTS", (RandomAI("RandomAI"), MCTS(simulations=MCTS_SIMULATION, name="MCTS"))),
    6: (
        "MCTS vs MCTS",
        (
            MCTS(simulations=MCTS_SIMULATION, name="MCTS-1"),
            MCTS(simulations=MCTS_SIMULATION, name="MCTS-2"),
        ),
    ),
}


def display_menu() -> None:
    """Display available game modes."""
    print("=== Quarto CLI ===")
    print("Select a game mode:")
    for key, (label, _) in GAME_MODES.items():
        print(f"{key}. {label}")


def main() -> None:
    """CLI entry point for Quarto."""
    display_menu()

    try:
        choice = int(input("Enter your choice: ").strip())
        label, players = GAME_MODES[choice]
    except (ValueError, KeyError):
        print("Invalid choice. Exiting.")
        sys.exit(1)

    print(f"Starting game: {label}\n")
    runner = GameRunner(*players)
    runner.run()


if __name__ == "__main__":
    main()
