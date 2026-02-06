#!/usr/bin/env python3
"""
Newton Interface Builder - Dedicated launcher for Interface Builder service.

This is a shortcut to run: newton serve --app interface-builder
"""

import sys
import os

# Add the newton_sdk to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'newton_sdk'))

from newton_sdk.cli import main

# Modify sys.argv to simulate "newton serve --app interface-builder"
sys.argv = ['newton', 'serve', '--app', 'interface-builder'] + sys.argv[1:]

if __name__ == "__main__":
    main()