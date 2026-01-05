#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# NEWTON SUPERCOMPUTER - SETUP SCRIPT
# ═══════════════════════════════════════════════════════════════════════════════
#
# This script sets up Newton on your local machine (SSD, laptop, etc.)
#
# Usage:
#   chmod +x setup_newton.sh
#   ./setup_newton.sh
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "                     NEWTON SUPERCOMPUTER SETUP"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Setting up Newton - Verified Computation System"
echo "The constraint IS the instruction. 1 == 1."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "[1/6] Checking Python version: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION < 3.9" | bc -l) -eq 1 ]]; then
    echo "ERROR: Python 3.9+ required. Found: $PYTHON_VERSION"
    exit 1
fi
echo "      ✓ Python version OK"

# Create virtual environment
echo ""
echo "[2/6] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "      ✓ Virtual environment created"
else
    echo "      ✓ Virtual environment exists"
fi

# Activate virtual environment
echo ""
echo "[3/6] Activating virtual environment..."
source venv/bin/activate
echo "      ✓ Activated"

# Install dependencies
echo ""
echo "[4/6] Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null
echo "      ✓ Dependencies installed"

# Run tests to verify installation
echo ""
echo "[5/6] Running verification tests..."
echo "      Running core tests (this may take a minute)..."

# Run TLM tests (most important - ACID compliance)
TLM_RESULT=$(python -m pytest newton_tlm/tests/ -q 2>&1 | tail -1)
echo "      TLM Tests: $TLM_RESULT"

# Run key integration tests
KEY_TESTS="tests/test_tinytalk.py tests/test_ratio_constraints.py tests/test_integration.py"
CORE_RESULT=$(python -m pytest $KEY_TESTS -q 2>&1 | tail -1)
echo "      Core Tests: $CORE_RESULT"

# Verify the server can start
echo ""
echo "[6/6] Testing server startup..."
python newton_supercomputer.py &
SERVER_PID=$!
sleep 3

# Check health endpoint
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status','fail'))" 2>/dev/null || echo "fail")

if [ "$HEALTH" == "ok" ]; then
    echo "      ✓ Server started successfully!"

    # Test verify endpoint
    VERIFY=$(curl -s -X POST http://localhost:8000/verify \
        -H "Content-Type: application/json" \
        -d '{"input": "test"}' 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('verified','false'))" 2>/dev/null || echo "false")

    if [ "$VERIFY" == "True" ]; then
        echo "      ✓ Verification endpoint working!"
    fi

    # Test calculate endpoint
    CALC=$(curl -s -X POST http://localhost:8000/calculate \
        -H "Content-Type: application/json" \
        -d '{"expression": {"op": "+", "args": [1, 1]}}' 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('result','0'))" 2>/dev/null || echo "0")

    if [ "$CALC" == "2" ]; then
        echo "      ✓ Calculation endpoint working! (1+1=$CALC)"
    fi
else
    echo "      ✗ Server failed to start"
fi

# Kill the test server
kill $SERVER_PID 2>/dev/null || true

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "                         SETUP COMPLETE!"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Newton is ready! Here's how to use it:"
echo ""
echo "  1. Start the server:"
echo "     source venv/bin/activate"
echo "     python newton_supercomputer.py"
echo ""
echo "  2. Test it:"
echo "     curl http://localhost:8000/health"
echo "     curl -X POST http://localhost:8000/verify -d '{\"input\": \"test\"}'"
echo "     curl -X POST http://localhost:8000/calculate -d '{\"expression\": {\"op\": \"+\", \"args\": [2, 3]}}'"
echo ""
echo "  3. Run all tests:"
echo "     python -m pytest tests/ -v"
echo ""
echo "  4. Use tinyTalk in Python:"
echo "     from tinytalk_py import Blueprint, field, law, forge, when, finfr"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "               The constraint IS the instruction. 1 == 1."
echo "═══════════════════════════════════════════════════════════════════════════════"
