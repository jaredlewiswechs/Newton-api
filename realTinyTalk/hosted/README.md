# realTinyTalk Hosted Playground

A **self-contained, static web IDE** for the realTinyTalk programming language. No server required -- everything runs in the browser.

## Quick Start

### Option 1: Open Locally
```bash
# Just open the HTML file in your browser
open realTinyTalk/hosted/index.html
# or on Linux:
xdg-open realTinyTalk/hosted/index.html
```

### Option 2: Host Online (Static)

Upload `index.html` to any static hosting service. No build step, no server, no dependencies.

**GitHub Pages:**
```bash
# 1. Create a new repo (or use gh-pages branch)
# 2. Copy index.html to the repo root
cp realTinyTalk/hosted/index.html docs/index.html
git add docs/index.html
git commit -m "Add realTinyTalk playground"
git push
# 3. Enable GitHub Pages in repo Settings -> Pages -> Source: /docs
```

**Netlify / Vercel / Cloudflare Pages:**
```bash
# Just drag-and-drop index.html into their deploy UI
# Or connect your repo and point to the realTinyTalk/hosted/ directory
```

**Any Web Server (Nginx, Apache, etc.):**
```bash
# Copy to your web root
cp realTinyTalk/hosted/index.html /var/www/html/tinytalk/index.html
# Visit http://yourserver.com/tinytalk/
```

### Option 3: Use the Zip Package
```bash
# Build the zip
bash realTinyTalk/hosted/package.sh

# The zip is at: realTinyTalk/hosted/dist/realTinyTalk-playground.zip
# Unzip and upload index.html to any hosting provider
```

## Features

| Feature | Description |
|---------|-------------|
| **Monaco Editor** | Full-featured code editor (same as VS Code) with TinyTalk syntax highlighting |
| **Client-Side Execution** | Code runs entirely in the browser via TinyTalk-to-JavaScript transpilation |
| **4 Themes** | Dark (GitHub), Light, Monokai, Nord |
| **13 Examples** | Built-in programs from Hello World to Quicksort |
| **Auto-Completion** | Keywords, functions, step chains, property magic, snippets |
| **Local Storage** | Scripts persist in your browser across sessions |
| **Export/Import** | Save and load `.tt` files |
| **JS Transpilation View** | See the generated JavaScript side-by-side |

## How It Works

The hosted playground includes a **client-side TinyTalk-to-JavaScript transpiler** that converts your TinyTalk code to JavaScript and executes it in the browser. The `tt` runtime provides all the TinyTalk standard library functions (show, range, step chains, property magic, etc.).

```
TinyTalk Source → Client-side Transpiler → JavaScript → Browser Execution
```

### Supported Language Features

- Variables (`let`, `when` constants)
- Functions (`law`, `forge`, `fn`, `when...do...finfr`)
- Control flow (`if/elif/else`, `for`, `while`, `break`, `continue`)
- Data types (strings, numbers, booleans, arrays, maps)
- Step chains (`_sort`, `_filter`, `_map`, `_take`, `_sum`, etc.)
- Property magic (`.upcase`, `.len`, `.reversed`, `.str`, `.int`, etc.)
- Natural comparisons (`is`, `isnt`, `has`, `isin`, `islike`)
- Standard library (`show`, `range`, `abs`, `sqrt`, `min`, `max`, etc.)
- Recursion

### Limitations vs Full Server IDE

The hosted version runs a lightweight transpiler client-side. For the full realTinyTalk experience with server-side verified execution, bounded execution enforcement, script persistence with versioning, and Python transpilation, use the Flask-based IDE:

```bash
python realTinyTalk/web/server.py
# Visit http://localhost:5555
```

## File Structure

```
realTinyTalk/hosted/
├── index.html          # Self-contained playground (single file, ~45KB)
├── package.sh          # Build script to create distributable zip
├── README.md           # This file
└── dist/               # Generated zip output
    └── realTinyTalk-playground.zip
```

## Requirements

- A modern web browser (Chrome 80+, Firefox 78+, Safari 14+, Edge 80+)
- Internet connection (for Monaco editor CDN on first load)
- That's it. No Python, no Node.js, no server.
