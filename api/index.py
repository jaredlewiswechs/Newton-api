"""
Vercel serverless function entry point for Newton Supercomputer.

This module exports the FastAPI app as an ASGI application for Vercel's
@vercel/python runtime. All routes defined in newton_supercomputer.py
are exposed through this single serverless function.

Vercel expects:
  - An `app` variable (ASGI application) for FastAPI/Starlette
  - OR a `handler` function for WSGI

We export `app` (the FastAPI ASGI app).
"""
import sys
import os
from pathlib import Path

# Ensure parent directory is on the import path so newton_supercomputer
# and its dependencies (core/, tinytalk_py/, parccloud/) can be resolved.
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Set environment marker so the app knows it's running on Vercel
os.environ.setdefault("VERCEL", "1")

# Import the FastAPI app
from newton_supercomputer import app  # noqa: E402

# Vercel's @vercel/python runtime looks for `app` (ASGI) at module level.
# The import above satisfies this. No additional handler alias is needed.

# Export handler alias for compatibility with some Vercel Python runtimes
handler = app
