"""
run_app.py
~~~~~~~~~~
Entrypoint launcher for Drama Downloader Studio GUI Application.
"""

import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from drama_downloader.gui import run_gui

if __name__ == "__main__":
    run_gui()
