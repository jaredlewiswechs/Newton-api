"""
Vercel serverless function entry point for Foghorn API.

Exports the FastAPI app as an ASGI application for Vercel's @vercel/python runtime.
All routes defined in foghorn.api are exposed through this single serverless function.

Vercel expects:
  - An `app` variable (ASGI application) for FastAPI/Starlette
  - OR a `handler` function for WSGI

We export `app` (the FastAPI ASGI app).
"""
import sys
import os
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Ensure parent directory is on the import path so foghorn and dependencies can be resolved.
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Set environment marker so the app knows it's running on Vercel
os.environ.setdefault("VERCEL", "1")

IMPORT_ERROR = None
IMPORT_TRACEBACK = None

try:
    from foghorn.api import mount_foghorn_api
    app = FastAPI(title="Foghorn API (Vercel)")
    mount_foghorn_api(app)
except Exception as exc:
    IMPORT_ERROR = exc
    IMPORT_TRACEBACK = traceback.format_exc()
    app = FastAPI(title="Foghorn API - Startup Error")

    @app.get("/")
    @app.get("/health")
    async def startup_error():
        details = {
            "status": "error",
            "error": "Foghorn API failed to start",
            "exception_type": type(IMPORT_ERROR).__name__,
            "exception_message": str(IMPORT_ERROR),
        }
        if os.environ.get("VERCEL") == "1":
            details["traceback"] = IMPORT_TRACEBACK
        return JSONResponse(status_code=500, content=details)

# Vercel's @vercel/python runtime looks for `app` (ASGI) at module level.
# The import above satisfies this. No additional handler alias is needed.
