"""
Vercel serverless function entry point for Newton Supercomputer.
This module exports the FastAPI app for Vercel's Python runtime.

Note: If imports fail, Vercel will display the error in the build logs.
Ensure all dependencies in requirements.txt are compatible with Vercel's Python runtime.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import newton_supercomputer
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the FastAPI app
# This will fail at build time if newton_supercomputer.py has issues
# Vercel's Python runtime expects an 'app' variable for ASGI applications
from newton_supercomputer import app

# The 'app' variable is automatically exported for Vercel
# No need to rename it - Vercel will use it directly
