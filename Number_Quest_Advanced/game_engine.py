"""Core rules for Number Quest. This module does not depend on Tkinter."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field


DIFFICULTY_ATTEMPTS = {
    "Easy": 10,
    "Medium": 7,
    "Hard": 5,
}

DIFFICULTY_BONUS = {
    "Easy": 40,
    "Medium": 80,
    "Hard": 120,
}


@dataclass
class GuessResult:
    status: str
    attempts_left: int
    message: str


@dataclass
class GameRound:
    minimum: int
    maximum: int
    difficulty: str
    player_name: str
    secret_number: int = field(init=False)
    max_attempts: int = field(init=False)
    attempts_left: int = field(init=False)
    guesses: list[int] = field(default_factory=list)
    hints_used: int = 0
    ended: bool = False
    won: bool = False
    _started_at: float = field(default_factory=time.perf_counter, init=False)
    _ended_at: float | None = None

    def __post_init__(self) -> None:
        if self.difficulty not in DIFFICULTY_ATTEMPTS:
            raise ValueError("Choose Easy, Medium or Hard difficulty.")
        if self.maximum <= self.minimum:
            raise ValueError("The maximum number must be greater than the minimum.")
        self.secret_number = random.randint(self.minimum, self.maximum)
        self.max_attempts = DIFFICULTY_ATTEMPTS[self.difficulty]
        self.attempts_left = self.max_attempts

    @property
    def elapsed_seconds(self) -> float:
        end = self._ended_at if self._ended_at is not None else time.perf_counter()
        return max(0.0, end - self._started_at)

    @property
    def attempts_used(self) -> int:
        return len(self.guesses)

    def submit_guess(self, guess: int) -> GuessResult:
        if self.ended:
            return GuessResult("finished", self.attempts_left, "This round has finished. Start a new round!")
        if not self.minimum <= guess <= self.maximum:
            return GuessResult("out_of_range", self.attempts_left,
                               f"Enter a number from {self.minimum} to {self.maximum}.")
        if guess in self.guesses:
            return GuessResult("duplicate", self.attempts_left,
                               "You already tried that number. Choose a different number.")

        self.guesses.append(guess)
        self.attempts_left -= 1

        if guess == self.secret_number:
            self.won = True
            self._finish()
            return GuessResult("correct", self.attempts_left, "Correct! You found the secret number!")

        if self.attempts_left == 0:
            self.won = False
            self._finish()
            return GuessResult("lost", self.attempts_left,
                               f"No attempts left. The secret number was {self.secret_number}.")

        if guess < self.secret_number:
            return GuessResult("low", self.attempts_left, "Too low — try a higher number.")
        return GuessResult("high", self.attempts_left, "Too high — try a lower number.")

    def use_hint(self) -> str:
        if self.ended:
            return "This round has finished."
        if self.hints_used >= 1:
            return "You have already used your hint for this round."
        self.hints_used += 1
        parity = "even" if self.secret_number % 2 == 0 else "odd"
        return f"Hint: the secret number is {parity}. (A hint reduces your final score.)"

    def _finish(self) -> None:
        self.ended = True
        self._ended_at = time.perf_counter()

    def calculate_score(self) -> int:
        """Return a score for a win; losses score zero."""
        if not self.won:
            return 0
        speed_bonus = max(0, 60 - int(self.elapsed_seconds))
        remaining_bonus = self.attempts_left * 20
        hint_penalty = self.hints_used * 20
        score = DIFFICULTY_BONUS[self.difficulty] + remaining_bonus + speed_bonus - hint_penalty
        return max(10, score)
