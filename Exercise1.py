# maths_quiz_gui.py — Tkinter Maths Quiz (Clean & Centered, fixed digit typing)
# 10 questions per round, three difficulty levels, random +/-, two attempts per
# question (10 or 5 points), final score with grade and an option to play again.

import os
import random
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

# Background image support (uses Pillow if it's available)
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except Exception:
    PIL_OK = False

# ----------------------
# Window & Theme
# ----------------------
WINDOW_SIZE = (1000, 600)   # fixed size so the layout stays stable

BG_CANDIDATES = [
    "download.jfif",
    os.path.join(os.path.dirname(__file__), "download.jfif"),
    "/mnt/data/download.jfif",
]

COLORS = {
    "bg":        "#0a0b1e",
    "panel":     "#121433",
    "shadow":    "#050615",
    "hud":       "#151739",
    "text":      "#eef1ff",
    "muted":     "#cfd6ff",
    "accent":    "#5ee7ff",
    "accent_hi": "#9af1ff",
    "accent_lo": "#38d2f0",
    "pink":      "#ff66d4",
    "purple":    "#9b6bff",
    "warn":      "#ff9fb3",
}


def load_bg(size):
    """Look for the grid image and return a PhotoImage if we can load it."""
    path = next((p for p in BG_CANDIDATES if os.path.exists(p)), None)
    if not path:
        return None
    try:
        if PIL_OK:
            return ImageTk.PhotoImage(Image.open(path).resize(size))
        # Without Pillow, JPEG support is shaky, so we just skip it.
        return None
    except Exception:
        return None


class MathsQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maths Quiz — Clean & Centered")
        self.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

        # Overall quiz state
        self.digits = 1
        self.q_index = 0
        self.score = 0
        self.first_try = True
        self.a = 0
        self.b = 0
        self.op = '+'

        # Main container for all screens
        self.stage = tk.Frame(self, bg=COLORS["bg"])
        self.stage.pack(expand=True, fill="both")

        # Optional background image
        self.bg_image = load_bg(WINDOW_SIZE)

        # Widget styles
        self._setup_styles()

        # References we reuse between screens
        self._progress = None
        self._hud_score = None
        self._card_canvas = None
        self._card_border_id = None

        # Quick way back to the menu during testing
        self.bind("<Escape>", lambda e: self.displayMenu())

        # Start on the home screen
        self.displayHome()

    # ----------------------
    # UI helpers
    # ----------------------
    def _setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Main neon buttons
        style.configure(
            "Primary.TButton",
            padding=(16, 10),
            font=("Segoe UI", 11, "bold"),
            foreground="#051a1e",
            background=COLORS["accent"],
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", COLORS["accent_hi"]), ("pressed", COLORS["accent_lo"])],
            relief=[("pressed", "flat")]
        )

        # Outline-style button for secondary actions
        style.configure(
            "Ghost.TButton",
            padding=(12, 8),
            font=("Segoe UI", 10, "bold"),
            foreground=COLORS["accent_hi"],
            background=COLORS["panel"],
            borderwidth=1
        )
        style.map(
            "Ghost.TButton",
            background=[("active", COLORS["hud"]), ("pressed", "#0d1130")],
            foreground=[("active", COLORS["accent"]), ("pressed", COLORS["accent_lo"])],
        )

        style.configure(
            "Cyan.Horizontal.TProgressbar",
            troughcolor=COLORS["panel"],
            background=COLORS["accent"],
        )

    def _clear(self):
        """Wipe the current screen and reset key bindings."""
        self.unbind("<Return>")
        # These shortcuts are only for the difficulty menu.
        self.unbind("1")
        self.unbind("2")
        self.unbind("3")

        for w in self.stage.winfo_children():
            w.destroy()

        self._card_canvas = None
        self._card_border_id = None

    def _paint_bg(self):
        """Paint the background image (or solid colour if we don't have one)."""
        if self.bg_image is not None:
            tk.Label(self.stage, image=self.bg_image, borderwidth=0) \
                .place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.stage.configure(bg=COLORS["bg"])

    def _center_frame(self, y_rel=0.5, parent=None, bg=None):
        """Place a frame horizontally centered at a given vertical position."""
        host = parent or self.stage
        frame = tk.Frame(host, bg=(bg or host["bg"]))
        frame.place(relx=0.5, rely=y_rel, anchor="center")
        return frame

    def _choose_font(self):
        """Try to pick a slightly more “sci-fi” font if it exists on the system."""
        families = set(tkfont.families())
        for f in ("Orbitron", "Audiowide", "Oxanium", "Neuropol"):
            if f in families:
                return f
        return "Segoe UI"

    def _title(self, parent, text, size=48, fg=COLORS["pink"]):
        """Consistent heading helper."""
        fam = self._choose_font()
        lbl = tk.Label(
            parent,
            text=text,
            font=(fam, size, "bold"),
            fg=fg,
            bg=parent["bg"],
            anchor="center",
            justify="center",
        )
        lbl.pack(pady=(8, 10))
        return lbl

    def _glass_card(self, y_rel=0.5, width=800, height=340, pad=24):
        """
        Simple “glass” card effect:
        - a darker shadow
        - a purple border
        - an inner panel for content
        """
        container = self._center_frame(y_rel=y_rel, parent=self.stage, bg=self.stage["bg"])

        # Soft shadow behind the card
        shadow = tk.Canvas(container, width=width, height=height,
                           bg=self.stage["bg"], highlightthickness=0)
        shadow.pack()
        shadow.create_rectangle(
            10, 10, width - 2, height - 2,
            fill=COLORS["shadow"], outline=COLORS["shadow"]
        )

        # Actual border frame
        canvas = tk.Canvas(container, width=width, height=height,
                           bg=self.stage["bg"], highlightthickness=0)
        canvas.place(x=0, y=0)
        border = canvas.create_rectangle(
            2, 2, width - 2, height - 2,
            outline=COLORS["purple"], width=2
        )

        inner = tk.Frame(container, bg=COLORS["panel"])
        inner.place(x=pad, y=pad, width=width - 2 * pad, height=height - 2 * pad)

        self._card_canvas, self._card_border_id = canvas, border
        return inner

    def _flash_border(self, color=COLORS["accent"], ms=130):
        """Quick flash on the card border (used for a correct answer)."""
        if self._card_canvas and self._card_border_id:
            try:
                self._card_canvas.itemconfig(self._card_border_id, outline=color)
                self.after(
                    ms,
                    lambda: self._card_canvas.itemconfig(
                        self._card_border_id, outline=COLORS["purple"]
                    ),
                )
            except Exception:
                pass

    def _label(self, parent, text, size=16, fg=COLORS["text"], bold=False, wrap=None):
        """Regular centered label with optional wrapping."""
        fam = self._choose_font()
        style = "bold" if bold else "normal"
        lbl = tk.Label(
            parent,
            text=text,
            font=(fam, size, style),
            fg=fg,
            bg=parent["bg"],
            anchor="center",
            justify="center",
            wraplength=wrap,
        )
        lbl.pack()
        return lbl

    # ----------------------
    # Screens
    # ----------------------
    def displayHome(self):
        """Intro screen with title and a single “Start” button."""
        self._clear()
        self._paint_bg()

        card = self._glass_card(y_rel=0.50, width=840, height=360, pad=28)
        self._title(card, "MATHS QUIZ", size=44)
        self._label(
            card,
            "Sharpen your skills with neon-powered addition & subtraction.",
            size=18,
            fg=COLORS["muted"],
            bold=True,
            wrap=760,
        )

        ttk.Button(
            card,
            text="Start Quiz",
            style="Primary.TButton",
            command=self.displayMenu,
        ).pack(pady=18, ipadx=14)

    def displayMenu(self):
        """Difficulty selection screen."""
        self._clear()
        self._paint_bg()

        card = self._glass_card(y_rel=0.50, width=840, height=400, pad=28)
        self._title(card, "DIFFICULTY LEVEL", size=36, fg=COLORS["pink"])
        self._label(
            card,
            "1) Easy = 1-digit   •   2) Moderate = 2-digit   •   3) Advanced = 4-digit",
            size=14,
            fg=COLORS["muted"],
            wrap=760,
        )

        btns = tk.Frame(card, bg=COLORS["panel"])
        btns.pack(pady=10)

        ttk.Button(
            btns,
            text="1. Easy",
            style="Primary.TButton",
            command=lambda: self._start_quiz(1),
        ).pack(pady=6, ipadx=14)
        ttk.Button(
            btns,
            text="2. Moderate",
            style="Primary.TButton",
            command=lambda: self._start_quiz(2),
        ).pack(pady=6, ipadx=14)
        ttk.Button(
            btns,
            text="3. Advanced",
            style="Primary.TButton",
            command=lambda: self._start_quiz(4),
        ).pack(pady=6, ipadx=14)

        # Number keys act as shortcuts here; they get unbound again in _clear()
        self.bind("1", lambda e: self._start_quiz(1))
        self.bind("2", lambda e: self._start_quiz(2))
        self.bind("3", lambda e: self._start_quiz(4))

        # Back-to-home button was removed as requested

    def displayProblem(self):
        """Question screen: HUD + card with the current sum/difference."""
        self._clear()
        self._paint_bg()

        # Small bar at the top with progress and score
        hud = tk.Frame(self.stage, bg=COLORS["hud"])
        hud.place(relx=0.5, rely=0.12, anchor="center")

        tk.Label(
            hud,
            text=f"Question {self.q_index + 1} / 10",
            fg=COLORS["muted"],
            bg=COLORS["hud"],
            font=(self._choose_font(), 11, "bold"),
        ).pack(side="left", padx=10, pady=4)

        self._hud_score = tk.Label(
            hud,
            text=f"Score: {self.score}",
            fg=COLORS["accent"],
            bg=COLORS["hud"],
            font=(self._choose_font(), 11, "bold"),
        )
        self._hud_score.pack(side="left", padx=10, pady=4)

        self._progress = ttk.Progressbar(
            hud,
            length=220,
            mode="determinate",
            style="Cyan.Horizontal.TProgressbar",
            maximum=10,
            value=self.q_index,
        )
        self._progress.pack(side="left", padx=10, pady=6)

        # Main card with the actual problem
        card = self._glass_card(y_rel=0.60, width=840, height=420, pad=28)
        self._title(card, "SOLVE", size=34)

        tk.Label(
            card,
            text=f"{self.a} {self.op} {self.b} =",
            font=("Consolas", 56, "bold"),
            fg=COLORS["text"],
            bg=COLORS["panel"],
        ).pack(pady=(6, 2))

        # Entry field and “Your answer” echo
        ans_var = tk.StringVar()
        entry = tk.Entry(
            card,
            width=12,
            font=("Consolas", 24),
            bg="#111633",
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief="flat",
            textvariable=ans_var,
            justify="center",
        )
        entry.pack(pady=(8, 4))
        entry.focus_set()

        echo = tk.Label(
            card,
            text="Your answer: —",
            font=(self._choose_font(), 12),
            fg=COLORS["muted"],
            bg=COLORS["panel"],
            anchor="center",
            justify="center",
        )
        echo.pack(pady=(0, 8), fill="x")

        def _update_echo(*_):
            txt = ans_var.get().strip()
            echo.config(text=f"Your answer: {txt if txt else '—'}")

        ans_var.trace_add("write", _update_echo)

        fb = tk.Label(
            card,
            text="",
            font=(self._choose_font(), 12),
            fg=COLORS["muted"],
            bg=COLORS["panel"],
            anchor="center",
            justify="center",
        )
        fb.pack(pady=(0, 8), fill="x")

        correct_value = self.a + self.b if self.op == "+" else self.a - self.b

        def submit():
            """Handle one submit click (or Enter key)."""
            txt = ans_var.get().strip()
            echo.config(text=f"Your answer: {txt if txt else '—'}")
            try:
                user = int(txt)
            except ValueError:
                fb.config(text="Please enter a whole number.")
                return

            if self.isCorrect(user):
                # First attempt gives 10, second attempt gives 5
                self.score += 10 if self.first_try else 5
                self._hud_score.config(text=f"Score: {self.score}")
                self._flash_border(COLORS["accent"])
                self.after(160, self._next_or_finish)
            else:
                if self.first_try:
                    self.first_try = False
                    fb.config(text="Not quite — one more try.")
                    entry.delete(0, tk.END)
                    ans_var.set("")  # clears the echo at the same time
                else:
                    fb.config(text=f"Answer: {correct_value}", fg=COLORS["warn"])
                    self.after(250, self._next_or_finish)

        ttk.Button(
            card,
            text="Submit",
            style="Primary.TButton",
            command=submit,
        ).pack(pady=8, ipadx=16)
        self.bind("<Return>", lambda e: submit())

    def displayResults(self):
        """Show the final score, grade, and options to replay or quit."""
        self._clear()
        self._paint_bg()

        card = self._glass_card(y_rel=0.50, width=840, height=360, pad=28)
        self._title(card, "RESULTS", size=40)
        self._label(card, f"Final Score: {self.score} / 100", size=22, bold=True)
        self._label(
            card,
            f"Rank: {self._grade(self.score)}",
            size=16,
            fg=COLORS["muted"],
            bold=True,
        )

        btns = tk.Frame(card, bg=COLORS["panel"])
        btns.pack(pady=12)

        ttk.Button(
            btns,
            text="Play Again",
            style="Primary.TButton",
            command=self.displayMenu,
        ).pack(pady=6, ipadx=14)
        ttk.Button(
            btns,
            text="Quit",
            style="Ghost.TButton",
            command=self.destroy,
        ).pack(pady=2, ipadx=18)

        # Small delay so the user sees the result before the popup appears
        self.after(400, self._prompt_replay)

    # ----------------------
    # Flow / state transitions
    # ----------------------
    def _prompt_replay(self):
        if messagebox.askyesno("Play again?", "Would you like to play another round?"):
            self.displayMenu()

    def _start_quiz(self, digits):
        """Reset state and begin a new 10-question round."""
        self.digits = digits
        self.q_index = 0
        self.score = 0
        self.first_try = True
        self._new_problem()
        self.displayProblem()

    def _new_problem(self):
        """Create a fresh arithmetic problem."""
        self.a = self.randomInt(self.digits)
        self.b = self.randomInt(self.digits)
        self.op = self.decideOperation()

    def _next_or_finish(self):
        """Move on to the next question or show the result screen."""
        self.q_index += 1
        self.first_try = True

        if self._progress:
            self._progress["value"] = min(self.q_index, 10)

        if self.q_index >= 10:
            self.displayResults()
        else:
            self._new_problem()
            self.displayProblem()

    # ----------------------
    # Required core functions
    # ----------------------
    def randomInt(self, digits):
        """Pick a random integer in the range that matches the difficulty."""
        if digits == 1:
            return random.randint(0, 9)
        if digits == 2:
            return random.randint(10, 99)
        if digits == 4:
            return random.randint(1000, 9999)
        # Shouldn't get here, but we fall back to a single digit just in case
        return random.randint(0, 9)

    def decideOperation(self):
        """Randomly choose addition or subtraction."""
        return random.choice(["+", "-"])

    def isCorrect(self, user_answer):
        """Check the user's answer against the correct result."""
        correct = self.a + self.b if self.op == "+" else self.a - self.b
        return user_answer == correct

    @staticmethod
    def _grade(score):
        """Very simple grade boundaries used for the final rank."""
        if score >= 90:
            return "A+"
        if score >= 80:
            return "A"
        if score >= 70:
            return "B"
        if score >= 60:
            return "C"
        if score >= 50:
            return "D"
        return "F"


if __name__ == "__main__":
    app = MathsQuizApp()
    app.mainloop()

