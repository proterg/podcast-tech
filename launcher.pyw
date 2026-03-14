"""
Uncapped Production Control - Desktop Launcher
Double-click this to start the server and open the dashboard.
Runs silently (no console window). Close via system tray or task manager.
"""

import subprocess
import sys
import os
import time
import webbrowser
import urllib.request
import tkinter as tk
from tkinter import messagebox

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable  # pythonw.exe when run as .pyw
# We need the console python.exe for uvicorn, not pythonw.exe
PYTHON_DIR = os.path.dirname(PYTHON)
PYTHON_CONSOLE = os.path.join(PYTHON_DIR, "python.exe")
if not os.path.exists(PYTHON_CONSOLE):
    PYTHON_CONSOLE = PYTHON

PORT = 8080
URL = f"http://localhost:{PORT}"
LOG_FILE = os.path.join(SCRIPT_DIR, "server.log")


def is_server_running():
    try:
        urllib.request.urlopen(f"{URL}/api/status", timeout=2)
        return True
    except Exception:
        return False


def start_server():
    """Start the FastAPI server as a background process."""
    log = open(LOG_FILE, "w")
    proc = subprocess.Popen(
        [PYTHON_CONSOLE, "-u", "run.py"],
        cwd=SCRIPT_DIR,
        stdout=log,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    return proc


def wait_for_server(proc, timeout=15):
    """Wait until the server responds or times out."""
    start = time.time()
    while time.time() - start < timeout:
        if proc.poll() is not None:
            return False  # Process died
        if is_server_running():
            return True
        time.sleep(0.5)
    return False


def main():
    # Check if already running
    if is_server_running():
        webbrowser.open(URL)
        return

    # Start server
    proc = start_server()

    # Wait for it to be ready
    if not wait_for_server(proc):
        # Server failed to start - show error
        root = tk.Tk()
        root.withdraw()
        log_tail = ""
        try:
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
                log_tail = "".join(lines[-20:])
        except Exception:
            pass
        messagebox.showerror(
            "Uncapped - Startup Error",
            f"Server failed to start.\n\n{log_tail}"
        )
        root.destroy()
        return

    # Open browser
    webbrowser.open(URL)

    # Keep running as a tray-like presence using a hidden tkinter window
    # This keeps the launcher alive so the server subprocess stays alive
    root = tk.Tk()
    root.title("Uncapped Production Control")
    root.geometry("300x120")
    root.resizable(False, False)
    root.configure(bg="#1a1a2e")
    root.protocol("WM_DELETE_WINDOW", lambda: shutdown(root, proc))

    # Minimize to taskbar immediately
    root.iconify()

    label = tk.Label(
        root,
        text="UNCAPPED\nProduction Control\n\nServer running on localhost:8080\nClose this window to stop.",
        bg="#1a1a2e", fg="#e0e0e0",
        font=("Segoe UI", 10),
        justify="center",
    )
    label.pack(expand=True)

    root.mainloop()


def shutdown(root, proc):
    """Clean shutdown: kill server, close window."""
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    root.destroy()


if __name__ == "__main__":
    main()
