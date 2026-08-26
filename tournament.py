import logging
import sys
from collections.abc import Callable

from quarto_ai.players.ai.mcts import MCTS
from quarto_ai.players.ai.minimax.evaluator import SimpleEvaluator
from quarto_ai.players.ai.minimax.minimax import Minimax
from quarto_ai.players.ai.random_ai import RandomAI
from quarto_ai.players.base import BaseModel
from quarto_ai.runners.exporter import ConsoleExporter
from quarto_ai.runners.tournament_runner import TournamentRunner

logger = logging.getLogger("quarto_ai.tournament")


AGENTS: dict[str, BaseModel] = {
    "RandomAI": RandomAI("RandomAI"),
    "MCTS-100": MCTS(simulations=100, name="MCTS-100"),
    "MCTS-1000": MCTS(simulations=1000, name="MCTS-1000"),
    "Minimax-d2": Minimax(
        evaluator=SimpleEvaluator(), depth=2, use_alpha_beta=False, name="Minimax-d2"
    ),
    "Minimax-d3": Minimax(
        evaluator=SimpleEvaluator(), depth=3, use_alpha_beta=False, name="Minimax-d3"
    ),
    "Minimax-d3-AB": Minimax(
        evaluator=SimpleEvaluator(), depth=3, use_alpha_beta=True, name="Minimax-d3-AB"
    ),
    "Minimax-d4-AB": Minimax(
        evaluator=SimpleEvaluator(), depth=4, use_alpha_beta=True, name="Minimax-d4-AB"
    ),
}

TOURNAMENT_MODES: dict[int, str] = {
    1: "1v1 Matchup",
    2: f"Championship ({' vs '.join(AGENTS.keys())})",
    3: "Exit",
}


def display_menu() -> None:
    """Display available tournament modes."""
    logger.info("=== Quarto Tournament CLI ===")
    logger.info("Select a mode:")
    for key, label in TOURNAMENT_MODES.items():
        logger.info(f"{key}. {label}")


def _prompt_settings() -> tuple[int, bool]:
    """Prompt the user for games per side and parallel processing."""
    try:
        games = int(input("Games per matchup side (default: 10): ").strip() or "10")
        use_parallel = input("Use parallel processing? (Y/n): ").strip().lower() != "n"
    except ValueError:
        logger.error("Invalid input. Exiting.")
        sys.exit(1)
    return games, use_parallel


def _run_matchup() -> None:
    """Run a 1v1 matchup between two chosen agents."""
    agent_list = list(AGENTS.keys())
    logger.info("\nAvailable agents:")
    for i, name in enumerate(agent_list, start=1):
        logger.info(f"  {i}. {name}")

    try:
        a = int(input("Select agent 1 (number): ").strip()) - 1
        b = int(input("Select agent 2 (number): ").strip()) - 1
        player_a = AGENTS[agent_list[a]]
        player_b = AGENTS[agent_list[b]]
    except (ValueError, IndexError):
        logger.error("Invalid selection. Exiting.")
        sys.exit(1)

    games, use_parallel = _prompt_settings()
    runner = TournamentRunner()

    logger.info(f"\nStarting 1v1: {player_a.name} vs {player_b.name}...")
    result = runner.run_matchup(player_a, player_b, games, parallel=use_parallel)
    ConsoleExporter.print_matchup_report(result)


def _run_championship() -> None:
    """Run a round-robin championship across all registered agents."""
    games, use_parallel = _prompt_settings()

    players = list(AGENTS.values())
    runner = TournamentRunner()

    logger.info("\nStarting Championship...")
    results = runner.run_championship(players, games, parallel=use_parallel)
    ConsoleExporter.print_championship_report(results["leaderboard"])


def _run_exit() -> None:
    """Exit the tournament CLI."""
    logger.info("Exiting.")
    sys.exit(0)


HANDLERS: dict[int, Callable[[], None]] = {
    1: _run_matchup,
    2: _run_championship,
    3: _run_exit,
}


def main() -> None:
    """CLI entry point for the Quarto tournament runner."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    display_menu()

    try:
        choice = int(input("Enter choice: ").strip())
        if choice not in HANDLERS:
            raise ValueError
    except ValueError:
        logger.error("Invalid choice. Exiting.")
        sys.exit(1)

    HANDLERS[choice]()


if __name__ == "__main__":
    main()
