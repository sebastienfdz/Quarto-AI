import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quarto_ai.runners.tournament_runner import LeaderboardEntry, MatchupResult

logger = logging.getLogger("quarto_ai.exporter")


class ConsoleExporter:
    """Exports tournament results to the standard console logger."""

    @staticmethod
    def print_matchup_report(results: "MatchupResult") -> None:
        """Logs a formatted summary of a 1v1 matchup."""
        total = results["total_games"]
        a_pct = (results["a_wins"] / total) * 100 if total > 0 else 0
        b_pct = (results["b_wins"] / total) * 100 if total > 0 else 0
        draw_pct = (results["draws"] / total) * 100 if total > 0 else 0

        starter_pct = (results["starter_wins"] / total) * 100 if total > 0 else 0
        follower_pct = (results["follower_wins"] / total) * 100 if total > 0 else 0

        logger.info("\n" + "=" * 50)
        logger.info(f"MATCHUP REPORT: {results['player_a_name']} vs {results['player_b_name']}")
        logger.info("=" * 50)
        logger.info(f"Total Games: {total}")
        logger.info(f"{results['player_a_name']} Wins: {results['a_wins']} ({a_pct:.1f}%)")
        logger.info(f"{results['player_b_name']} Wins: {results['b_wins']} ({b_pct:.1f}%)")
        logger.info(f"Draws: {results['draws']} ({draw_pct:.1f}%)")
        logger.info("-" * 50)
        logger.info("Starting Bias Analysis:")
        logger.info(f"Player 0 (Starter) Wins:  {results['starter_wins']} ({starter_pct:.1f}%)")
        logger.info(f"Player 1 (Follower) Wins: {results['follower_wins']} ({follower_pct:.1f}%)")
        logger.info(f"Draws:                     {results['draws']} ({draw_pct:.1f}%)")
        logger.info("=" * 50 + "\n")

    @staticmethod
    def print_championship_report(leaderboard: list["LeaderboardEntry"]) -> None:
        """Logs a formatted leaderboard table for a championship."""
        logger.info("\n" + "=" * 70)
        logger.info("CHAMPIONSHIP LEADERBOARD")
        logger.info("=" * 70)
        logger.info(
            f"{'Rank':<5} | {'Player':<20} | {'Elo':<6} | {'Points':<8} | "
            f"{'Wins':<6} | {'Draws':<6} | {'Losses':<6} | {'Win Rate':<8}"
        )
        logger.info("-" * 70)

        for rank, entry in enumerate(leaderboard, 1):
            total = entry["total_games"]
            win_rate = (entry["wins"] / total) * 100 if total > 0 else 0.0

            logger.info(
                f"{rank:<5} | {entry['player'].name:<20} | {int(entry['elo']):<6} | "
                f"{entry['points']:<8} | {entry['wins']:<6} | {entry['draws']:<6} | "
                f"{entry['losses']:<6} | {win_rate:.1f}%"
            )
        logger.info("=" * 70 + "\n")
