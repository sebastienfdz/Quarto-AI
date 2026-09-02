import argparse
import datetime
import logging
import time

from quarto_ai.players.ai.mcts import MCTS
from quarto_ai.players.ai.minimax.evaluator import SimpleEvaluator
from quarto_ai.players.ai.minimax.minimax import Minimax
from quarto_ai.players.ai.random_ai import RandomAI
from quarto_ai.runners.exporter import MarkdownExporter
from quarto_ai.runners.tournament_runner import TournamentRunner

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("quarto_ai.benchmark")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Quarto AI benchmark.")
    parser.add_argument(
        "--games",
        type=int,
        default=2,
        help="Number of games per side for each matchup.",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Run games in parallel.",
    )
    parser.add_argument(
        "--no-parallel",
        action="store_false",
        dest="parallel",
        help="Disable parallel execution.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom path to save the report (defaults to benchmarks/benchmark_{games}games_YYYYMMDD_HHMMSS.md).",
    )
    args = parser.parse_args()

    players = [
        RandomAI("RandomAI"),
        MCTS(simulations=100, name="MCTS-100"),
        MCTS(simulations=1000, name="MCTS-1000"),
        # MCTS(simulations=10000, name="MCTS-10000"),
        Minimax(evaluator=SimpleEvaluator(), depth=3, use_alpha_beta=True, name="Minimax-d3-AB"),
        Minimax(evaluator=SimpleEvaluator(), depth=4, use_alpha_beta=True, name="Minimax-d4-AB"),
        Minimax(evaluator=SimpleEvaluator(), depth=5, use_alpha_beta=True, name="Minimax-d5-AB"),
        # Minimax(evaluator=SimpleEvaluator(), depth=6, use_alpha_beta=True, name="Minimax-d6-AB"),
    ]

    logger.info("=" * 60)
    logger.info("QUARTO AI BENCHMARK SCRIPT")
    logger.info("=" * 60)
    logger.info(f"Games per side: {args.games}")
    logger.info(f"Parallel: {args.parallel}")
    logger.info(f"Players: {[p.name for p in players]}")
    logger.info("=" * 60)

    start_time = time.perf_counter()
    runner = TournamentRunner()
    results = runner.run_championship(players, args.games, parallel=args.parallel)
    elapsed = time.perf_counter() - start_time

    methodology = (
        f"- **Games per side**: {args.games}\n"
        f"- **Total Matchups**: {len(results['matchups'])}\n"
        f"- **Total Games Played**: {sum(m['total_games'] for m in results['matchups'])}\n"
        f"- **Execution Time**: {datetime.timedelta(seconds=int(elapsed))}\n"
        f"- **Execution Mode**: {'Parallel (Multiprocessing)' if args.parallel else 'Sequential'}\n"
        f"- **Agents**: {', '.join([p.name for p in players])}"
    )

    output_path = (
        args.output
        or f"benchmarks/benchmark_{args.games}games_{datetime.datetime.now():%Y%m%d_%H%M%S}.md"
    )
    MarkdownExporter.generate_report(results, output_path, methodology=methodology)


if __name__ == "__main__":
    main()
