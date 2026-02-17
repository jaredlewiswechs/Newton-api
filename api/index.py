"""
Vercel serverless entry point for realTinyTalk.

Exposes the Flask-based TinyTalk Web IDE as a Vercel serverless function.
Vercel's @vercel/python runtime detects the `app` variable at module level.
"""
import sys
import os
import traceback
from pathlib import Path

# Ensure the repo root is on the import path so `realTinyTalk` resolves.
repo_root = str(Path(__file__).parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

os.environ.setdefault("VERCEL", "1")

IMPORT_ERROR = None
IMPORT_TRACEBACK = None

try:
    from realTinyTalk.web.server import app  # noqa: E402
except Exception as exc:
    IMPORT_ERROR = exc
    IMPORT_TRACEBACK = traceback.format_exc()

    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route("/")
    @app.route("/health")
    def startup_error():
        details = {
            "status": "error",
            "error": "realTinyTalk failed to start",
            "exception_type": type(IMPORT_ERROR).__name__,
            "exception_message": str(IMPORT_ERROR),
        }
        if os.environ.get("VERCEL") == "1":
            details["traceback"] = IMPORT_TRACEBACK
        return jsonify(details), 500

# Vercel looks for `app` at module level — already satisfied above.
handler = app
