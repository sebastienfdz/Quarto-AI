# Quarto-AI

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/sebastienfdz/Quarto-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/sebastienfdz/Quarto-AI/actions/workflows/ci.yml)
[![Code Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen.svg)](https://github.com/sebastienfdz/Quarto-AI/actions)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checked: Mypy](https://img.shields.io/badge/type%20checker-mypy%20(strict)-blue.svg)](https://mypy-lang.org/)
[![Package Manager: uv](https://img.shields.io/badge/package%20manager-uv-DE5FE9.svg)](https://github.com/astral-sh/uv)

A Python implementation of the abstract strategy board game **Quarto**. This project features a robust game engine, multiple AI agent paradigms (Heuristic Random, Monte Carlo Tree Search, and Minimax with Alpha-Beta Pruning), and a parallel tournament framework with an order-invariant, convergent Elo rating system.

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

Run the interactive terminal interface to play against AI agents or watch them face each other:

```bash
uv run python main.py
```

Available modes include `Human vs Human`, `Human vs AI` (RandomAI, MCTS, Minimax), and `AI vs AI` matchups.

---

## Tournament & Benchmarking

The project provides two ways to benchmark agents: an interactive tournament CLI and an automated headless benchmarking script.

### 1. Interactive Tournament CLI
Run custom 1v1 matchups or round-robin championships with live progress feedback:

```bash
uv run python tournament.py
```

### 2. Automated Headless Benchmark
Run full round-robin tournaments across all configured agents with multiprocessing and export results directly to Markdown:

```bash
# Run standard benchmark (50 games per side per matchup)
uv run python -m scripts.benchmark --games 50

# Custom output path
uv run python -m scripts.benchmark --games 50 --output benchmarks/custom_report.md
```

---

## Benchmark Results (5,600 Games)

Below are the baseline championship results across 8 agents playing 100 games per side (200 games per matchup, 28 matchups, 5,600 total games) using multiprocessing. Ratings are computed via Iterative Batch Gradient Descent Elo.

### Championship Leaderboard

| Rank | Player | Elo | Wins | Draws | Losses | Win Rate |
|:----:|:-------|----:|-----:|------:|-------:|---------:|
| 1 | **MCTS-10000** | 1754 (+254) | 958 | 179 | 263 | **68.4%** |
| 2 | **Minimax-d3-AB** | 1750 (+250) | 920 | 242 | 238 | **65.7%** |
| 3 | **Minimax-d6-AB** | 1696 (+196) | 640 | 628 | 132 | **45.7%** |
| 4 | **Minimax-d5-AB** | 1631 (+131) | 648 | 389 | 363 | **46.3%** |
| 5 | **MCTS-1000** | 1581 (+81) | 683 | 152 | 565 | **48.8%** |
| 6 | **Minimax-d4-AB** | 1528 (+28) | 542 | 261 | 597 | **38.7%** |
| 7 | **MCTS-100** | 1143 (-357) | 210 | 26 | 1164 | **15.0%** |
| 8 | **RandomAI** | 914 (-586) | 59 | 3 | 1338 | **4.2%** |

### Key Findings & Insights
- **Top Performers**: `MCTS-10000` (1754 Elo) and `Minimax-d3-AB` (1750 Elo) lead the leaderboard with ~68% win rates against the field.
- **Defensive Robustness at Depth**: `Minimax-d6-AB` achieves the lowest loss rate of the entire tournament (**9.4% losses** across 1,400 games) and forces draws in 44.9% of games against top-tier opponents.
- **Starting-Player Advantage**: Analysis across all 5,600 games reveals an inherent advantage for the starter (**Player 1: 44.0% wins** vs **Player 2: 39.2% wins**, 16.8% draws).

📄 **[View Full Benchmark Report & Head-to-Head Cross Matrix](benchmarks/results.md)**

---

## Development & Testing

```bash
# Run the test suite with coverage report
uv run pytest --cov=quarto_ai

# Check types with mypy (strict mode)
uv run mypy .

# Lint and check formatting with ruff
uv run ruff check .
uv run ruff format --check .
```

### Docker

A lightweight multi-stage `Dockerfile` is provided for containerized execution across all modes:

```bash
# Build the image
docker build -t quarto-ai .

# 1. Interactive Play (default)
docker run -it --rm quarto-ai

# 2. Interactive Tournament CLI
docker run -it --rm quarto-ai tournament.py

# 3. Automated Benchmark
docker run -it --rm -v ./benchmarks:/app/benchmarks quarto-ai -m scripts.benchmark --games 10
```

---

## Implementation Details

- **Piece Representation**: Pieces are modeled as 4-bit integers (`height << 3 | color << 2 | shape << 1 | fill`). This allows line attribute checks to be computed in $O(1)$ per piece with bitwise operations.
- **State Machine**: The game loop is governed by a state machine alternating between `GamePhase.SELECTION` and `GamePhase.PLACEMENT`, validating actions against game rules with a custom exception hierarchy.
- **Player Interface**: All players implement the `BaseModel` abstract base class (`choose_position`, `choose_piece`), decoupling decision-making logic from the game runner.
- **Implemented Agents**:
  - `RandomAI`: Immediate winning-move detection with uniform random fallback for position and piece selection.
  - `MCTS`: Monte Carlo Tree Search using UCB1 for node selection and random rollout simulations.
  - `Minimax`: Adversarial search supporting optional Alpha-Beta pruning (`use_alpha_beta`), depth in plies (half turns), and dependency injection of heuristic evaluators (`BaseEvaluator`).
- **Heuristic Evaluator (`SimpleEvaluator`)**: Evaluates alive-line threat density (scoring 2- and 3-piece lines that can still achieve Quarto) from Player 1's perspective.
- **Convergent Elo Rating System (`EloSystem`)**: Employs an Iterative Batch Gradient Descent algorithm with win-rate normalization ($K=8.0$) to guarantee order-invariance, numerical stability across large game volumes, and zero-sum conservation.
- **Concurrency**: The tournament runner executes games in parallel across worker processes using Python's `ProcessPoolExecutor` to accelerate large tournament runs.

---

## Project Structure

```text
Quarto-AI/
├── benchmarks/             # Benchmark reports and canonical results
│   └── results.md          # 5,600-game official baseline report
├── quarto_ai/
│   ├── game/               # Core engine (board, piece, state machine, exceptions)
│   ├── interfaces/         # CLI user interface
│   ├── players/            # Player base class and implementations
│   │   ├── ai/             # AI implementations (RandomAI, MCTS, Minimax)
│   │   │   └── minimax/    # Minimax search and heuristic evaluators
│   │   ├── base.py         # BaseModel ABC
│   │   └── human.py        # CLI-based human player
│   └── runners/            # Game runner, tournament runner, Elo system, exporters
│       ├── elo.py          # Iterative Batch Elo rating system
│       ├── exporter.py     # Console & Markdown report exporters
│       ├── game_runner.py  # Single-match orchestrator
│       └── tournament_runner.py # Parallel round-robin tournament engine
├── scripts/
│   └── benchmark.py        # Automated benchmark CLI
├── tests/                  # Pytest test suite (100% passing, 93%+ coverage)
├── main.py                 # Interactive game entrypoint
├── tournament.py           # Interactive tournament entrypoint
├── Dockerfile              # Container definition
└── pyproject.toml          # Tooling configuration (Ruff, Mypy, Pytest)
```

---

## Future Considerations

- **`AdvancedEvaluator`**: Enhanced heuristic evaluator accounting for piece pool danger and piece-gifting safety in addition to board threats.
- **Performance Profiling**: Bottleneck profiling (`cProfile`) for deep Minimax and large MCTS search trees.
- **MCTS Tree Reuse**: Retain and re-root the search tree across successive turns to maximize simulation efficiency.
