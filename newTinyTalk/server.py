"""
TinyTalk API Server + IDE
Flask-based HTTP API for running TinyTalk code, plus a web-based IDE.

Endpoints:
    GET  /               Web IDE
    POST /api/run        Execute TinyTalk code
    GET  /api/health     Health check
    GET  /api/examples   List example programs
"""

import os
from flask import Flask, request, jsonify, send_from_directory

from .kernel import TinyTalkKernel
from .runtime import ExecutionBounds

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

app = Flask(__name__, static_folder=STATIC_DIR)

# Bounded execution for API requests (stricter than CLI)
API_BOUNDS = ExecutionBounds(
    max_ops=500_000,
    max_iterations=50_000,
    max_recursion=500,
    timeout_seconds=10.0,
)


@app.route("/")
def ide():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "2.0.0", "language": "TinyTalk"})


@app.route("/api/run", methods=["POST"])
def run_code():
    data = request.get_json(force=True, silent=True) or {}
    source = data.get("code", data.get("source", ""))

    if not source:
        return jsonify({"success": False, "error": "No code provided"}), 400

    kernel = TinyTalkKernel(bounds=API_BOUNDS)
    result = kernel.run(source)

    return jsonify({
        "success": result.success,
        "output": result.output,
        "error": result.error or None,
        "elapsed_ms": result.elapsed_ms,
        "op_count": result.op_count,
    })


@app.route("/api/examples", methods=["GET"])
def examples():
    examples_dir = os.path.join(os.path.dirname(__file__), "examples")
    result = []
    if os.path.isdir(examples_dir):
        for fname in sorted(os.listdir(examples_dir)):
            if fname.endswith(".tt"):
                with open(os.path.join(examples_dir, fname)) as f:
                    result.append({
                        "name": fname.replace(".tt", ""),
                        "filename": fname,
                        "code": f.read(),
                    })
    return jsonify(result)


def create_app():
    """Factory function for WSGI servers."""
    return app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555, debug=True)
