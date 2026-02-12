"""
Vercel serverless function entry point for Newton Voice Interface.

Exports the FastAPI app as an ASGI application for Vercel's @vercel/python runtime.
"""
import sys
import os
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Ensure parent directory is on the import path so app.py and core/ can be resolved.
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Set environment marker so the app knows it's running on Vercel
os.environ.setdefault("VERCEL", "1")

# Import the FastAPI app. If import fails on Vercel (missing dependency,
# packaging issue, etc.), keep the function alive and return a structured
# error response instead of a generic "Function Invocation Failed" crash page.
IMPORT_ERROR = None
IMPORT_TRACEBACK = None

try:
    from app import app  # noqa: E402
except Exception as exc:
    IMPORT_ERROR = exc
    IMPORT_TRACEBACK = traceback.format_exc()
    app = FastAPI(title="Newton Voice Interface - Startup Error")

    @app.get("/")
    @app.get("/health")
    async def startup_error():
        details = {
            "status": "error",
            "error": "Newton Voice Interface failed to start",
            "exception_type": type(IMPORT_ERROR).__name__,
            "exception_message": str(IMPORT_ERROR),
        }
        if os.environ.get("VERCEL") == "1":
            details["traceback"] = IMPORT_TRACEBACK
        return JSONResponse(status_code=500, content=details)

# Vercel's @vercel/python runtime looks for `app` (ASGI) at module level.
handler = app
