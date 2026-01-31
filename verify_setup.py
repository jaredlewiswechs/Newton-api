#!/usr/bin/env python3
"""
Quick setup verification script for Newton.
Run this after setup to ensure everything works.
"""

import sys
import subprocess
import importlib.util

def check(name, test_func, fix_suggestion=""):
    """Check a requirement and print result."""
    try:
        result = test_func()
        if result:
            print(f"✓ {name}")
            return True
        else:
            print(f"✗ {name}")
            if fix_suggestion:
                print(f"  → {fix_suggestion}")
            return False
    except Exception as e:
        print(f"✗ {name}: {e}")
        if fix_suggestion:
            print(f"  → {fix_suggestion}")
        return False

def main():
    print("=" * 70)
    print(" Newton Setup Verification")
    print("=" * 70)
    print()
    
    checks_passed = 0
    total_checks = 0
    
    # Check Python version
    total_checks += 1
    if check("Python 3.9+", 
             lambda: sys.version_info >= (3, 9),
             "Install Python 3.9 or higher"):
        checks_passed += 1
    
    # Check pip
    total_checks += 1
    if check("pip installed",
             lambda: subprocess.run(["pip", "--version"], 
                                   capture_output=True).returncode == 0,
             "Install pip: python3 -m ensurepip"):
        checks_passed += 1
    
    # Check virtual environment
    total_checks += 1
    if check("Virtual environment active",
             lambda: hasattr(sys, 'real_prefix') or 
                    (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix),
             "Run: source venv/bin/activate"):
        checks_passed += 1
    
    # Check FastAPI
    total_checks += 1
    if check("FastAPI installed",
             lambda: importlib.util.find_spec("fastapi") is not None,
             "Run: pip install -r requirements.txt"):
        checks_passed += 1
    
    # Check Uvicorn
    total_checks += 1
    if check("Uvicorn installed",
             lambda: importlib.util.find_spec("uvicorn") is not None,
             "Run: pip install -r requirements.txt"):
        checks_passed += 1
    
    # Check Pydantic
    total_checks += 1
    if check("Pydantic installed",
             lambda: importlib.util.find_spec("pydantic") is not None,
             "Run: pip install -r requirements.txt"):
        checks_passed += 1
    
    # Check pytest
    total_checks += 1
    if check("Pytest installed",
             lambda: importlib.util.find_spec("pytest") is not None,
             "Run: pip install pytest"):
        checks_passed += 1
    
    # Check main server file
    total_checks += 1
    import os
    if check("newton_supercomputer.py exists",
             lambda: os.path.exists("newton_supercomputer.py"),
             "Make sure you're in the Newton-api directory"):
        checks_passed += 1
    
    # Check requirements.txt
    total_checks += 1
    if check("requirements.txt exists",
             lambda: os.path.exists("requirements.txt"),
             "Make sure you're in the Newton-api directory"):
        checks_passed += 1
    
    print()
    print("=" * 70)
    print(f" Results: {checks_passed}/{total_checks} checks passed")
    print("=" * 70)
    print()
    
    if checks_passed == total_checks:
        print("🎉 All checks passed! Newton is ready to use.")
        print()
        print("Next steps:")
        print("  1. Start the server: python newton_supercomputer.py")
        print("  2. In another terminal: curl http://localhost:8000/health")
        print("  3. Read QUICKSTART.md for more examples")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print()
        print("Need help? Check GETTING_STARTED.md for troubleshooting.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
