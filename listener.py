"""
listener.py - Watches the clipboard for newly selected/copied single words
Fires a callback whenever a clean single word is detected
"""

import time
import threading
import pyperclip
import re


class ClipboardListener:
    def __init__(self, on_word_selected):
        self.on_word_selected = on_word_selected
        self._last_text = ""
        self._running = False
        self._debounce_timer = None
        self._debounce_delay = 0.4  # seconds — wait for user to finish selecting

    def start(self):
        """Start polling the clipboard for changes."""
        self._running = True
        # Seed with current clipboard so we don't trigger on launch
        try:
            self._last_text = pyperclip.paste()
        except Exception:
            self._last_text = ""

        while self._running:
            try:
                current = pyperclip.paste()
                if current != self._last_text:
                    self._last_text = current
                    self._schedule_check(current)
            except Exception:
                pass
            time.sleep(0.2)

    def stop(self):
        self._running = False

    def _schedule_check(self, text):
        """Debounce: only process after user stops changing selection."""
        if self._debounce_timer:
            self._debounce_timer.cancel()
        self._debounce_timer = threading.Timer(
            self._debounce_delay, self._process_text, args=[text]
        )
        self._debounce_timer.start()

    def _process_text(self, text):
        cleaned = text.strip()
        word = self._extract_single_word(cleaned)
        if word:
            self.on_word_selected(word)

    def _extract_single_word(self, text):
        """
        Returns the word if text is a single dictionary word (letters only, optional hyphen).
        Returns None for phrases, sentences, numbers, or garbage.
        """
        # Remove surrounding punctuation/quotes
        text = text.strip("\"'.,;:!?()[]{}""''")
        # Allow hyphenated words like "well-being"
        pattern = r"^[A-Za-z][A-Za-z\-']*[A-Za-z]$|^[A-Za-z]{1,2}$"
        if re.match(pattern, text) and len(text) >= 2 and len(text) <= 45:
            return text.lower()
        return None