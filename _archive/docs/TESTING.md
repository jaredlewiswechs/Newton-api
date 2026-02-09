# Newton Supercomputer - Testing Guide

```
    ╭──────────────────────────────────────────────────────────────╮
    │                                                              │
    │   Testing Newton - Full System Validation                   │
    │                                                              │
    │   "The constraint IS the instruction."                      │
    │   "The verification IS the computation."                    │
    │                                                              │
    ╰──────────────────────────────────────────────────────────────╯
```

**Complete testing guide for Newton Supercomputer API**

This guide covers everything you need to test Newton on any platform - Windows, macOS, or Linux.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Test Suites](#test-suites)
- [Windows-Specific Instructions](#windows-specific-instructions)
- [Troubleshooting](#troubleshooting)
- [Understanding Test Results](#understanding-test-results)
- [Writing Your Own Tests](#writing-your-own-tests)

---

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Internet connection (for first-time setup)

### Verify Python Installation

```bash
# Check Python version
python --version    # Windows
python3 --version   # macOS/Linux

# Should show Python 3.9.x or higher
```

### Install Newton

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# Install dependencies
pip install -r requirements.txt

# Install Newton SDK in editable mode
pip install -e .
```

---

## Running Tests

Newton has three levels of testing:

### 1. Quick System Test (10 tests, ~5 seconds)

Tests the core features to verify Newton is working.

**Terminal 1** - Start the server:
```bash
# Windows Command Prompt
python newton_supercomputer.py

# Windows PowerShell
python .\newton_supercomputer.py

# macOS/Linux
python3 newton_supercomputer.py
```

**Terminal 2** - Run the test:
```bash
# Windows
python test_full_system.py

# macOS/Linux
python3 test_full_system.py
```

**Expected Output:**
```
═══════════════════════════════════════════════════════════════
              NEWTON FULL SYSTEM TEST
═══════════════════════════════════════════════════════════════

✓ Health Check: 2.31ms
✓ Forge Verification: 1.85ms
✓ CDL Constraint: 0.92ms
✓ Logic Engine: 1.23ms
✓ Ledger: 1.45ms
✓ Cartridge Auto: 3.21ms
✓ Rosetta Compiler: 2.87ms
✓ Visual Cartridge: 2.54ms
✓ Robust Statistics: 1.67ms
✓ Ratio Constraint (f/g): 1.02ms

═══════════════════════════════════════════════════════════════
  RESULTS: 10/10 tests passed
  ✓ ALL SYSTEMS OPERATIONAL

  Newton is ready. The constraint IS the instruction.
  1 == 1.
═══════════════════════════════════════════════════════════════
```

### 2. Comprehensive System Test (80+ tests, ~30 seconds)

Tests ALL features, endpoints, and components.

**Terminal 1** - Start the server (same as above)

**Terminal 2** - Run comprehensive tests:
```bash
# Windows
python test_comprehensive_system.py

# macOS/Linux
python3 test_comprehensive_system.py
```

This tests:
- ✓ Core Verification Components (CDL, Logic, Forge, Vault, Ledger)
- ✓ All 118+ API Endpoints
- ✓ Cartridge System (Visual, Sound, Sequence, Data, Rosetta, Auto)
- ✓ Statistics & Robust Methods
- ✓ Grounding & Evidence
- ✓ Merkle Proofs & Audit Trail
- ✓ Policy Engine
- ✓ Negotiator
- ✓ Education Features (TEKS, Assessments, Classrooms)
- ✓ Voice Interface
- ✓ Chatbot Compiler
- ✓ Interface Builder
- ✓ Jester Analyzer
- ✓ License Verification

### 3. Unit Tests with Pytest (700+ tests, ~2 minutes)

Runs all unit tests including property-based tests with Hypothesis.

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_properties.py -v

# Run with coverage report
pytest tests/ --cov=core --cov-report=html

# Run only fast tests (skip slow integration tests)
pytest tests/ -m "not slow"
```

---

## Test Suites

### Core Component Tests

Tests the fundamental verification components:

```bash
pytest tests/test_properties.py         # Property-based tests (Hypothesis)
pytest tests/test_integration.py        # Integration tests
pytest tests/test_ratio_constraints.py  # Ratio constraint tests
```

### Language & Compiler Tests

Tests tinyTalk language and compilers:

```bash
pytest tests/test_tinytalk.py              # tinyTalk language
pytest tests/test_chatbot_compiler.py      # Chatbot compiler
pytest tests/test_qap_compiler.py          # QAP compiler
pytest tests/test_constraint_extraction.py # Constraint extraction
```

### System Tests

Tests complete systems:

```bash
pytest tests/test_newton_acid_test.py   # ACID compliance
pytest tests/test_glass_box.py          # Glass box verification
pytest tests/test_merkle_proofs.py      # Merkle proof system
```

### Feature Tests

Tests specific features:

```bash
pytest tests/test_voice_interface.py    # Voice interface
pytest tests/test_policy_engine.py      # Policy engine
pytest tests/test_negotiator.py         # Negotiator system
pytest tests/test_education_enhanced.py # Education features
```

---

## Windows-Specific Instructions

### Using Command Prompt (cmd.exe)

```cmd
# Navigate to Newton directory
cd C:\path\to\Newton-api

# Activate virtual environment (if using one)
venv\Scripts\activate.bat

# Start server in first window
python newton_supercomputer.py

# Open new Command Prompt window and run tests
python test_full_system.py
```

### Using PowerShell

```powershell
# Navigate to Newton directory
cd C:\path\to\Newton-api

# Activate virtual environment (if using one)
venv\Scripts\Activate.ps1

# Note: You may need to enable script execution first
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Start server in first window
python .\newton_supercomputer.py

# Open new PowerShell window and run tests
python .\test_full_system.py
```

### Using Windows Terminal (Recommended)

Windows Terminal makes it easy to run multiple terminals side-by-side:

1. Open Windows Terminal
2. Split pane (Ctrl+Shift+D for vertical split)
3. Run server in left pane: `python newton_supercomputer.py`
4. Run tests in right pane: `python test_full_system.py`

### Using Git Bash (Alternative)

```bash
# Works like macOS/Linux
python3 newton_supercomputer.py &
python3 test_full_system.py
```

---

## Troubleshooting

### Server Not Starting

**Problem:** `Connection refused` error when running tests

**Solution:**
```bash
# Check if port 8000 is already in use
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000

# If port is in use, kill the process or use a different port
# Windows: Find PID from above command, then
taskkill /PID <pid> /F

# macOS/Linux
kill -9 <pid>
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# If still failing, install explicitly
pip install fastapi uvicorn pydantic requests
```

### Python Version Issues

**Problem:** `SyntaxError` or version-related errors

**Solution:**
```bash
# Check Python version
python --version

# Newton requires Python 3.9+
# Install from: https://www.python.org/downloads/

# On Windows, you may need to use 'py' launcher
py -3.9 newton_supercomputer.py
```

### Virtual Environment Issues

**Problem:** Dependencies not found even after installing

**Solution:**
```bash
# Create fresh virtual environment
python -m venv venv

# Activate it
# Windows Command Prompt
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
pip install -e .
```

### Permission Errors on Windows

**Problem:** `Access denied` when running scripts

**Solution:**
```powershell
# Enable script execution in PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run as Administrator (right-click > Run as Administrator)
```

### Test Timeout

**Problem:** Tests hanging or timing out

**Solution:**
```bash
# Increase timeout in test files
# Or check if server is actually running
curl http://localhost:8000/health

# Windows (if curl not available)
Invoke-WebRequest -Uri http://localhost:8000/health
```

---

## Understanding Test Results

### Successful Test Output

```
✓ Health Check: 2.31ms
   3/3 components operational
```
- Green checkmark ✓ = Test passed
- Time in milliseconds = Response time
- Details indented below

### Failed Test Output

```
✗ Forge Verification: HTTP 500
```
- Red X ✗ = Test failed
- Error code or message shown
- Check server logs for details

### Test Summary

```
═══════════════════════════════════════════════════════════════
  RESULTS: 80/85 tests passed
  ✗ 5 tests failed

  Check that Newton is running: python newton_supercomputer.py
═══════════════════════════════════════════════════════════════
```

**Pass Rate:**
- 100% = All systems operational
- 90-99% = Minor issues, most features work
- 80-89% = Some systems down, investigate failures
- <80% = Major issues, check setup

---

## Writing Your Own Tests

### Basic Test Template

```python
import requests

BASE_URL = "http://localhost:8000"

def test_my_feature():
    """Test a specific feature"""
    response = requests.post(
        f"{BASE_URL}/endpoint",
        json={"key": "value"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["verified"] == True
    
    print("✓ My feature works!")

if __name__ == "__main__":
    test_my_feature()
```

### Using Newton SDK

```python
from newton_sdk import NewtonClient

def test_with_sdk():
    """Test using the Newton SDK"""
    client = NewtonClient(base_url="http://localhost:8000")
    
    # Verify content
    result = client.verify("Test content")
    assert result["verified"] == True
    
    # Evaluate constraint
    result = client.constraint(
        constraint={"field": "age", "operator": "ge", "value": 18},
        obj={"age": 25}
    )
    assert result["passed"] == True
    
    print("✓ SDK test passed!")

if __name__ == "__main__":
    test_with_sdk()
```

### Property-Based Testing

```python
from hypothesis import given, strategies as st
import pytest

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    """Test that addition is commutative"""
    from newton_sdk import NewtonClient
    client = NewtonClient()
    
    result1 = client.calculate({"op": "+", "args": [a, b]})
    result2 = client.calculate({"op": "+", "args": [b, a]})
    
    assert result1["result"] == result2["result"]
```

---

## Performance Testing

### Quick Benchmark

```bash
# Time a single request
time curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "test"}'
```

### Load Testing

```bash
# Install Apache Bench (Windows: download from Apache)
# macOS: comes with OS
# Linux: apt-get install apache2-utils

# Run 1000 requests with 10 concurrent
ab -n 1000 -c 10 -p test_data.json -T application/json \
  http://localhost:8000/verify
```

### Using Python

```python
import time
import requests
import statistics

def benchmark_endpoint(url, iterations=100):
    """Benchmark an endpoint"""
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        requests.get(url)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # Convert to ms
    
    print(f"Mean: {statistics.mean(times):.2f}ms")
    print(f"Median: {statistics.median(times):.2f}ms")
    print(f"Min: {min(times):.2f}ms")
    print(f"Max: {max(times):.2f}ms")

benchmark_endpoint("http://localhost:8000/health")
```

---

## Continuous Integration

### GitHub Actions

Add to `.github/workflows/test.yml`:

```yaml
name: Test Newton

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -e .
    
    - name: Start Newton server
      run: |
        python newton_supercomputer.py &
        sleep 5
    
    - name: Run tests
      run: |
        python test_full_system.py
        pytest tests/ -v
```

---

## Test Coverage

### Generate Coverage Report

```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
pytest tests/ --cov=core --cov=newton_sdk --cov-report=html

# Open report
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

### Coverage Goals

- Core modules (cdl.py, logic.py, forge.py, etc.): **90%+**
- API endpoints: **80%+**
- Utility functions: **70%+**
- Overall project: **80%+**

---

## Additional Resources

- **README.md** - Project overview and quick start
- **QUICKSTART.md** - 5-minute getting started guide
- **GETTING_STARTED.md** - 30-minute comprehensive guide
- **TINYTALK_PROGRAMMING_GUIDE.md** - tinyTalk language reference
- **API Documentation** - See newton_supercomputer.py docstrings
- **Examples** - Check `examples/` directory for working code

---

## Support

If tests are failing and you can't figure out why:

1. Check this troubleshooting guide
2. Review the server logs for errors
3. Try the setup script: `./setup_newton.sh` (Linux/macOS)
4. Check the [GitHub Issues](https://github.com/jaredlewiswechs/Newton-api/issues)
5. Review recent commits for breaking changes

---

## Test Philosophy

> "The constraint IS the instruction. The verification IS the computation."

Newton's testing follows these principles:

1. **Determinism** - Same input always produces same output
2. **Termination** - All tests must complete (bounded execution)
3. **Verification** - Every test verifies a specific property
4. **Immutability** - Test data doesn't change during execution

When all tests pass: **1 == 1**

---

**Last Updated:** January 31, 2026

**Newton Version:** 1.3.0

**Maintained by:** Jared Lewis Conglomerate
