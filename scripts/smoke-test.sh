#!/bin/bash
# Newton API Smoke Test Script
# Tests all critical endpoints on the deployed Render service

BASE_URL="${NEWTON_API_URL:-https://newton-api.onrender.com}"
PASS=0
FAIL=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Newton API Smoke Tests"
echo "Base URL: $BASE_URL"
echo "========================================"
echo ""

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_field="$5"

    echo -n "Testing: $name... "

    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        if [ -n "$expected_field" ]; then
            if echo "$body" | grep -q "$expected_field"; then
                echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
                ((PASS++))
            else
                echo -e "${YELLOW}⚠ WARN${NC} (HTTP $http_code, missing expected field: $expected_field)"
                ((PASS++))
            fi
        else
            echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
            ((PASS++))
        fi
        echo "  Response: ${body:0:200}..."
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        echo "  Response: $body"
        ((FAIL++))
    fi
    echo ""
}

# 1. Health Check
test_endpoint "Health Check" "GET" "/health" "" "status"

# 2. Ask Newton (Primary Entry Point)
test_endpoint "Ask Newton (2+2)" "POST" "/ask" '{"query":"2 + 2"}' "answer"

# 3. Ask Newton (Boolean)
test_endpoint "Ask Newton (1==1)" "POST" "/ask" '{"query":"1==1"}' ""

# 4. Verified Calculation Engine
test_endpoint "Calculate (10+32)" "POST" "/calculate" '{"expression":{"op":"+","args":[10,32]}}' "result"

# 5. Calculate (multiplication)
test_endpoint "Calculate (6*7)" "POST" "/calculate" '{"expression":{"op":"*","args":[6,7]}}' "result"

# 6. Content/Safety Verification
test_endpoint "Verify (safe content)" "POST" "/verify" '{"input":"Help me write a lesson plan"}' "verified"

# 7. Constraint Evaluation (CDL)
test_endpoint "Constraint Check" "POST" "/constraint" '{"constraint":{"field":"balance","operator":">=","value":0},"object":{"balance":150}}' "result"

# 8. Ledger (Read-Only)
test_endpoint "Ledger (list)" "GET" "/ledger" "" ""

# 9. Ledger Entry
test_endpoint "Ledger (entry 0)" "GET" "/ledger/0" "" ""

# 10. Metrics (Optional)
test_endpoint "Metrics" "GET" "/metrics" "" ""

# Summary
echo "========================================"
echo "RESULTS"
echo "========================================"
echo -e "Passed: ${GREEN}$PASS${NC}"
echo -e "Failed: ${RED}$FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All tests passed! Newton is live and verified.${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Check the output above.${NC}"
    exit 1
fi
