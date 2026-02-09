#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Package realTinyTalk Hosted Playground for distribution
# Creates a .zip file ready for static hosting
# ═══════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"
ZIP_NAME="realTinyTalk-playground.zip"

echo "═══════════════════════════════════════════════════════"
echo "  Packaging realTinyTalk Hosted Playground"
echo "═══════════════════════════════════════════════════════"

# Clean previous build
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR/realTinyTalk-playground"

# Copy the standalone HTML file
cp "$SCRIPT_DIR/index.html" "$DIST_DIR/realTinyTalk-playground/index.html"

# Create a simple README for the zip
cat > "$DIST_DIR/realTinyTalk-playground/README.txt" << 'EOF'
realTinyTalk Playground
=======================

A self-contained web IDE for the realTinyTalk programming language.

QUICK START
-----------
1. Open index.html in any modern browser (Chrome, Firefox, Safari, Edge)
2. Write TinyTalk code in the editor
3. Press Ctrl+Enter (or click Run) to execute
4. See output in the right panel

HOSTING ONLINE
--------------
Upload index.html to any static hosting service:
  - GitHub Pages
  - Netlify
  - Vercel
  - Cloudflare Pages
  - Any web server (Apache, Nginx, etc.)

No server-side dependencies required - everything runs in the browser!

FEATURES
--------
- Monaco editor with full TinyTalk syntax highlighting
- 4 color themes (Dark, Light, Monokai, Nord)
- 13 built-in example programs
- Client-side code execution (no server needed)
- Auto-completion for keywords, functions, and step chains
- Local storage for saving your scripts
- Export/Import .tt files
- JavaScript transpilation view

(c) 2026 Jared Lewis - Ada Computing Company
EOF

# Create the zip
cd "$DIST_DIR"
zip -r "$ZIP_NAME" realTinyTalk-playground/

echo ""
echo "Package created: $DIST_DIR/$ZIP_NAME"
echo ""
echo "To deploy:"
echo "  1. Unzip the file"
echo "  2. Upload index.html to your hosting provider"
echo "  3. Open in a browser - that's it!"
echo ""
