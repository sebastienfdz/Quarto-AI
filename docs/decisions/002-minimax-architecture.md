# ADR-002 — Minimax: Ply-Based Depth and Heuristic Evaluation

- **Date:** 2026-08
- **Status:** Accepted

---

## Context and Problem Statement

Implementing adversarial search for Quarto raised two design questions:

1. **Depth metric**: Quarto's two-phase turn creates an irregular branching factor if depth is counted in full turns (up to $16 \times 15 = 240$ at turn 1, and boundary turns such as Turn 0 — where only a piece is gifted, no placement occurs — require special-casing in the search logic). Counting depth in atomic half-turns (plies) keeps the branching factor at most 16 per node and eliminates boundary exceptions.
2. **Evaluation perspective**: Because the active player places *for themselves* then gifts *to their opponent*, the notion of "current player" changes mid-turn. Using a relative (active-player) perspective causes sign inversions during Minimax backtracking.

---

## Decision

**Ply-based depth**: Each ply is one atomic phase — either a placement or a selection. Depth 3 means "look 3 actions ahead" (e.g. place, select, place), regardless of how they map onto full turns.

**Absolute evaluation (Player 1 standard)**: `BaseEvaluator.evaluate(state)` always returns a score from Player 1's perspective: `+math.inf` for a Player 1 win, `-math.inf` for a loss, `0.0` for a draw. Minimax maximises on Player 1's placement turns and minimises on Player 2's, without the evaluator needing to know who is maximising.

**`SimpleEvaluator`**: Non-terminal states are scored by counting *alive lines* — lines where placed pieces still share at least one attribute and a Quarto is still achievable:

$$\text{Score} = \text{sign} \cdot (w_3 \cdot L_3 + w_2 \cdot L_2)$$

where $L_k$ = alive lines with exactly $k$ pieces, $w_3 = 5.0$, $w_2 = 1.0$, and $\text{sign}$ is $+1.0$ if Player 1 is placing or $-1.0$ if Player 2 is placing.

**Dependency injection**: `Minimax` accepts any `BaseEvaluator` at construction time, so heuristics can be swapped or benchmarked without modifying the search algorithm.

---

## Consequences

- Uniform ply-based depth makes search cost predictable and controllable, with no special cases for boundary turns.
- Absolute-perspective evaluation eliminates mid-turn sign-oscillation bugs.
- Swapping heuristics (e.g. for a future `AdvancedEvaluator`) requires only passing a different evaluator instance at construction — no changes to the search algorithm.
- **Trade-off**: Positions evaluated at depth cutoffs can be in either phase depending on the starting phase and depth parity — evaluators must handle both `PLACEMENT` and `SELECTION` states.
