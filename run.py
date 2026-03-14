#!/usr/bin/env python
"""Uncapped Production Control - Entry Point"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from app.config import config


def main():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║   UNCAPPED Production Control        ║")
    print("  ║   Starting server...                 ║")
    print("  ╚══════════════════════════════════════╝")
    print()

    uvicorn.run(
        "app.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
