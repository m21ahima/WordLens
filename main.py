"""
WordLens - System-wide highlight-to-meaning tool
Entry point: starts the clipboard listener and overlay manager
"""

import threading
import sys
from listener import ClipboardListener
from overlay import OverlayManager


def main():
    print("📖 WordLens is running...")
    print("   Highlight any word in any app to see its meaning.")
    print("   Press Ctrl+C to quit.\n")

    overlay_manager = OverlayManager()
    listener = ClipboardListener(on_word_selected=overlay_manager.show_definition)

    # Run listener in background thread
    listener_thread = threading.Thread(target=listener.start, daemon=True)
    listener_thread.start()

    # Run overlay (tkinter must be on main thread)
    try:
        overlay_manager.run()
    except KeyboardInterrupt:
        print("\n👋 WordLens stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()