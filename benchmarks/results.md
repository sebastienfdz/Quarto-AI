# Quarto AI Benchmark Results

*Generated on: September 01, 2026*

## Methodology

- **Games per side**: 100
- **Total Matchups**: 28
- **Total Games Played**: 5600
- **Execution Time**: 2:21:53
- **Execution Mode**: Parallel (Multiprocessing)
- **Agents**: RandomAI, MCTS-100, MCTS-1000, MCTS-10000, Minimax-d3-AB, Minimax-d4-AB, Minimax-d5-AB, Minimax-d6-AB

## Championship Leaderboard

| Rank | Player | Elo | Wins | Draws | Losses |
|:----:|:-------|----:|-----:|------:|-------:|
| 1 | **MCTS-10000** | 1754 (+254) | 958 (68.4%) | 179 (12.8%) | 263 (18.8%) |
| 2 | **Minimax-d3-AB** | 1750 (+250) | 920 (65.7%) | 242 (17.3%) | 238 (17.0%) |
| 3 | **Minimax-d6-AB** | 1696 (+196) | 640 (45.7%) | 628 (44.9%) | 132 (9.4%) |
| 4 | **Minimax-d5-AB** | 1631 (+131) | 648 (46.3%) | 389 (27.8%) | 363 (25.9%) |
| 5 | **MCTS-1000** | 1581 (+81) | 683 (48.8%) | 152 (10.9%) | 565 (40.4%) |
| 6 | **Minimax-d4-AB** | 1528 (+28) | 542 (38.7%) | 261 (18.6%) | 597 (42.6%) |
| 7 | **MCTS-100** | 1143 (-357) | 210 (15.0%) | 26 (1.9%) | 1164 (83.1%) |
| 8 | **RandomAI** | 914 (-586) | 59 (4.2%) | 3 (0.2%) | 1338 (95.6%) |

## Head-to-Head Win Rate Matrix

*(Row player's win rate against Column player)*

| Player | MCTS-100 | MCTS-1000 | MCTS-10000 | Minimax-d3-AB | Minimax-d4-AB | Minimax-d5-AB | Minimax-d6-AB | RandomAI |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| **MCTS-100** | - | 10.0% | 6.5% | 4.5% | 2.5% | 4.5% | 3.0% | 74.0% |
| **MCTS-1000** | 88.5% | - | 21.5% | 44.0% | 38.0% | 29.5% | 21.0% | 99.0% |
| **MCTS-10000** | 92.5% | 71.0% | - | 70.5% | 57.0% | 47.0% | 41.0% | 100.0% |
| **Minimax-d3-AB** | 95.0% | 47.0% | 18.0% | - | 100.0% | 100.0% | 0.0% | 100.0% |
| **Minimax-d4-AB** | 96.0% | 50.0% | 26.0% | 0.0% | - | 0.0% | 0.0% | 99.0% |
| **Minimax-d5-AB** | 93.0% | 52.0% | 31.0% | 0.0% | 50.0% | - | 0.0% | 98.0% |
| **Minimax-d6-AB** | 91.0% | 51.5% | 28.5% | 0.0% | 50.0% | 0.0% | - | 99.0% |
| **RandomAI** | 26.0% | 1.0% | 0.0% | 0.0% | 1.0% | 0.5% | 1.0% | - |

## Head-to-Head Matchups

| Matchup | Games Played | Player A Wins | Player B Wins | Draws |
|:--------|:------------:|:-------------:|:-------------:|:-----:|
| RandomAI vs MCTS-100 | 200 | 52 (26.0%) | 148 (74.0%) | 0 (0.0%) |
| RandomAI vs MCTS-1000 | 200 | 2 (1.0%) | 198 (99.0%) | 0 (0.0%) |
| RandomAI vs MCTS-10000 | 200 | 0 (0.0%) | 200 (100.0%) | 0 (0.0%) |
| RandomAI vs Minimax-d3-AB | 200 | 0 (0.0%) | 200 (100.0%) | 0 (0.0%) |
| RandomAI vs Minimax-d4-AB | 200 | 2 (1.0%) | 198 (99.0%) | 0 (0.0%) |
| RandomAI vs Minimax-d5-AB | 200 | 1 (0.5%) | 196 (98.0%) | 3 (1.5%) |
| RandomAI vs Minimax-d6-AB | 200 | 2 (1.0%) | 198 (99.0%) | 0 (0.0%) |
| MCTS-100 vs MCTS-1000 | 200 | 20 (10.0%) | 177 (88.5%) | 3 (1.5%) |
| MCTS-100 vs MCTS-10000 | 200 | 13 (6.5%) | 185 (92.5%) | 2 (1.0%) |
| MCTS-100 vs Minimax-d3-AB | 200 | 9 (4.5%) | 190 (95.0%) | 1 (0.5%) |
| MCTS-100 vs Minimax-d4-AB | 200 | 5 (2.5%) | 192 (96.0%) | 3 (1.5%) |
| MCTS-100 vs Minimax-d5-AB | 200 | 9 (4.5%) | 186 (93.0%) | 5 (2.5%) |
| MCTS-100 vs Minimax-d6-AB | 200 | 6 (3.0%) | 182 (91.0%) | 12 (6.0%) |
| MCTS-1000 vs MCTS-10000 | 200 | 43 (21.5%) | 142 (71.0%) | 15 (7.5%) |
| MCTS-1000 vs Minimax-d3-AB | 200 | 88 (44.0%) | 94 (47.0%) | 18 (9.0%) |
| MCTS-1000 vs Minimax-d4-AB | 200 | 76 (38.0%) | 100 (50.0%) | 24 (12.0%) |
| MCTS-1000 vs Minimax-d5-AB | 200 | 59 (29.5%) | 104 (52.0%) | 37 (18.5%) |
| MCTS-1000 vs Minimax-d6-AB | 200 | 42 (21.0%) | 103 (51.5%) | 55 (27.5%) |
| MCTS-10000 vs Minimax-d3-AB | 200 | 141 (70.5%) | 36 (18.0%) | 23 (11.5%) |
| MCTS-10000 vs Minimax-d4-AB | 200 | 114 (57.0%) | 52 (26.0%) | 34 (17.0%) |
| MCTS-10000 vs Minimax-d5-AB | 200 | 94 (47.0%) | 62 (31.0%) | 44 (22.0%) |
| MCTS-10000 vs Minimax-d6-AB | 200 | 82 (41.0%) | 57 (28.5%) | 61 (30.5%) |
| Minimax-d3-AB vs Minimax-d4-AB | 200 | 200 (100.0%) | 0 (0.0%) | 0 (0.0%) |
| Minimax-d3-AB vs Minimax-d5-AB | 200 | 200 (100.0%) | 0 (0.0%) | 0 (0.0%) |
| Minimax-d3-AB vs Minimax-d6-AB | 200 | 0 (0.0%) | 0 (0.0%) | 200 (100.0%) |
| Minimax-d4-AB vs Minimax-d5-AB | 200 | 0 (0.0%) | 100 (50.0%) | 100 (50.0%) |
| Minimax-d4-AB vs Minimax-d6-AB | 200 | 0 (0.0%) | 100 (50.0%) | 100 (50.0%) |
| Minimax-d5-AB vs Minimax-d6-AB | 200 | 0 (0.0%) | 0 (0.0%) | 200 (100.0%) |

## Starting-Player Bias Analysis

| Role | Total Wins | Global Win Rate |
|:-----|-----------:|----------------:|
| Player 1 (Starter) | 2465 | 44.0% |
| Player 2 (Follower) | 2195 | 39.2% |
| Draws | 940 | 16.8% |
