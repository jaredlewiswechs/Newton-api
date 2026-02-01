"""
Vercel serverless function entry point for Newton Supercomputer.
This module exports the FastAPI app for Vercel's Python runtime.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import newton_supercomputer
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app
from newton_supercomputer import app

# Vercel expects a variable named 'app' to be exported
# This is already done by the import above
