#!/bin/bash
# Quick deployment verification script for Newton apps
# Run this after deploying to Render to verify all apps work

BASE_URL="${1:-https://newton-api.onrender.com}"

echo "🔍 Testing Newton Apps on $BASE_URL"
echo "=========================================="
echo ""

apps=(
  "/:Homepage"
  "/app:Newton Supercomputer"
  "/frontend:Newton Frontend"
  "/teachers:Teacher's Aide"
  "/builder:Interface Builder"
  "/jester-analyzer:Jester Analyzer"
  "/tinytalk-ide:TinyTalk IDE"
  "/construct-studio:Construct Studio"
  "/newton-demo:Newton Demo"
  "/games/gravity_wars:Gravity Wars"
  "/parccloud:ParcCloud"
  "/health:API Health"
  "/docs:API Docs"
)

passed=0
failed=0

for app in "${apps[@]}"; do
  path="${app%%:*}"
  name="${app##*:}"
  
  printf "Testing %-30s ... " "$name"
  status=$(curl -s -L -o /dev/null -w "%{http_code}" "$BASE_URL$path")
  
  if [ "$status" = "200" ]; then
    echo "✅ OK ($status)"
    ((passed++))
  else
    echo "❌ FAILED ($status)"
    ((failed++))
  fi
done

echo ""
echo "=========================================="
echo "Results: $passed passed, $failed failed"
echo ""

if [ $failed -eq 0 ]; then
  echo "🎉 All apps are working correctly!"
  exit 0
else
  echo "⚠️  Some apps failed. Check the logs above."
  exit 1
fi
