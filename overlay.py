"""
overlay.py - Floating definition card that appears near the cursor.
Built with tkinter: always-on-top, borderless, auto-dismisses.
"""

import tkinter as tk
import threading
from dictionary import get_definition

# ── Palette ────────────────────────────────────────────────────────────────
BG          = "#1C1C1E"       # dark card background
ACCENT      = "#F5A623"       # warm amber — the "ink" colour
TEXT_MAIN   = "#F2F2F7"       # near-white
TEXT_SUB    = "#8E8E93"       # muted gray
TAG_BG      = "#2C2C2E"       # pill background
BORDER      = "#3A3A3C"       # card border
CLOSE_BG    = "#3A3A3C"
CLOSE_HOVER = "#FF453A"

FONT_WORD   = ("Georgia", 18, "bold")
FONT_PHON   = ("Georgia", 11, "italic")
FONT_TAG    = ("Helvetica", 9, "bold")
FONT_DEF    = ("Helvetica", 12)
FONT_POS    = ("Helvetica", 10, "italic")
FONT_ERR    = ("Helvetica", 11, "italic")
FONT_CLOSE  = ("Helvetica", 11, "bold")

CARD_WIDTH  = 340
PAD         = 18
CORNER      = 14
AUTO_CLOSE  = 8000   # ms — auto-dismiss after 8 seconds


class OverlayManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()          # hidden until needed
        self._window = None
        self._auto_close_id = None
        self._lock = threading.Lock()

    # ── Public API ──────────────────────────────────────────────────────────

    def show_definition(self, word: str):
        """Called from the listener thread — schedules UI work on main thread."""
        self.root.after(0, lambda: self._fetch_and_show(word))

    def run(self):
        self.root.mainloop()

    # ── Internal ────────────────────────────────────────────────────────────

    def _fetch_and_show(self, word: str):
        # Close any existing card first
        self._close_card()

        # Show a loading card immediately
        self._build_card({"word": word, "phonetic": "", "meanings": [], "error": None},
                         loading=True)

        # Fetch in background, then update
        def fetch():
            result = get_definition(word)
            self.root.after(0, lambda: self._update_card(result))

        threading.Thread(target=fetch, daemon=True).start()

    def _build_card(self, data: dict, loading=False):
        x, y = self._cursor_position()

        win = tk.Toplevel(self.root)
        win.overrideredirect(True)          # borderless
        win.attributes("-topmost", True)    # always on top
        win.configure(bg=BG)

        # ── Outer frame (acts as border) ────────────────────────────────────
        outer = tk.Frame(win, bg=BORDER, padx=1, pady=1)
        outer.pack(fill="both", expand=True)

        card = tk.Frame(outer, bg=BG, padx=PAD, pady=PAD)
        card.pack(fill="both", expand=True)

        # ── Header row: word + close button ─────────────────────────────────
        header = tk.Frame(card, bg=BG)
        header.pack(fill="x", pady=(0, 4))

        word_label = tk.Label(
            header, text=data["word"], font=FONT_WORD,
            fg=ACCENT, bg=BG, anchor="w"
        )
        word_label.pack(side="left")

        close_btn = tk.Label(
            header, text="✕", font=FONT_CLOSE,
            fg=TEXT_SUB, bg=CLOSE_BG,
            padx=7, pady=2, cursor="hand2"
        )
        close_btn.pack(side="right", padx=(8, 0))
        close_btn.bind("<Button-1>", lambda e: self._close_card())
        close_btn.bind("<Enter>",    lambda e: close_btn.config(fg="white", bg=CLOSE_HOVER))
        close_btn.bind("<Leave>",    lambda e: close_btn.config(fg=TEXT_SUB, bg=CLOSE_BG))

        # ── Phonetic ─────────────────────────────────────────────────────────
        if data.get("phonetic"):
            tk.Label(card, text=data["phonetic"], font=FONT_PHON,
                     fg=TEXT_SUB, bg=BG, anchor="w").pack(fill="x", pady=(0, 8))

        # ── Divider ──────────────────────────────────────────────────────────
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=(2, 10))

        # ── Body ─────────────────────────────────────────────────────────────
        if loading:
            tk.Label(card, text="Looking up…", font=FONT_ERR,
                     fg=TEXT_SUB, bg=BG, anchor="w").pack(fill="x")

        elif data.get("error"):
            tk.Label(card, text=data["error"], font=FONT_ERR,
                     fg="#FF453A", bg=BG, anchor="w",
                     wraplength=CARD_WIDTH - PAD * 2, justify="left"
                     ).pack(fill="x")

        else:
            for meaning in data.get("meanings", []):
                # Part-of-speech pill
                pos_row = tk.Frame(card, bg=BG)
                pos_row.pack(fill="x", pady=(0, 4))

                pill = tk.Label(
                    pos_row, text=meaning["part_of_speech"].upper(),
                    font=FONT_TAG, fg=ACCENT, bg=TAG_BG,
                    padx=7, pady=2
                )
                pill.pack(side="left")

                # Definitions
                for i, defn in enumerate(meaning["definitions"], 1):
                    defn_frame = tk.Frame(card, bg=BG)
                    defn_frame.pack(fill="x", pady=(0, 3))

                    if len(meaning["definitions"]) > 1:
                        tk.Label(defn_frame, text=f"{i}.", font=FONT_DEF,
                                 fg=TEXT_SUB, bg=BG, anchor="nw",
                                 width=2).pack(side="left", anchor="nw")

                    tk.Label(defn_frame, text=defn, font=FONT_DEF,
                             fg=TEXT_MAIN, bg=BG, anchor="w",
                             wraplength=CARD_WIDTH - PAD * 2 - 18,
                             justify="left").pack(side="left", fill="x", expand=True)

                # Small spacer between meanings
                tk.Frame(card, bg=BG, height=6).pack()

        # ── Hide hint ────────────────────────────────────────────────────────
        hint_row = tk.Frame(card, bg=BG)
        hint_row.pack(fill="x", pady=(6, 0))
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x")
        tk.Label(card, text="click ✕ or anywhere outside to dismiss",
                 font=("Helvetica", 8), fg="#636366", bg=BG
                 ).pack(pady=(5, 0))

        # ── Position window ──────────────────────────────────────────────────
        win.update_idletasks()
        w = win.winfo_reqwidth()
        h = win.winfo_reqheight()
        sx = win.winfo_screenwidth()
        sy = win.winfo_screenheight()

        # Offset slightly below cursor; flip if near edge
        cx = min(x + 14, sx - w - 10)
        cy = y + 24
        if cy + h > sy - 40:
            cy = y - h - 10

        win.geometry(f"+{cx}+{cy}")

        # Click-outside to dismiss
        win.bind("<FocusOut>", lambda e: self._close_card())
        card.bind("<Button-1>", lambda e: None)   # absorb clicks on card itself
        win.bind("<Button-1>", lambda e: None)

        self._window = win

        # Auto-close
        self._auto_close_id = self.root.after(AUTO_CLOSE, self._close_card)

    def _update_card(self, data: dict):
        """Replace loading card with real definition."""
        self._close_card(cancel_auto=True)
        self._build_card(data)

    def _close_card(self, cancel_auto=False, *_):
        if self._auto_close_id:
            self.root.after_cancel(self._auto_close_id)
            self._auto_close_id = None
        if self._window:
            try:
                self._window.destroy()
            except Exception:
                pass
            self._window = None

    def _cursor_position(self):
        try:
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            return x, y
        except Exception:
            return 100, 100