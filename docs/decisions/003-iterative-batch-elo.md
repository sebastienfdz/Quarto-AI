# ADR-003 — Iterative Batch Elo for Tournament Rating

- **Date:** 2026-09
- **Status:** Accepted

---

## Context and Problem Statement

Evaluating AI agents in a round-robin tournament requires an Elo system that fairly reflects relative skill across all agents simultaneously. Sequential Elo updates ($K = 32$, applied after each matchup) produced two pathologies during the baseline benchmark (5,600 games, 8 agents, 200 games per matchup):

1. **Match-order bias**: `Minimax-d6-AB` won 194/200 games against a `RandomAI` whose rating had already collapsed to ~300 Elo. Because the formula expected a near-perfect win rate, it *lost* Elo — ending at **-110 Elo** despite a 90.6% non-loss rate.
2. **Batch scale explosion**: Applying $K = 32$ directly to 200-game cumulative win counts produced extreme rating swings, pushing agents above 3000 or below 0.

Note: unlike human players whose skill drifts over time, AI agents have a fixed deterministic level throughout the entire benchmark. Post-tournament batch computation is therefore valid — there is no "stale rating" problem.

---

## Decision

We replace sequential updates with an **Iterative Batch Gradient Descent Elo** system.

Rating deltas are accumulated across all matchups in each epoch before any rating changes:

$$\Delta_{AB} = K \cdot \left(\frac{W_A + 0.5 \cdot D}{N} - E(R_A, R_B)\right), \quad E(R_A, R_B) = \frac{1}{1 + 10^{(R_B - R_A)/400}}$$

where $W_A$ = Player A wins, $D$ = draws, $N$ = total games, $K = 8.0$. All ratings update simultaneously at the end of each epoch. The algorithm stops when the maximum per-epoch delta falls below `CONVERGENCE_THRESHOLD = 0.01`, with a safety cap of `MAX_EPOCHS = 1000`.

Normalising by $N$ bounds each matchup's contribution to $[-K, +K]$ regardless of game volume.

---

## Consequences

- Ratings are order-invariant because no rating changes mid-epoch — all deltas are accumulated before any update is applied.
- Every delta added to Player A is subtracted from Player B: the total Elo in the system is exactly conserved ($\sum R_i = N \times 1500$).
- Decoupling match execution from rating computation means `EloSystem.calculate_ratings()` is a pure, stateless function easy to test in isolation.
- **Trade-off**: Ratings can only be computed once all matchups are complete — intermediate standings are not available.
