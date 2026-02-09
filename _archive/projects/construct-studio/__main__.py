#!/usr/bin/env python3
"""
Construct Studio CLI Entry Point
================================

Run with: python -m construct_studio

Commands:
    python -m construct_studio           Start REPL
    python -m construct_studio demo      Run demos
    python -m construct_studio version   Show version
"""

from .cli import main

if __name__ == "__main__":
    main()
