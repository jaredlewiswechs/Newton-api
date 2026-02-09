#!/bin/bash
# =============================================================================
# Newton Teacher's Aide - New Repo & Cloudflare Auto-Deploy Setup
# Run this script from the newton-teachers-aide-deploy directory
# =============================================================================

set -e

REPO_NAME="newton-teachers-aide"
DESCRIPTION="Newton Teacher's Aide - Offline teaching assistant with Cloudflare Pages auto-deploy"

echo "=================================================="
echo " Newton Teacher's Aide - Repo & Deploy Setup"
echo "=================================================="
echo ""

# Check for gh CLI
if ! command -v gh &> /dev/null; then
  echo "ERROR: GitHub CLI (gh) is required. Install it:"
  echo "  brew install gh       # macOS"
  echo "  winget install gh     # Windows"
  echo "  sudo apt install gh   # Ubuntu/Debian"
  exit 1
fi

# Check auth
if ! gh auth status &> /dev/null 2>&1; then
  echo "Not logged in to GitHub. Running 'gh auth login'..."
  gh auth login
fi

echo ""
echo "Step 1: Creating GitHub repo '$REPO_NAME'..."
gh repo create "$REPO_NAME" --public --description "$DESCRIPTION" --clone
echo "   Done."

echo ""
echo "Step 2: Copying app files..."
# Copy all files except this script and the .git directory
for f in index.html app.js newton-offline-engine.js styles.css _headers _redirects wrangler.toml package.json .gitignore README.md; do
  if [ -f "../newton-teachers-aide-deploy/$f" ]; then
    cp "../newton-teachers-aide-deploy/$f" "$REPO_NAME/"
  elif [ -f "$f" ]; then
    cp "$f" "$REPO_NAME/" 2>/dev/null || true
  fi
done
echo "   Done."

echo ""
echo "Step 3: Committing and pushing..."
cd "$REPO_NAME"
git add -A
git commit -m "Initial commit: Newton Teacher's Aide for Cloudflare Pages

Fully offline teaching assistant with TEKS standards, lesson planning,
assessment analysis, and more. Zero server dependency.

(c) 2026 Jared Lewis - Ada Computing Company"
git branch -M main
git push -u origin main
echo "   Done."

echo ""
echo "=================================================="
echo " REPO CREATED SUCCESSFULLY!"
echo "=================================================="
echo ""
echo " Your repo: https://github.com/$(gh api user -q .login)/$REPO_NAME"
echo ""
echo " NEXT: Connect to Cloudflare Pages for auto-deploy:"
echo ""
echo "   1. Go to: https://dash.cloudflare.com → Pages"
echo "   2. Click 'Create a project' → 'Connect to Git'"
echo "   3. Select '$REPO_NAME'"
echo "   4. Build settings:"
echo "      - Build command: (leave blank)"
echo "      - Build output directory: /"
echo "   5. Click 'Save and Deploy'"
echo ""
echo " Or deploy manually right now:"
echo "   cd $REPO_NAME && npm install && npm run deploy"
echo ""
