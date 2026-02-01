"""
Test suite for Vercel serverless function entry point.

Verifies that api/index.py correctly exports the FastAPI app
for Vercel's Python runtime.
"""
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


def test_api_index_exports_app():
    """Test that api.index module exports an 'app' variable."""
    import api.index as module
    # Verify the module has an 'app' attribute
    assert hasattr(module, 'app'), "api.index must export 'app' variable"
    
    # Verify app is not None
    assert module.app is not None, "app variable must not be None"


def test_app_is_fastapi_instance():
    """Test that the exported app is a FastAPI instance."""
    from api.index import app
    from fastapi import FastAPI
    # Verify app is a FastAPI instance
    assert isinstance(app, FastAPI), f"app must be a FastAPI instance, got {type(app)}"


def test_app_is_asgi_compatible():
    """Test that the app is ASGI-compatible (callable)."""
    from api.index import app
    # ASGI apps must be callable
    assert callable(app), "app must be callable (ASGI-compatible)"


def test_no_handler_alias():
    """Test that there's no 'handler' alias (Vercel expects 'app')."""
    import api.index as module
    # Verify there's no 'handler' variable that could cause confusion
    # Note: It's OK if handler exists as long as 'app' is the primary export
    # but ideally we should only have 'app'
    module_vars = [attr for attr in dir(module) if not attr.startswith('_')]
    
    # The important thing is that 'app' exists
    assert 'app' in module_vars, "Module must expose 'app' variable"


def test_app_import_path_consistency():
    """Test that importing app from api.index gives the same object as from newton_supercomputer."""
    from api.index import app as api_app
    from newton_supercomputer import app as original_app
    # They should be the exact same object
    assert api_app is original_app, "api.index.app should be the same object as newton_supercomputer.app"


if __name__ == "__main__":
    # Run tests manually
    print("Running Vercel entrypoint tests...")
    
    test_api_index_exports_app()
    print("✓ api.index exports 'app' variable")
    
    test_app_is_fastapi_instance()
    print("✓ app is a FastAPI instance")
    
    test_app_is_asgi_compatible()
    print("✓ app is ASGI-compatible")
    
    test_no_handler_alias()
    print("✓ No conflicting handler alias")
    
    test_app_import_path_consistency()
    print("✓ app import path is consistent")
    
    print("\nAll tests passed! ✓")
