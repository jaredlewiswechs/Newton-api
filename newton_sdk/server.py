"""
═══════════════════════════════════════════════════════════════════════════════
 Newton Server Launcher
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys


def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = False, app: str = "main"):
    """
    Start the Newton Supercomputer server.

    Args:
        host: Host to bind to
        port: Port to listen on
        reload: Enable auto-reload for development
        app: Which app to serve ('main', 'teachers-aide', 'interface-builder', 'jester', 'demo')

    Usage:
        from newton_sdk import serve
        serve(port=8000, app='teachers-aide')

    Or from command line:
        newton serve --app teachers-aide --port 8000
    """
    # Add root directory to path
    sdk_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(sdk_dir)

    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    try:
        import uvicorn

        # Select which app to serve
        if app == "main":
            from newton_supercomputer import app
            app_module = "newton_supercomputer"
        elif app == "teachers-aide":
            from demo.teachers_aide_service import app
            app_module = "demo.teachers_aide_service"
        elif app == "interface-builder":
            # For now, fall back to main app - could be extended
            from newton_supercomputer import app
            app_module = "newton_supercomputer"
        elif app == "jester":
            # For now, fall back to main app - could be extended
            from newton_supercomputer import app
            app_module = "newton_supercomputer"
        elif app == "demo":
            from demo.teachers_aide_service import app
            app_module = "demo.teachers_aide_service"
        else:
            print(f"Unknown app: {app}")
            sys.exit(1)

        print(f"""
═══════════════════════════════════════════════════════════════════════════════
 NEWTON SUPERCOMPUTER v1.0.0 - {app.title()} App
 Verified Computation Engine
═══════════════════════════════════════════════════════════════════════════════

 App: {app}
 Module: {app_module}
 Server starting at http://{host}:{port}

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
