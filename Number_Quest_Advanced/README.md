# Number Quest — Advanced Python Mini Project 02

A polished number guessing game built with **Python + Tkinter**. It uses only the Python standard library; no `pip install` is required.

## Features

- Attractive desktop GUI with **dark and light themes**
- Easy, Medium and Hard difficulty levels (10, 7 and 5 attempts)
- Custom minimum and maximum number range (negative ranges are supported)
- Live round timer
- Score calculation using difficulty, attempts remaining, speed and hint use
- One even/odd hint per round
- Duplicate guesses do not consume an attempt
- Input validation and clear feedback
- Persistent top-five leaderboard and lifetime statistics saved to `game_data.json`
- Keyboard support: `Enter` to guess, `Ctrl+N` for a new round, `Ctrl+T` to switch theme
- Keeps the latest 100 game records in the local JSON file

## Requirements

- Python 3.10 or later recommended
- Tkinter (included with most Windows Python installations)

No third-party packages are required.

## Run on Windows / VS Code

1. Extract the project ZIP.
2. Open the `Number_Quest_Advanced` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Run:

   ```powershell
   python number_guessing.py
   ```

   Or double-click `run_game.bat` in File Explorer.

## How to play

1. Enter a player name.
2. Choose Easy, Medium or Hard.
3. Enter the minimum and maximum values for the secret-number range.
4. Click **Start New Game**.
5. Enter a whole number and click **Guess** (or press Enter).
6. Use one optional even/odd hint, or start a new round at any time.

A win is scored using a difficulty bonus, remaining attempts and a speed bonus. Using a hint deducts points. A lost round is recorded with zero points.

## Saved data

The game creates `game_data.json` beside the Python files after the first completed round. It contains local leaderboard entries and statistics. It is intentionally excluded from Git so personal scores are not uploaded accidentally.

## Project structure

```text
Number_Quest_Advanced/
├── number_guessing.py   # Tkinter graphical user interface
├── game_engine.py       # Game rules, timer, hints and scoring
├── storage.py           # JSON leaderboard and statistics
├── run_game.bat         # Windows launcher
├── requirements.txt     # No external dependencies
├── .gitignore           # Excludes local game data and Python cache
└── README.md
```

## Learning concepts

Functions, classes, dataclasses, random numbers, conditionals, loops, exception handling, Tkinter widgets and events, JSON file handling, sorting, and `time.perf_counter()`.
