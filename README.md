# Dynamic Dots and Boxes

Dynamic Dots and Boxes is a Python game built using Pygame. In this game, players (the user and the AI) compete to capture boxes by drawing lines between dots. Capturing a box awards a power token that can be used for special power-ups, such as extra moves, line reversal, or swapping tokens.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Running the Game](#running-the-game)
- [Game Instructions](#game-instructions)
- [AI Algorithms](#ai-algorithms)
- [Project Structure](#project-structure)

## Features

- Two-player game: user vs. AI.
- Power-ups system:
  - **Extra Move**: Allows you to keep your turn.
  - **Line Reversal**: Undo the opponent's last move.
  - **Swap Token**: Exchange your token for a random line.
- AI that uses either Minimax or Alpha-Beta pruning algorithms.
- Menu selection for difficulty, grid size, and AI algorithm.

## Setup

1. **Prerequisites:**

   - Python 3.7 or later
   - Pygame library

2. **Install Pygame:**

   Open a terminal and run:

   ```bash
   pip install pygame
   ```

3. **Clone or Download the Repository:**

   Navigate to the desired directory on your machine and run:

   ```bash
   git clone https://github.com/yourusername/dynamic-dots-and-boxes.git
   ```

   Or download the ZIP and extract it.

## Running the Game

From the project directory, run the following command in your terminal:

```bash
python main.py
```

The game window will open, and you will be presented with the main menu to choose the difficulty level.

## Game Instructions

1. **Main Menu:**

   - Select the **Difficulty** (Easy, Medium, Hard). The difficulty affects the AI search depth and the chance to use power-ups.
   - Choose a **Grid Size** (predefined or custom input from 3 to 20).
   - The AI algorithm is also chosen here (Minimax for Easy, Alpha-Beta for Medium/Hard – or if you select a different option in the algorithm menu if implemented).

2. **Gameplay:**

   - The game board is displayed with a grid of dots.
   - Draw a line between two adjacent dots by clicking on the grid.
   - Completing a box (all four sides) awards you (or the AI) a power token.
   - **Power-up rules:** Once a token is used in a turn, no new token is awarded for additional boxes until the opponent completes a turn.
   - Use power-ups by clicking the corresponding buttons on the left panel.

3. **Special Power-ups:**

   - **Extra Move:** Continue your turn even after capturing a box.
   - **Line Reversal:** Remove the last move made by your opponent.
   - **Swap Token:** Exchange your token for a random move on the grid.

4. **End Game:**
   - The game ends when all possible lines have been drawn.
   - The player with the most boxes wins.
   - An end-game menu will display the result and offer options to play again, return to the main menu, or quit.

## AI Algorithms

The AI can use one of two algorithms:

- **Minimax:** A basic decision-making algorithm.
- **Alpha-Beta Pruning:** An optimized version of Minimax that prunes branches to reduce computation time.

At the start of the game, you can choose which algorithm the AI will use.

## Project Structure

```
dynamic-dots-and-boxes/
├── alpha_beta_pruning.py   # Contains the alpha-beta pruning function
├── constants.py            # Constants definitions (colors, player enum, etc.)
├── logic.py                # Game logic for Dots and Boxes
├── main.py                 # Contains the main game loop and menus
├── minimax.py              # Contains the minimax algorithm implementation
└── README.md               # This file
```

Enjoy playing Dynamic Dots and Boxes!
