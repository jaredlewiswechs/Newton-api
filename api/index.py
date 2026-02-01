"""
Vercel serverless function entry point for Newton Supercomputer.
This module exports the FastAPI app for Vercel's Python runtime.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import newton_supercomputer
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the FastAPI app
from newton_supercomputer import app

# Export for Vercel
# Vercel's Python runtime expects an 'app' variable for ASGI applications
handler = app
