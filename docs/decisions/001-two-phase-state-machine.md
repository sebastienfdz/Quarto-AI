# ADR-001 — Two-Phase State Machine for Quarto's Turn Lifecycle

- **Date:** 2026-08
- **Status:** Accepted

---

## Context and Problem Statement

In Quarto, a turn consists of two actions: placing the piece received from the opponent, then selecting and handing an available piece.
Two boundary turns are asymmetric: Turn 0 has no placement (only a selection) and Turn 16 has no selection after the final placement.

The question was how to enforce this lifecycle at the engine level without relying on callers to sequence actions correctly.

---

## Decision

The game lifecycle is modelled as a **Two-Phase Finite State Machine** (`GamePhase.PLACEMENT` and `GamePhase.SELECTION`).
`GameState` validates each action against the active phase, raising `InvalidPhaseError` on violations.
`BaseModel` exposes two distinct methods — `choose_position` and `choose_piece` — allowing players to reason about one action at a time.
Turn 0 and Turn 16 are handled as explicit state transitions with no special-casing in player code.

This also limits the branching factor per ply to at most 16 (positions or pieces), compared to $16 \times 15 = 240$ for a composite-move approach.

---

## Consequences

- Phase violations and illegal moves are caught at the engine boundary — AI and UI code cannot produce invalid game states.
- Each ply has a uniform branching factor of at most 16, reducing the search space for MCTS and Minimax at every depth.
- A full turn requires two method calls and two state transitions instead of one atomic action.
