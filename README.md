# Quarto-AI

[![CI](https://github.com/sebastienfdz/Quarto-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/sebastienfdz/Quarto-AI/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checked: Mypy](https://img.shields.io/badge/type%20checker-mypy%20(strict)-blue.svg)](https://mypy-lang.org/)
[![Package Manager: uv](https://img.shields.io/badge/package%20manager-uv-DE5FE9.svg)](https://github.com/astral-sh/uv)

A Python implementation of the abstract strategy board game **Quarto**. This project includes a complete game engine, multiple player types (Human CLI, Heuristic Random, and Monte Carlo Tree Search), and a parallel tournament runner to benchmark agent performance.

---

## Game Overview

**Quarto** is a two-player game played on a 4×4 board with 16 unique pieces. Each piece has four binary attributes:
- **Height**: Tall / Short
- **Color**: Dark / Light
- **Shape**: Square / Circular
- **Fill**: Solid / Hollow

### Core Rules

1. **Turn Structure**: Players do not choose the piece they place. Instead, each turn is split into two steps:
   - Place the piece handed to you by your opponent on an empty square.
   - Choose an available piece from the pool and hand it to your opponent.
2. **Win Condition**: The first player to align 4 pieces that share at least one common attribute (along any row, column, or diagonal) wins.
3. **Draw**: If all 16 squares are filled without an alignment, the game ends in a draw.

---

## Quickstart

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended)

### 1. Installation

```bash
git clone https://github.com/sebastienfdz/Quarto-AI.git
cd Quarto-AI

# Install dependencies and dev tools
uv sync --all-extras
```

### 2. Interactive Play (CLI)

Run the main script to start a game in your terminal:

```bash
uv run python main.py
```

Available game modes:
1. `Human vs Human`
2. `Human vs RandomAI`
3. `Human vs MCTS`
4. `RandomAI vs RandomAI`
5. `RandomAI vs MCTS`
6. `MCTS vs MCTS`

---

## Tournament & Benchmarking

The project includes a tournament runner that uses Python's `ProcessPoolExecutor` to run games in parallel across CPU cores.

```bash
uv run python tournament.py
```

You can run direct 1v1 matchups with configurable simulation counts or a round-robin championship between multiple players.

### Sample Matchup Output

```text
==================================================
MATCHUP REPORT: RandomAI vs MCTS-1000
==================================================
Total Games: 100
RandomAI Wins: 4 (4.0%)
MCTS-1000 Wins: 94 (94.0%)
Draws: 2 (2.0%)
--------------------------------------------------
Starting Bias Analysis:
Player 0 (Starter) Wins:  48 (48.0%)
Player 1 (Follower) Wins: 50 (50.0%)
Draws:                     2 (2.0%)
==================================================
```

---

## Development & Testing

```bash
# Run the test suite
uv run pytest

# Check types with mypy
uv run mypy .

# Lint and check formatting with ruff
uv run ruff check .
uv run ruff format --check .
```

### Docker

A multi-stage `Dockerfile` is provided for containerized execution:

```bash
docker build -t quarto-ai .
docker run -it --rm quarto-ai
```

---

## Implementation Details

- **Piece Representation**: Pieces are modeled as 4-bit integers (`height << 3 | color << 2 | shape << 1 | fill`). This allows attribute checks across lines to be calculated with bitwise operations.
- **State Machine**: The game loop is governed by a state machine that alternates between `GamePhase.SELECTION` and `GamePhase.PLACEMENT`, validating actions against game rules and custom exceptions.
- **Player Interface**: All players implement the `BaseModel` abstract base class (`choose_position`, `choose_piece`), decoupling decision-making logic from the game runner.
- **Implemented Agents**:
  - `RandomAI`: Selects an immediate winning move if available; otherwise plays and chooses randomly.
  - `MCTS`: Monte Carlo Tree Search using UCB1 for node selection and random rollouts for simulation.
- **Concurrency**: The tournament runner schedules games across worker processes to avoid Python's Global Interpreter Lock (GIL) during CPU-bound rollouts.

---

## Project Structure

```text
Quarto-AI/
├── quarto_ai/
│   ├── game/               # Core engine (board, piece, state machine, exceptions)
│   ├── interfaces/         # CLI user interface
│   ├── players/            # Player base class and implementations
│   │   ├── ai/             # AI implementations (RandomAI, MCTS)
│   │   ├── base.py         # BaseModel ABC
│   │   └── human.py        # CLI-based human player
│   └── runners/            # Game runner and parallel tournament runner
├── tests/                  # Pytest test suite
├── main.py                 # Interactive game entrypoint
├── tournament.py           # Tournament benchmarking entrypoint
├── Dockerfile              # Container definition
└── pyproject.toml          # Tooling configuration (Ruff, Mypy, Pytest)
```

---

## Planned Improvements

- **Minimax with Alpha-Beta Pruning**: Add an adversarial tree search agent with heuristic state evaluation.
- **MCTS Tree Reuse**: Retain and re-root the search tree across successive turns to improve move quality without increasing simulation budgets.
- **Elo Rating Calculation**: Track relative player ratings across tournament championships.
- **Architectural Decision Records (ADRs)**: Document key technical choices in `docs/decisions/` (bitwise representation, concurrency model, search algorithms).

