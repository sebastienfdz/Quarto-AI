import logging
import sys

from quarto_ai.players.ai.mcts import MCTS
from quarto_ai.players.ai.random_ai import RandomAI
from quarto_ai.runners.tournament_runner import TournamentRunner

logger = logging.getLogger("quarto_ai.tournament")


def _handle_matchup_menu(runner: TournamentRunner) -> None:
    """Handles user input and execution for the 1v1 matchup mode."""
    try:
        sims = int(input("Enter MCTS simulations (default: 100): ").strip() or "100")
        games = int(input("Enter games per side (default: 50): ").strip() or "50")
        use_parallel = input("Use parallel processing? (Y/n): ").strip().lower() != "n"
    except ValueError:
        logger.error("Invalid inputs. Exiting.")
        sys.exit(1)

    logger.info("\nStarting matchup...")
    p1 = RandomAI("RandomAI")
    p2 = MCTS(simulations=sims, name=f"MCTS-{sims}")

    results = runner.run_matchup(p1, p2, games, parallel=use_parallel)
    runner.print_matchup_report(results)


def _handle_championship_menu(runner: TournamentRunner) -> None:
    """Handles user input and execution for the Round-Robin championship mode."""
    try:
        games = int(input("Enter games per matchup side (default: 10): ").strip() or "10")
        use_parallel = input("Use parallel processing? (Y/n): ").strip().lower() != "n"
    except ValueError:
        logger.error("Invalid input. Exiting.")
        sys.exit(1)

    logger.info("\nStarting championship...")
    p1 = RandomAI("RandomAI")
    p2 = MCTS(simulations=100, name="MCTS-100")
    p3 = MCTS(simulations=1000, name="MCTS-1000")
    players = [p1, p2, p3]

    leaderboard = runner.run_championship(players, games, parallel=use_parallel)
    runner.print_championship_report(leaderboard)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("quarto_ai.tournament").setLevel(logging.INFO)

    logger.info("=== Quarto Tournament CLI ===")
    logger.info("Select an option:")
    logger.info("1. 1v1 Matchup (RandomAI vs MCTS)")
    logger.info("2. Championship (RandomAI vs MCTS-100 vs MCTS-1000)")
    logger.info("3. Exit")

    try:
        choice = int(input("Enter choice: ").strip())
    except (ValueError, IndexError):
        logger.error("Invalid choice. Exiting.")
        sys.exit(1)

    runner = TournamentRunner()

    if choice == 1:
        _handle_matchup_menu(runner)
    elif choice == 2:
        _handle_championship_menu(runner)
    else:
        logger.info("Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
