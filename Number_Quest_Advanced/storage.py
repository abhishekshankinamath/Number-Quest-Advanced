"""JSON persistence for Number Quest scores and lifetime statistics."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).with_name("game_data.json")

DEFAULT_DATA: dict[str, Any] = {
    "stats": {
        "played": 0,
        "won": 0,
        "lost": 0,
        "total_score": 0,
        "high_score": 0,
        "current_streak": 0,
        "best_streak": 0,
    },
    "records": [],
}


class GameStorage:
    def __init__(self, path: Path | str = DATA_FILE) -> None:
        self.path = Path(path)
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return json.loads(json.dumps(DEFAULT_DATA))
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                raise ValueError("Game data must be a JSON object.")
            stats = dict(DEFAULT_DATA["stats"])
            if isinstance(loaded.get("stats"), dict):
                stats.update(loaded["stats"])
            records = loaded.get("records", [])
            if not isinstance(records, list):
                records = []
            return {"stats": stats, "records": records}
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            # Keep the game usable if the saved file is damaged.
            return json.loads(json.dumps(DEFAULT_DATA))

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        temporary.replace(self.path)

    def record_game(
        self,
        *,
        player: str,
        won: bool,
        score: int,
        difficulty: str,
        minimum: int,
        maximum: int,
        attempts_used: int,
        elapsed_seconds: float,
        hints_used: int,
    ) -> None:
        stats = self.data["stats"]
        stats["played"] += 1
        if won:
            stats["won"] += 1
            stats["total_score"] += score
            stats["high_score"] = max(stats["high_score"], score)
            stats["current_streak"] += 1
            stats["best_streak"] = max(stats["best_streak"], stats["current_streak"])
        else:
            stats["lost"] += 1
            stats["current_streak"] = 0

        record = {
            "player": player,
            "won": bool(won),
            "score": int(score),
            "difficulty": difficulty,
            "minimum": int(minimum),
            "maximum": int(maximum),
            "attempts_used": int(attempts_used),
            "elapsed_seconds": round(float(elapsed_seconds), 2),
            "hints_used": int(hints_used),
            "date": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        self.data["records"].append(record)
        # Keep the most recent 100 rounds in the local history file.
        self.data["records"] = self.data["records"][-100:]
        self._save()

    def top_scores(self, limit: int = 5) -> list[dict[str, Any]]:
        wins = [r for r in self.data["records"] if r.get("won")]
        return sorted(
            wins,
            key=lambda r: (-int(r.get("score", 0)), float(r.get("elapsed_seconds", 0))),
        )[:limit]

    def statistics(self) -> dict[str, int]:
        return dict(self.data["stats"])
