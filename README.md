# Quarto-AI
Quarto-AI is a Python project implementing the **Quarto board game** engine, multiple AI players, command-line interfaces and more to come.

---
## Features
- Complete **game engine** with rules enforcement
- Multiple **player types**:
  - Human player (input using CLI)
  - Random AI (with basic winning-move detection)
  - Extensible base class to add new AIs
- **Game runner** to orchestrate matches between any players

---
## Installation
1. Clone the repository:
```bash
git clone https://github.com/sebastienfdz/Quarto-AI
cd Quarto-AI
```

2. Create and activate a virtual environment (Python 3.12+ recommended): 
```bash
# Windows
py -3.12 -m venv .venv
.\.venv\Scripts\activate 
# Linux / macOS
python3.12 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---
## Usage
- Run the main CLI interface:
```bash
python main.py
```

- You will be prompted to choose a game mode: 1. Human vs Human 2. Human vs RandomAI 3. RandomAI vs RandomAI

```bash
=== Quarto CLI ===
Select a game mode:
1. Human vs Human
2. Human vs RandomAI
3. RandomAI vs RandomAI
Enter your choice: _
```

---
## Project Structure
``` bash
quarto-ai/
│ 
├── quarto_ai/
│   ├── game/           # Core game engine (board, exceptions, piece, state)
│   ├── interfaces/     # CLI and (future) GUI interfaces
│   ├── players/        # Player base class + Human and AI implementations
│   │   └── ai/         # Different AI strategies (Random, Minimax, MCTS…)
│   └── runners/        # GameRunner orchestrating matches
│
├── main.py             # Code entrypoint
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---
## Roadmap
- [ ] Implement **Monte Carlo Tree Search** (MCTS) AI
- [ ] Implement **Minimax AI**
- [ ] Add **unittest** using pytest
- [ ] Add **GUI** for interactive play
- [ ] Add **Docker** to have a simple reproducible environment
- [ ] Add **tournament system** to rank AIs
