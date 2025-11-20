# Tkinter Maths Quiz — final version used for the assignment
# 10 questions per round, with 1/2/4 digit difficulty and random +/-
# Two attempts per question (10 points first try, 5 on second), plus final score and grade with replay option.

import os
import random
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

# Optional: Pillow support so we can use a JPG background if it's available
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except Exception:
    PIL_OK = False

# ----------------------
# Basic window size and color theme
# ----------------------
WINDOW_SIZE = (1000, 600)

BG_CANDIDATES = [
    "download.jfif",
    os.path.join(os.path.dirname(__file__), "download.jfif"),
    "/mnt/data/download.jfif",
]

COLORS = {
    "bg": "#0a0b1e",
    "panel": "#121433",
    "shadow": "#050615",
    "hud": "#151739",
    "text": "#eef1ff",
    "muted": "#cfd6ff",
    "accent": "#5ee7ff",
    "accent_hi": "#9af1ff",
    "accent_lo": "#38d2f0",
    "pink": "#ff66d4",
    "purple": "#9b6bff",
    "warn": "#ff9fb3",
}


def load_bg(size):
    """Try to load a background image and resize it to the window."""
    path = next((p for p in BG_CANDIDATES if os.path.exists(p)), None)
    if not path:
        return None
    try:
        if PIL_OK:
            return ImageTk.PhotoImage(Image.open(path).resize(size))
    except Exception:
        return None


class MathsQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maths Quiz — Clean & Centered")
        self.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

        # Keeps track of the current quiz state
        self.digits = 1
        self.q_index = 0
        self.score = 0
        self.first_try = True
        self.a = 0
        self.b = 0
        self.op = '+'

        # Main frame where all different screens are shown
        self.stage = tk.Frame(self, bg=COLORS["bg"])
        self.stage.pack(expand=True, fill="both")

        # Preload background image once so we can reuse it
        self.bg_image = load_bg(WINDOW_SIZE)

        # Set up ttk styles for buttons and other widgets
        self._setup_styles()

        # Keyboard shortcut: Escape goes back to the menu
        self.bind("<Escape>", lambda e: self.displayMenu())

        # Start on the home screen
        self.displayHome()

    # ----------------------
    # Helper functions
    # ----------------------
    def _setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

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

        style.configure(
            "Ghost.TButton",
            padding=(10, 6),
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
        # Remove old widgets and keybindings before drawing the next screen
        self.unbind("<Return>")
        self.unbind("1")
        self.unbind("2")
        self.unbind("3")
        for w in self.stage.winfo_children():
            w.destroy()

    def _paint_bg(self):
        # Either show the image background or fall back to a solid color
        if self.bg_image:
            tk.Label(self.stage, image=self.bg_image, borderwidth=0).place(
                x=0, y=0, relwidth=1, relheight=1
            )
        else:
            self.stage.configure(bg=COLORS["bg"])

    def _center_frame(self, y_rel=0.5, parent=None, bg=None):
        host = parent or self.stage
        frame = tk.Frame(host, bg=(bg or host["bg"]))
        frame.place(relx=0.5, rely=y_rel, anchor="center")
        return frame

    def _choose_font(self):
        families = set(tkfont.families())
        for f in ("Orbitron", "Audiowide", "Oxanium", "Neuropol"):
            if f in families:
                return f
        return "Segoe UI"

    def _title(self, parent, text, size=48, fg=COLORS["pink"]):
        fam = self._choose_font()
        lbl = tk.Label(
            parent,
            text=text,
            font=(fam, size, "bold"),
            fg=fg,
            bg=parent["bg"],
            anchor="center",
        )
        lbl.pack(pady=(8, 10))
        return lbl

    def _glass_card(self, y_rel=0.5, width=840, height=400, pad=28):
        # Simple framed "card" in the middle of the screen for content
        container = self._center_frame(y_rel=y_rel, parent=self.stage, bg=self.stage["bg"])
        canvas = tk.Canvas(
            container,
            width=width,
            height=height,
            bg=self.stage["bg"],
            highlightthickness=0,
        )
        canvas.pack()
        canvas.create_rectangle(
            2, 2, width - 2, height - 2, outline=COLORS["purple"], width=2
        )
        inner = tk.Frame(container, bg=COLORS["panel"])
        inner.place(x=pad, y=pad, width=width - 2 * pad, height=height - 2 * pad)
        return inner

    def _label(self, parent, text, size=16, fg=COLORS["text"], bold=False, wrap=None):
        fam = self._choose_font()
        lbl = tk.Label(
            parent,
            text=text,
            font=(fam, size, "bold" if bold else "normal"),
            fg=fg,
            bg=parent["bg"],
            anchor="center",
            justify="center",
            wraplength=wrap,
        )
        lbl.pack()
        return lbl

    # ----------------------
    # Screens (home, level select, question view, results)
    # ----------------------
    def displayHome(self):
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
        self._clear()
        self._paint_bg()

        card = self._glass_card(y_rel=0.50, width=840, height=460, pad=28)
        self._title(card, "DIFFICULTY LEVEL", size=36, fg=COLORS["pink"])
        self._label(
            card,
            "1) Easy = 1-digit   •   2) Moderate = 2-digit   •   3) Advanced = 4-digit",
            size=14,
            fg=COLORS["muted"],
            wrap=760,
        )

        btns = tk.Frame(card, bg=COLORS["panel"])
        btns.pack(pady=20)

        def make_btn(text, cmd, style="Primary.TButton"):
            b = ttk.Button(btns, text=text, style=style, command=cmd)
            b.pack(pady=6, ipadx=14, ipady=2)
            return b

        make_btn("1. Easy", lambda: self._start_quiz(1))
        make_btn("2. Moderate", lambda: self._start_quiz(2))
        make_btn("3. Advanced", lambda: self._start_quiz(4))
        make_btn("Back to Home", self.displayHome, style="Ghost.TButton")

        self.bind("1", lambda e: self._start_quiz(1))
        self.bind("2", lambda e: self._start_quiz(2))
        self.bind("3", lambda e: self._start_quiz(4))

    def displayProblem(self):
        self._clear()
        self._paint_bg()

        # Small bar at the top showing question number and score
        hud = tk.Frame(self.stage, bg=COLORS["hud"])
        hud.place(relx=0.5, rely=0.12, anchor="center")
        tk.Label(
            hud,
            text=f"Question {self.q_index + 1} / 10",
            fg=COLORS["muted"],
            bg=COLORS["hud"],
            font=(self._choose_font(), 11, "bold"),
        ).pack(side="left", padx=10)
        self._hud_score = tk.Label(
            hud,
            text=f"Score: {self.score}",
            fg=COLORS["accent"],
            bg=COLORS["hud"],
            font=(self._choose_font(), 11, "bold"),
        )
        self._hud_score.pack(side="left", padx=10)

        card = self._glass_card(y_rel=0.60, width=840, height=420, pad=28)
        self._title(card, "SOLVE", size=34)
        tk.Label(
            card,
            text=f"{self.a} {self.op} {self.b} =",
            font=("Consolas", 56, "bold"),
            fg=COLORS["text"],
            bg=COLORS["panel"],
        ).pack(pady=(6, 2))

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
        )
        echo.pack(pady=(0, 8))

        def update_echo(*_):
            txt = ans_var.get().strip()
            echo.config(text=f"Your answer: {txt if txt else '—'}")

        ans_var.trace_add("write", update_echo)
        fb = tk.Label(
            card,
            text="",
            font=(self._choose_font(), 12),
            fg=COLORS["muted"],
            bg=COLORS["panel"],
        )
        fb.pack(pady=(0, 8))

        correct_value = self.a + self.b if self.op == '+' else self.a - self.b

        def submit():
            txt = ans_var.get().strip()
            try:
                user = int(txt)
            except ValueError:
                fb.config(text="Please enter a number.")
                return
            if self.isCorrect(user):
                self.score += 10 if self.first_try else 5
                self._hud_score.config(text=f"Score: {self.score}")
                self.after(150, self._next_or_finish)
            else:
                if self.first_try:
                    self.first_try = False
                    fb.config(text="Try again!")
                    entry.delete(0, tk.END)
                else:
                    fb.config(text=f"Answer: {correct_value}", fg=COLORS["warn"])
                    self.after(300, self._next_or_finish)

        ttk.Button(
            card,
            text="Submit",
            style="Primary.TButton",
            command=submit,
        ).pack(pady=10, ipadx=16)
        self.bind("<Return>", lambda e: submit())

    def displayResults(self):
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

        self.after(400, self._prompt_replay)

    # ----------------------
    # Game flow (start, next question, finish)
    # ----------------------
    def _prompt_replay(self):
        if messagebox.askyesno("Play again?", "Would you like to play another round?"):
            self.displayMenu()

    def _start_quiz(self, digits):
        self.digits = digits
        self.q_index = 0
        self.score = 0
        self.first_try = True
        self._new_problem()
        self.displayProblem()

    def _new_problem(self):
        self.a = self.randomInt(self.digits)
        self.b = self.randomInt(self.digits)
        self.op = self.decideOperation()

    def _next_or_finish(self):
        self.q_index += 1
        self.first_try = True
        if self.q_index >= 10:
            self.displayResults()
        else:
            self._new_problem()
            self.displayProblem()

    # ----------------------
    # Core quiz logic (numbers, operator choice, correctness check, grade)
    # ----------------------
    def randomInt(self, digits):
        if digits == 1:
            return random.randint(0, 9)
        if digits == 2:
            return random.randint(10, 99)
        if digits == 4:
            return random.randint(1000, 9999)
        return random.randint(0, 9)

    def decideOperation(self):
        return random.choice(['+', '-'])

    def isCorrect(self, user_answer):
        correct = self.a + self.b if self.op == '+' else self.a - self.b
        return user_answer == correct

    @staticmethod
    def _grade(score):
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
