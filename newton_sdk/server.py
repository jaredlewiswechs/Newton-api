"""
═══════════════════════════════════════════════════════════════════════════════
 Newton Server Launcher
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys


def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Start the Newton Supercomputer server.

    Usage:
        from newton_sdk import serve
        serve(port=8000)

    Or from command line:
        newton serve --port 8000
    """
    # Add root directory to path
    sdk_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(sdk_dir)

    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    try:
        import uvicorn
        from newton_supercomputer import app

        print(f"""
═══════════════════════════════════════════════════════════════════════════════
 NEWTON SUPERCOMPUTER v1.0.0
 Verified Computation Engine
═══════════════════════════════════════════════════════════════════════════════

 Server starting at http://{host}:{port}

 Endpoints:
   POST /calculate  - Verified computation
   POST /verify     - Content safety
   POST /constraint - CDL evaluation
   POST /ask        - Full pipeline
   GET  /health     - System status

 Press Ctrl+C to stop
═══════════════════════════════════════════════════════════════════════════════
""")

        uvicorn.run(
            "newton_supercomputer:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )

    except ImportError as e:
        print(f"""
Error: Server dependencies not installed.

Install with:
    pip install newton-sdk[server]

Or install manually:
    pip install fastapi uvicorn pydantic cryptography

Details: {e}
""")
        sys.exit(1)
