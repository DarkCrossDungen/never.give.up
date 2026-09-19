"""
TerraPulse Standalone Launcher
==============================
Launches the TerraPulse FastAPI backend on port 8000 and automatically
opens the interactive web dashboard in your default browser.
Zero API keys required — runs 100% locally with open agrometeorology!
"""

import os
import sys
import webbrowser
import threading
import time

# Ensure backend directory is in the Python search path
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import uvicorn
from main import app


def open_browser():
    """Wait for Uvicorn to bind port and launch the browser."""
    time.sleep(1.2)
    url = "http://localhost:8000"
    print(f"\n[TerraPulse] Opening dashboard at: {url}\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass


if __name__ == "__main__":
    print("=" * 65)
    print("  TERRAPULSE — Earth Forward Geospatial Precision Agronomy")
    print("  Built for NextStep Hacks 2026")
    print("  Starting server at http://127.0.0.1:8000 ...")
    print("=" * 65)

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
