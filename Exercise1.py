# maths_quiz_gui.py — Tkinter Maths Quiz (Final Version with natural comments)

import os
import random
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

# Pillow lets us use JPG/JFIF backgrounds. The app still works without it.
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except Exception:
    PIL_OK = False

# Window size and main colour palette
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
    """Try to load the grid background image. If anything fails, just skip it."""
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

        # Slight scaling tweak so text looks less jagged on Windows
        try:
            self.tk.call("tk", "scaling", 1.15)
        except Exception:
            pass

        self.title("Maths Quiz — Clean & Centered")
        self.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

        # Basic quiz state
        self.digits = 1
        self.q_index = 0
        self.score = 0
        self.first_try = True
        self.a = 0
        self.b = 0
        self.op = "+"

        # Main container frame
        self.stage = tk.Frame(self, bg=COLORS["bg"])
        self.stage.pack(expand=True, fill="both")

        # Background image is optional
        self.bg_image = load_bg(WINDOW_SIZE)

        self._setup_styles()
        self.displayHome()

    # ---------- styling and small helpers ----------

    def _setup_styles(self):
        style = ttk.Style(self)

        # Main blue buttons
        style.configure(
            "Primary.TButton",
            padding=(14, 9),
            font=("Segoe UI", 11),
            foreground="#061019",
            background=COLORS["accent"],
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", COLORS["accent_hi"]), ("pressed", COLORS["accent_lo"])],
        )

        # Slightly bigger button used for “Submit”
        style.configure(
            "Action.TButton",
            padding=(18, 12),
            font=("Segoe UI", 12),
            foreground="#000000",
            background=COLORS["accent"],
            borderwidth=0,
        )
        style.map(
            "Action.TButton",
            background=[("active", COLORS["accent_hi"]), ("pressed", COLORS["accent_lo"])],
        )

        # Flat outlined button for back/secondary actions
        style.configure(
            "Ghost.TButton",
            padding=(10, 6),
            font=("Segoe UI", 10),
            foreground=COLORS["accent_hi"],
            background=COLORS["panel"],
            borderwidth=1,
        )

        style.configure(
            "Cyan.Horizontal.TProgressbar",
            troughcolor=COLORS["panel"],
            background=COLORS["accent"],
        )

    def _clear(self):
        """Reset the stage before drawing a new screen."""
        # Remove key bindings that only make sense on the previous screen
        self.unbind("1")
        self.unbind("2")
        self.unbind("3")
        self.unbind("<Return>")

        for w in self.stage.winfo_children():
            w.destroy()

    def _paint_bg(self):
        """Fill the window with the grid image if we have one."""
        if self.bg_image:
            tk.Label(self.stage, image=self.bg_image, borderwidth=0).place(
                x=0, y=0, relwidth=1, relheight=1
            )

    def _center_frame(self, y_rel=0.5, parent=None):
        """Create a fixed-size card anchored in the middle of the window."""
        host = parent or self.stage
        f = tk.Frame(host, bg=COLORS["panel"])
        f.place(relx=0.5, rely=y_rel, anchor="center")
        return f

    def _title(self, parent, text, size=40, fg=COLORS["pink"]):
        """Big heading helper so titles stay consistent."""
        lbl = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, "bold"),
            fg=fg,
            bg=COLORS["panel"],
        )
        lbl.pack(pady=(8, 14))
        return lbl

    # ---------- main screens ----------

    def displayHome(self):
        """Landing page with simple CTA."""
        self._clear()
        self._paint_bg()

        card = self._center_frame(0.50)
        card.config(width=750, height=300)
        card.pack_propagate(False)

        self._title(card, "MATHS QUIZ", size=42)
        tk.Label(
            card,
            text="Sharpen your skills with neon-powered addition & subtraction.",
            font=("Segoe UI", 15),
            fg=COLORS["muted"],
            bg=COLORS["panel"],
            wraplength=700,
        ).pack(pady=14)

        ttk.Button(
            card,
            text="Start Quiz",
            style="Primary.TButton",
            command=self.displayMenu,
        ).pack(pady=20)

    def displayMenu(self):
        """Difficulty selection screen + 1/2/3 shortcuts."""
        self._clear()
        self._paint_bg()

        card = self._center_frame(0.50)
        card.config(width=750, height=430)
        card.pack_propagate(False)

        self._title(card, "DIFFICULTY LEVEL", size=36)
        tk.Label(
            card,
            text="1) Easy = 1-digit   •   2) Moderate = 2-digit   •   3) Advanced = 4-digit",
            font=("Segoe UI", 13),
            fg=COLORS["muted"],
            bg=COLORS["panel"],
            wraplength=700,
        ).pack(pady=8)

        btns = tk.Frame(card, bg=COLORS["panel"])
        btns.pack(pady=18)

        def add_btn(label, cmd, style="Primary.TButton"):
            ttk.Button(btns, text=label, style=style, command=cmd).pack(
                pady=6, ipadx=14, ipady=3
            )

        add_btn("1. Easy", lambda: self._start_quiz(1))
        add_btn("2. Moderate", lambda: self._start_quiz(2))
        add_btn("3. Advanced", lambda: self._start_quiz(4))
        add_btn("Back to Home", self.displayHome, style="Ghost.TButton")

        # Number keys act as shortcuts only on this menu
        self.bind("1", lambda e: self._start_quiz(1))
        self.bind("2", lambda e: self._start_quiz(2))
        self.bind("3", lambda e: self._start_quiz(4))

    def displayProblem(self):
        """Show the current arithmetic problem and accept an answer."""
        self._clear()
        self._paint_bg()

        # Small HUD with question count and score
        hud = tk.Frame(self.stage, bg=COLORS["hud"])
        hud.place(relx=0.5, rely=0.12, anchor="center")

        tk.Label(
            hud,
            text=f"Question {self.q_index + 1} / 10",
            fg=COLORS["muted"],
            bg=COLORS["hud"],
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left", padx=10)

        self._hud_score = tk.Label(
            hud,
            text=f"Score: {self.score}",
            fg=COLORS["accent"],
            bg=COLORS["hud"],
            font=("Segoe UI", 11, "bold"),
        )
        self._hud_score.pack(side="left", padx=10)

        card = self._center_frame(0.60)
        card.config(width=750, height=430)
        card.pack_propagate(False)

        self._title(card, "SOLVE", size=32)

        tk.Label(
            card,
            text=f"{self.a} {self.op} {self.b} =",
            font=("Consolas", 52, "bold"),
            fg=COLORS["text"],
            bg=COLORS["panel"],
        ).pack(pady=(4, 8))

        # Input field + live echo label
        ans_var = tk.StringVar()

        entry = tk.Entry(
            card,
            width=12,
            font=("Consolas", 26),
            bg="#111633",
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief="flat",
            textvariable=ans_var,
            justify="center",
        )
        entry.pack()
        entry.focus_set()

        echo = tk.Label(
            card,
            text="Your answer: —",
            font=("Segoe UI", 11),
            fg=COLORS["muted"],
            bg=COLORS["panel"],
        )
        echo.pack(pady=8)

        def update_echo(*_):
            txt = ans_var.get().strip()
            echo.config(text=f"Your answer: {txt if txt else '—'}")

        ans_var.trace_add("write", update_echo)

        fb = tk.Label(
            card,
            text="",
            font=("Segoe UI", 11),
            fg=COLORS["muted"],
            bg=COLORS["panel"],
        )
        fb.pack(pady=6)

        correct_value = self.a + self.b if self.op == "+" else self.a - self.b

        def submit():
            """Handle one submission attempt for this question."""
            txt = ans_var.get().strip()
            try:
                user = int(txt)
            except ValueError:
                fb.config(text="Please enter a number.")
                return

            if self.isCorrect(user):
                # First try is worth more than second try
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
                    self.after(250, self._next_or_finish)

        ttk.Button(
            card,
            text="Submit",
            style="Action.TButton",
            command=submit,
        ).pack(pady=12, ipadx=12)

        # Enter key submits the answer
        self.bind("<Return>", lambda e: submit())

    def displayResults(self):
        """End-of-quiz screen with grade and replay option."""
        self._clear()
        self._paint_bg()

        card = self._center_frame(0.50)
        card.config(width=750, height=350)
        card.pack_propagate(False)

        self._title(card, "RESULTS", size=38)

        tk.Label(
            card,
            text=f"Final Score: {self.score} / 100",
            font=("Segoe UI", 20, "bold"),
            fg=COLORS["text"],
            bg=COLORS["panel"],
        ).pack(pady=6)

        tk.Label(
            card,
            text=f"Rank: {self._grade(self.score)}",
            font=("Segoe UI", 15, "bold"),
            fg=COLORS["muted"],
            bg=COLORS["panel"],
        ).pack(pady=6)

        btns = tk.Frame(card, bg=COLORS["panel"])
        btns.pack(pady=14)

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
        ).pack(pady=6, ipadx=14)

        # Soft nudge to play again
        self.after(300, self._prompt_replay)

    # ---------- quiz flow ----------

    def _prompt_replay(self):
        if messagebox.askyesno("Play again?", "Would you like another round?"):
            self.displayMenu()

    def _start_quiz(self, digits):
        """Initialise a new 10-question round for the chosen difficulty."""
        self.digits = digits
        self.q_index = 0
        self.score = 0
        self.first_try = True
        self._new_problem()
        self.displayProblem()

    def _new_problem(self):
        """Pick two numbers and an operator based on difficulty."""
        self.a = self.randomInt(self.digits)
        self.b = self.randomInt(self.digits)
        self.op = self.decideOperation()

    def _next_or_finish(self):
        """Move to the next question or show results if we reached 10."""
        self.q_index += 1
        self.first_try = True

        if self.q_index >= 10:
            self.displayResults()
        else:
            self._new_problem()
            self.displayProblem()

    # ---------- core logic required by the brief ----------

    def randomInt(self, digits):
        """Return a random integer, range depends on the difficulty setting."""
        if digits == 1:
            return random.randint(0, 9)
        if digits == 2:
            return random.randint(10, 99)
        if digits == 4:
            return random.randint(1000, 9999)
        # Fallback, should never really be hit
        return 0

    def decideOperation(self):
        """Randomly choose between addition and subtraction."""
        return random.choice(["+", "-"])

    def isCorrect(self, user_answer):
        """Compare user’s answer to the correct result."""
        correct = self.a + self.b if self.op == "+" else self.a - self.b
        return user_answer == correct

    @staticmethod
    def _grade(score):
        """Simple letter grade mapping based on final score."""
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
