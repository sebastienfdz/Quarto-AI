import sys
from quarto_ai.runners.game_runner import GameRunner
from quarto_ai.players.human import HumanPlayer
from quarto_ai.players.ai.random_ai import RandomAI

GAME_MODES: dict[int, tuple[str, tuple]] = {
    1: ("Human vs Human", (HumanPlayer("Human 1"), HumanPlayer("Human 2"))),
    2: ("Human vs RandomAI", (HumanPlayer("Human"), RandomAI("RandomAI"))),
    3: ("RandomAI vs RandomAI", (RandomAI("RandomAI-1"), RandomAI("RandomAI-2"))),
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
