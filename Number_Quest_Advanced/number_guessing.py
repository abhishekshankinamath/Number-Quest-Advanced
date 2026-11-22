"""Number Quest - a polished, easy-to-use Tkinter number guessing game."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from game_engine import GameRound
from storage import GameStorage


THEMES = {
    "dark": {
        "bg": "#0B1220", "card": "#142033", "card_alt": "#1B2B43",
        "text": "#F8FAFC", "muted": "#A8B6CC", "border": "#2A3A54",
        "entry": "#0E192B", "accent": "#8B5CF6", "accent_hover": "#7445E8",
        "cyan": "#22D3EE", "green": "#34D399", "red": "#FB7185",
        "gold": "#FBBF24", "white": "#FFFFFF", "tree_alt": "#192940",
    },
    "light": {
        "bg": "#EEF3FA", "card": "#FFFFFF", "card_alt": "#E7EEF8",
        "text": "#17243A", "muted": "#64748B", "border": "#D5DFED",
        "entry": "#FFFFFF", "accent": "#7051E8", "accent_hover": "#5B3CD0",
        "cyan": "#087F9B", "green": "#07865D", "red": "#D83D5B",
        "gold": "#B77909", "white": "#FFFFFF", "tree_alt": "#F2F6FC",
    },
}


class NumberQuestApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Number Quest | Python Mini Project 02")
        self.root.geometry("1120x790")
        self.root.minsize(940, 700)
        self.theme_name = "dark"
        self.colors = THEMES[self.theme_name]
        self.storage = GameStorage()
        self.game: GameRound | None = None
        self._timer_job: str | None = None
        self._last_message = "Choose your settings, then press Start Game."
        self._last_message_kind = "info"
        self._build_ui()
        self._refresh_statistics()
        self._refresh_leaderboard()
        self._render_round()
        self._tick_timer()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Control-n>", lambda _event: self.start_new_game())
        self.root.bind("<Control-t>", lambda _event: self.toggle_theme())
        self.root.bind("<Return>", self._on_enter)

    # ---------------------------------------------------------------
    # UI construction and styling
    # ---------------------------------------------------------------
    def _build_ui(self) -> None:
        c = self.colors
        for child in self.root.winfo_children():
            child.destroy()
        self.root.configure(bg=c["bg"])

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "NQ.TCombobox", fieldbackground=c["entry"], background=c["card_alt"],
            foreground=c["text"], arrowcolor=c["text"], padding=7,
        )
        style.map(
            "NQ.TCombobox",
            fieldbackground=[("readonly", c["entry"])],
            foreground=[("readonly", c["text"])],
            selectbackground=[("readonly", c["accent"])],
            selectforeground=[("readonly", c["white"])],
        )
        style.configure(
            "NQ.Horizontal.TProgressbar", troughcolor=c["card_alt"],
            background=c["cyan"], bordercolor=c["card_alt"], lightcolor=c["cyan"],
            darkcolor=c["cyan"], thickness=11,
        )
        style.configure(
            "NQ.Treeview", background=c["card_alt"], fieldbackground=c["card_alt"],
            foreground=c["text"], rowheight=29, borderwidth=0, font=("Segoe UI", 9),
        )
        style.configure(
            "NQ.Treeview.Heading", background=c["card"], foreground=c["muted"],
            font=("Segoe UI", 9, "bold"), relief="flat", padding=(6, 7),
        )
        style.map("NQ.Treeview", background=[("selected", c["accent"])],
                  foreground=[("selected", c["white"])])

        page = tk.Frame(self.root, bg=c["bg"], padx=22, pady=18)
        page.pack(fill="both", expand=True)
        page.grid_columnconfigure(0, weight=3, uniform="main")
        page.grid_columnconfigure(1, weight=2, uniform="main")
        page.grid_rowconfigure(1, weight=1)

        # Header
        header = tk.Frame(page, bg=c["bg"])
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        brand = tk.Frame(header, bg=c["bg"])
        brand.pack(side="left", fill="x", expand=True)
        tk.Label(brand, text="🎯  NUMBER QUEST", bg=c["bg"], fg=c["text"],
                 font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(brand, text="Think smart. Guess the number. Beat your best score.",
                 bg=c["bg"], fg=c["muted"], font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))
        self.theme_button = self._make_button(
            header, "☀  Light theme" if self.theme_name == "dark" else "☾  Dark theme",
            self.toggle_theme, "secondary")
        self.theme_button.pack(side="right", padx=(10, 0), pady=5)

        # Left: game area
        left = self._card(page)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)
        self._build_setup(left)
        self._build_play_area(left)

        # Right: stats and leaderboard
        right = tk.Frame(page, bg=c["bg"])
        right.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        right.grid_columnconfigure(0, weight=1)
        self._build_stats(right)
        self._build_leaderboard(right)
        self._build_tips(right)

        footer = tk.Frame(page, bg=c["bg"])
        footer.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(13, 0))
        tk.Label(footer, text="ENTER  Guess     •     CTRL + N  New round     •     CTRL + T  Change theme",
                 bg=c["bg"], fg=c["muted"], font=("Segoe UI", 9)).pack(side="left")
        tk.Label(footer, text="PYTHON • TKINTER • JSON", bg=c["bg"], fg=c["muted"],
                 font=("Segoe UI", 8, "bold")).pack(side="right")

    def _card(self, parent: tk.Widget) -> tk.Frame:
        return tk.Frame(parent, bg=self.colors["card"], highlightthickness=1,
                        highlightbackground=self.colors["border"], bd=0, padx=17, pady=15)

    def _section_title(self, parent: tk.Widget, title: str, subtitle: str | None = None) -> None:
        c = self.colors
        tk.Label(parent, text=title, bg=c["card"], fg=c["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(parent, text=subtitle, bg=c["card"], fg=c["muted"],
                     font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

    def _build_setup(self, parent: tk.Frame) -> None:
        c = self.colors
        setup = tk.Frame(parent, bg=c["card"])
        setup.pack(fill="x", pady=(0, 15))
        self._section_title(setup, "ROUND SETUP", "Choose a player name, difficulty and your own number range.")
        fields = tk.Frame(setup, bg=c["card"])
        fields.pack(fill="x", pady=(12, 9))
        fields.grid_columnconfigure(0, weight=2)
        fields.grid_columnconfigure(1, weight=1)
        fields.grid_columnconfigure(2, weight=1)
        fields.grid_columnconfigure(3, weight=1)

        # Each input must be created inside its own grid-managed column frame.
        # Mixing pack() and grid() is allowed in different parent frames, but
        # never for children of the same parent.
        player_field = self._field(fields, "PLAYER", 0)
        self.player_entry = self._make_entry(player_field, "Player name")
        self.player_entry.insert(0, "Player")
        self.player_entry.pack(fill="x", ipady=5)

        difficulty_field = self._field(fields, "DIFFICULTY", 1)
        self.difficulty_box = ttk.Combobox(
            difficulty_field, values=("Easy", "Medium", "Hard"),
            state="readonly", style="NQ.TCombobox", width=10
        )
        self.difficulty_box.set("Medium")
        self.difficulty_box.pack(fill="x", ipady=5)

        minimum_field = self._field(fields, "MIN NUMBER", 2)
        self.min_entry = self._make_entry(minimum_field, "Minimum")
        self.min_entry.insert(0, "1")
        self.min_entry.pack(fill="x", ipady=5)

        maximum_field = self._field(fields, "MAX NUMBER", 3)
        self.max_entry = self._make_entry(maximum_field, "Maximum")
        self.max_entry.insert(0, "100")
        self.max_entry.pack(fill="x", ipady=5)

        actions = tk.Frame(setup, bg=c["card"])
        actions.pack(fill="x")
        self.start_button = self._make_button(actions, "▶  START NEW GAME", self.start_new_game, "primary")
        self.start_button.pack(side="left", fill="x", expand=True)
        tk.Label(actions, text="Range can include negative numbers too.", bg=c["card"],
                 fg=c["muted"], font=("Segoe UI", 8)).pack(side="right", padx=(10, 0))

    def _field(self, parent: tk.Frame, label: str, column: int) -> tk.Frame:
        """Create and return one grid-managed column to hold a label and input."""
        c = self.colors
        box = tk.Frame(parent, bg=c["card"])
        box.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0))
        tk.Label(box, text=label, bg=c["card"], fg=c["muted"],
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 5))
        return box

    def _make_entry(self, parent: tk.Widget, placeholder: str = "") -> tk.Entry:
        c = self.colors
        entry = tk.Entry(parent, bg=c["entry"], fg=c["text"], insertbackground=c["text"],
                         relief="flat", bd=0, font=("Segoe UI", 10),
                         highlightthickness=1, highlightbackground=c["border"],
                         highlightcolor=c["accent"])
        if placeholder:
            entry.configure(disabledforeground=c["muted"])
        return entry

    def _build_play_area(self, parent: tk.Frame) -> None:
        c = self.colors
        play = tk.Frame(parent, bg=c["card_alt"], padx=17, pady=17)
        play.pack(fill="both", expand=True)
        play.grid_columnconfigure(0, weight=1)
        top_line = tk.Frame(play, bg=c["card_alt"])
        top_line.grid(row=0, column=0, sticky="ew")
        tk.Label(top_line, text="YOUR CHALLENGE", bg=c["card_alt"], fg=c["muted"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        self.timer_label = tk.Label(top_line, text="⏱  00:00", bg=c["card_alt"], fg=c["cyan"],
                                    font=("Segoe UI", 11, "bold"))
        self.timer_label.pack(side="right")

        self.status_label = tk.Label(play, text="Ready when you are!", bg=c["card_alt"],
                                     fg=c["text"], font=("Segoe UI", 21, "bold"),
                                     wraplength=590, justify="center")
        self.status_label.grid(row=1, column=0, sticky="ew", pady=(25, 5))
        self.detail_label = tk.Label(play, text="Press START NEW GAME to choose a secret number.",
                                     bg=c["card_alt"], fg=c["muted"],
                                     font=("Segoe UI", 10), wraplength=590, justify="center")
        self.detail_label.grid(row=2, column=0, sticky="ew", pady=(0, 24))

        metrics = tk.Frame(play, bg=c["card_alt"])
        metrics.grid(row=3, column=0, sticky="ew", pady=(0, 7))
        metrics.grid_columnconfigure(0, weight=1)
        metrics.grid_columnconfigure(1, weight=1)
        self.attempts_label = tk.Label(metrics, text="ATTEMPTS  —", bg=c["card_alt"],
                                       fg=c["text"], font=("Segoe UI", 10, "bold"))
        self.attempts_label.grid(row=0, column=0, sticky="w")
        self.range_label = tk.Label(metrics, text="RANGE  —", bg=c["card_alt"],
                                    fg=c["muted"], font=("Segoe UI", 9, "bold"))
        self.range_label.grid(row=0, column=1, sticky="e")
        self.attempts_bar = ttk.Progressbar(play, style="NQ.Horizontal.TProgressbar",
                                            maximum=10, value=0)
        self.attempts_bar.grid(row=4, column=0, sticky="ew", pady=(0, 19))

        guess_area = tk.Frame(play, bg=c["card_alt"])
        guess_area.grid(row=5, column=0, sticky="ew")
        guess_area.grid_columnconfigure(0, weight=1)
        self.guess_entry = self._make_entry(guess_area)
        self.guess_entry.configure(font=("Segoe UI", 18, "bold"), justify="center")
        self.guess_entry.grid(row=0, column=0, sticky="ew", ipady=9, padx=(0, 8))
        self.guess_button = self._make_button(guess_area, "GUESS  ↵", self.submit_guess, "primary")
        self.guess_button.grid(row=0, column=1, sticky="ew", ipady=5)

        secondary = tk.Frame(play, bg=c["card_alt"])
        secondary.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        self.hint_button = self._make_button(secondary, "💡  GET A HINT", self.use_hint, "secondary")
        self.hint_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.new_round_button = self._make_button(secondary, "↻  NEW ROUND", self.start_new_game, "secondary")
        self.new_round_button.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.hint_label = tk.Label(play, text="One free hint is available each round.",
                                   bg=c["card_alt"], fg=c["gold"], font=("Segoe UI", 9),
                                   wraplength=580, justify="center")
        self.hint_label.grid(row=7, column=0, sticky="ew", pady=(12, 0))
        self.message_label = tk.Label(play, text=self._last_message, bg=c["card_alt"],
                                      fg=c["muted"], font=("Segoe UI", 9),
                                      wraplength=580, justify="center")
        self.message_label.grid(row=8, column=0, sticky="ew", pady=(10, 0))

    def _build_stats(self, parent: tk.Frame) -> None:
        c = self.colors
        card = self._card(parent)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self._section_title(card, "YOUR PROGRESS", "Your stats are saved on this computer.")
        grid = tk.Frame(card, bg=c["card"])
        grid.pack(fill="x", pady=(12, 0))
        for col in range(2):
            grid.grid_columnconfigure(col, weight=1)
        self.stat_value_labels: dict[str, tk.Label] = {}
        stat_items = [
            ("won", "WINS", c["green"]),
            ("played", "GAMES PLAYED", c["cyan"]),
            ("high_score", "HIGH SCORE", c["gold"]),
            ("best_streak", "BEST STREAK", c["accent"]),
        ]
        for index, (key, label, color) in enumerate(stat_items):
            tile = tk.Frame(grid, bg=c["card_alt"], padx=11, pady=9)
            tile.grid(row=index // 2, column=index % 2, sticky="ew", padx=4, pady=4)
            tk.Label(tile, text=label, bg=c["card_alt"], fg=c["muted"],
                     font=("Segoe UI", 8, "bold")).pack(anchor="w")
            value = tk.Label(tile, text="0", bg=c["card_alt"], fg=color,
                             font=("Segoe UI", 19, "bold"))
            value.pack(anchor="w", pady=(2, 0))
            self.stat_value_labels[key] = value

    def _build_leaderboard(self, parent: tk.Frame) -> None:
        c = self.colors
        card = self._card(parent)
        card.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)
        self._section_title(card, "🏆 TOP 5 LEADERBOARD", "Best winning scores on this device.")
        table_wrap = tk.Frame(card, bg=c["card"])
        table_wrap.pack(fill="both", expand=True, pady=(12, 0))
        columns = ("rank", "player", "score", "level")
        self.leaderboard = ttk.Treeview(table_wrap, columns=columns, show="headings",
                                        height=5, style="NQ.Treeview")
        self.leaderboard.heading("rank", text="#")
        self.leaderboard.heading("player", text="PLAYER")
        self.leaderboard.heading("score", text="SCORE")
        self.leaderboard.heading("level", text="LEVEL")
        self.leaderboard.column("rank", width=32, anchor="center", stretch=False)
        self.leaderboard.column("player", width=112, anchor="w")
        self.leaderboard.column("score", width=62, anchor="center")
        self.leaderboard.column("level", width=68, anchor="center")
        self.leaderboard.pack(fill="both", expand=True)
        self.leaderboard.tag_configure("odd", background=c["tree_alt"])
        self.leaderboard.tag_configure("even", background=c["card_alt"])

    def _build_tips(self, parent: tk.Frame) -> None:
        c = self.colors
        card = self._card(parent)
        card.grid(row=2, column=0, sticky="ew")
        self._section_title(card, "QUICK TIPS")
        tips = (
            "• Easy gives you 10 attempts; Medium 7; Hard 5.\n"
            "• Repeated guesses do not use an attempt.\n"
            "• A hint reveals whether the number is even or odd.\n"
            "• Faster wins and unused attempts earn more points."
        )
        tk.Label(card, text=tips, bg=c["card"], fg=c["muted"], justify="left",
                 font=("Segoe UI", 9), wraplength=370).pack(anchor="w", pady=(9, 0))

    def _make_button(self, parent: tk.Widget, text: str, command, kind: str = "secondary") -> tk.Button:
        c = self.colors
        if kind == "primary":
            normal, hover, foreground = c["accent"], c["accent_hover"], c["white"]
        else:
            normal, hover, foreground = c["card_alt"], c["border"], c["text"]
        button = tk.Button(parent, text=text, command=command, bg=normal, fg=foreground,
                           activebackground=hover, activeforeground=foreground,
                           font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                           cursor="hand2", padx=13, pady=9)
        button.bind("<Enter>", lambda _e, b=button, color=hover: b.configure(bg=color))
        button.bind("<Leave>", lambda _e, b=button, color=normal: b.configure(bg=color))
        return button

    # ---------------------------------------------------------------
    # Gameplay
    # ---------------------------------------------------------------
    def start_new_game(self) -> None:
        name = self.player_entry.get().strip() or "Player"
        if len(name) > 18:
            self._set_message("Player name must be 18 characters or fewer.", "error")
            return
        try:
            minimum = int(self.min_entry.get().strip())
            maximum = int(self.max_entry.get().strip())
        except ValueError:
            self._set_message("Minimum and maximum must be whole numbers.", "error")
            return
        if maximum <= minimum:
            self._set_message("Maximum must be greater than minimum.", "error")
            return
        if maximum - minimum > 10**12:
            self._set_message("Please choose a smaller range (maximum span: 1 trillion).", "error")
            return

        difficulty = self.difficulty_box.get()
        self.game = GameRound(minimum, maximum, difficulty, name)
        self._last_message = f"A new {difficulty.lower()} round has started. Make your first guess!"
        self._last_message_kind = "info"
        self._render_round()
        self.guess_entry.focus_set()

    def submit_guess(self) -> None:
        if self.game is None or self.game.ended:
            self._set_message("Start a new game before guessing.", "error")
            return
        raw = self.guess_entry.get().strip()
        try:
            guess = int(raw)
        except ValueError:
            self._set_message("Please enter a whole number, such as 42.", "error")
            self.guess_entry.focus_set()
            return

        result = self.game.submit_guess(guess)
        self.guess_entry.delete(0, tk.END)
        self._last_message = result.message
        if result.status in ("out_of_range", "duplicate", "finished"):
            self._last_message_kind = "error"
            self._render_round()
            self.guess_entry.focus_set()
            return

        if result.status == "correct":
            self._last_message_kind = "success"
            score = self.game.calculate_score()
            elapsed = self.game.elapsed_seconds
            self._save_finished_round(score)
            self._last_message = (
                f"🎉 Brilliant, {self.game.player_name}! You won {score} points "
                f"in {self._format_time(elapsed)}."
            )
        elif result.status == "lost":
            self._last_message_kind = "error"
            self._save_finished_round(0)
        elif result.status == "low":
            self._last_message_kind = "info"
            self.root.bell()
        elif result.status == "high":
            self._last_message_kind = "info"
            self.root.bell()

        self._render_round()
        if self.game.ended:
            self._refresh_statistics()
            self._refresh_leaderboard()
        else:
            self.guess_entry.focus_set()

    def use_hint(self) -> None:
        if self.game is None or self.game.ended:
            self._set_message("Start a game to use a hint.", "error")
            return
        hint = self.game.use_hint()
        self.hint_label.configure(text=hint)
        self._set_message("Hint used. Remember: hints reduce your final score.", "info")
        self.hint_button.configure(state="disabled")

    def _save_finished_round(self, score: int) -> None:
        assert self.game is not None
        self.storage.record_game(
            player=self.game.player_name,
            won=self.game.won,
            score=score,
            difficulty=self.game.difficulty,
            minimum=self.game.minimum,
            maximum=self.game.maximum,
            attempts_used=self.game.attempts_used,
            elapsed_seconds=self.game.elapsed_seconds,
            hints_used=self.game.hints_used,
        )

    # ---------------------------------------------------------------
    # Refresh, time and visual state
    # ---------------------------------------------------------------
    def _render_round(self) -> None:
        c = self.colors
        if self.game is None:
            self.status_label.configure(text="Ready when you are!", fg=c["text"])
            self.detail_label.configure(text="Press START NEW GAME to choose a secret number.")
            self.attempts_label.configure(text="ATTEMPTS  —")
            self.range_label.configure(text="RANGE  —")
            self.attempts_bar.configure(maximum=10, value=0)
            self.timer_label.configure(text="⏱  00:00")
            self.guess_entry.configure(state="disabled")
            self.guess_button.configure(state="disabled")
            self.hint_button.configure(state="disabled")
            self.hint_label.configure(text="One free hint is available each round.")
            self.message_label.configure(text=self._last_message, fg=c["muted"])
            return

        game = self.game
        self.attempts_label.configure(text=f"ATTEMPTS  {game.attempts_left} / {game.max_attempts}")
        self.range_label.configure(text=f"RANGE  {game.minimum} to {game.maximum}")
        self.attempts_bar.configure(maximum=game.max_attempts, value=game.attempts_left)
        self.timer_label.configure(text=f"⏱  {self._format_time(game.elapsed_seconds)}")
        self.detail_label.configure(
            text=f"{game.difficulty} mode  •  {game.minimum} to {game.maximum}  •  "
                 f"{game.max_attempts} attempts allowed"
        )
        if game.ended and game.won:
            self.status_label.configure(text="YOU GOT IT! 🎉", fg=c["green"])
            self.detail_label.configure(
                text=f"The secret number was {game.secret_number}. You used {game.attempts_used} guess(es)."
            )
        elif game.ended:
            self.status_label.configure(text="ROUND OVER", fg=c["red"])
            self.detail_label.configure(text=f"The secret number was {game.secret_number}. Try another round!")
        else:
            self.status_label.configure(text="Make your guess", fg=c["text"])
        enabled = "disabled" if game.ended else "normal"
        self.guess_entry.configure(state=enabled)
        self.guess_button.configure(state=enabled)
        self.hint_button.configure(state="disabled" if game.ended or game.hints_used else "normal")
        if game.hints_used == 0:
            self.hint_label.configure(text="One hint available: reveal whether the secret number is even or odd.")
        self.message_label.configure(text=self._last_message,
                                     fg=self._message_color(self._last_message_kind))

    def _set_message(self, text: str, kind: str = "info") -> None:
        self._last_message = text
        self._last_message_kind = kind
        if hasattr(self, "message_label"):
            self.message_label.configure(text=text, fg=self._message_color(kind))

    def _message_color(self, kind: str) -> str:
        return {"success": self.colors["green"], "error": self.colors["red"],
                "info": self.colors["muted"]}.get(kind, self.colors["muted"])

    def _refresh_statistics(self) -> None:
        stats = self.storage.statistics()
        for key, label in getattr(self, "stat_value_labels", {}).items():
            label.configure(text=str(stats.get(key, 0)))

    def _refresh_leaderboard(self) -> None:
        if not hasattr(self, "leaderboard"):
            return
        for item in self.leaderboard.get_children():
            self.leaderboard.delete(item)
        for index, record in enumerate(self.storage.top_scores(5), start=1):
            tag = "odd" if index % 2 else "even"
            self.leaderboard.insert(
                "", "end",
                values=(index, record.get("player", "Player"), record.get("score", 0),
                        record.get("difficulty", "—")),
                tags=(tag,),
            )
        if not self.storage.top_scores(5):
            self.leaderboard.insert("", "end", values=("—", "No wins yet", "—", "—"), tags=("even",))

    def _tick_timer(self) -> None:
        if self.game is not None and not self.game.ended and hasattr(self, "timer_label"):
            self.timer_label.configure(text=f"⏱  {self._format_time(self.game.elapsed_seconds)}")
        self._timer_job = self.root.after(250, self._tick_timer)

    @staticmethod
    def _format_time(seconds: float) -> str:
        total = max(0, int(seconds))
        minutes, secs = divmod(total, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def toggle_theme(self) -> None:
        # Preserve setup choices while rebuilding the widgets in the new palette.
        setup_values = {
            "player": self.player_entry.get(),
            "difficulty": self.difficulty_box.get(),
            "minimum": self.min_entry.get(),
            "maximum": self.max_entry.get(),
        }
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.colors = THEMES[self.theme_name]
        self._build_ui()
        self.player_entry.delete(0, tk.END)
        self.player_entry.insert(0, setup_values["player"])
        self.difficulty_box.set(setup_values["difficulty"])
        self.min_entry.delete(0, tk.END)
        self.min_entry.insert(0, setup_values["minimum"])
        self.max_entry.delete(0, tk.END)
        self.max_entry.insert(0, setup_values["maximum"])
        self._refresh_statistics()
        self._refresh_leaderboard()
        self._render_round()

    def _on_enter(self, _event: tk.Event) -> str:
        if self.game is not None and not self.game.ended:
            self.submit_guess()
        return "break"

    def _on_close(self) -> None:
        if self._timer_job is not None:
            try:
                self.root.after_cancel(self._timer_job)
            except tk.TclError:
                pass
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    NumberQuestApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
