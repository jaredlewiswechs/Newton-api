#!/usr/bin/env python3
"""
Newton Teachers Aide - Dedicated launcher for Teachers Aide service.

This is a shortcut to run: newton serve --app teachers-aide
"""

import sys
import os

# Add the newton_sdk to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'newton_sdk'))

from newton_sdk.cli import main

# Modify sys.argv to simulate "newton serve --app teachers-aide"
sys.argv = ['newton', 'serve', '--app', 'teachers-aide'] + sys.argv[1:]

if __name__ == "__main__":
    main()