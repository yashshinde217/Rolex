"""
main.py — Rolex Entry Point

Launches the GUI (orb + chat panel) with all AI modules running
in a background thread.

Run:
    python src/main.py

Press Ctrl+C or say "exit" to stop.
"""

import os
import sys

# Make sure src/ is on path so all sibling imports work
sys.path.insert(0, os.path.dirname(__file__))

from gui.app import RolexApp


if __name__ == "__main__":
    app = RolexApp()
    app.run()