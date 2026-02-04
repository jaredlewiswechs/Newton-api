# 📚 realTinyTalk: Library Development Guide

**How to work on realTinyTalk from any computer (library, school, friend's house)**

---

## 🚀 Quick Start (5 minutes)

### Option 1: GitHub Codespaces (Easiest - Nothing to Install!)

1. Go to: `https://github.com/YOUR_USERNAME/Newton-api`
2. Click the green **Code** button
3. Click **Codespaces** → **Create codespace**
4. Wait 2 minutes for it to load
5. In the terminal, type:
   ```bash
   pip install flask
   python realTinyTalk/web/server.py
   ```
6. Click the popup to open port 5555 → You're coding!

### Option 2: Any Computer with Python

```bash
# Step 1: Get the code
git clone https://github.com/YOUR_USERNAME/Newton-api.git
cd Newton-api

# Step 2: Install Flask (the web server)
pip install flask

# Step 3: Run it!
python realTinyTalk/web/server.py
```

Then open your browser to: **http://localhost:5555**

---

## 🎓 How Programming Languages Work (HS Crash Course)

### The Big Picture

When you write code like:
```
let name = "Newton"
show("Hello" name)
```

The computer doesn't understand English! It needs to be translated. Here's how:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Your Code  │ ──▶ │   LEXER     │ ──▶ │   PARSER    │ ──▶ │ INTERPRETER │
│  (text)     │     │  (tokens)   │     │   (tree)    │     │  (runs it)  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

---

### Step 1: The LEXER (Word Splitter)

**What it does:** Breaks your code into "tokens" (words)

**Analogy:** Like breaking a sentence into words

```
Input:  let name = "Newton"

Output: [LET] [IDENTIFIER:name] [EQUALS] [STRING:"Newton"]
```

**File:** `realTinyTalk/lexer.py`

**Think of it like:** A cashier scanning items at a grocery store - each item gets a barcode (token type)

---

### Step 2: The PARSER (Grammar Checker)

**What it does:** Takes tokens and builds a "tree" showing the structure

**Analogy:** Like diagramming a sentence in English class

```
Input:  let name = "Newton"

Output (Tree):
        LetStatement
        /          \
    name         "Newton"
   (variable)    (value)
```

**File:** `realTinyTalk/parser.py`

**Think of it like:** 
- "The cat sat" ✅ (Subject-Verb = valid grammar)
- "Cat the sat" ❌ (Invalid grammar)

The parser checks that your code follows the rules!

---

### Step 3: The INTERPRETER (Code Runner)

**What it does:** Walks through the tree and actually DOES the stuff

**File:** `realTinyTalk/interpreter.py`

```
Tree:     LetStatement(name, "Newton")
          ↓
Action:   Create variable 'name' with value "Newton"
          ↓
Memory:   { name: "Newton" }
```

---

### BONUS: The EMITTER (Translator)

**What it does:** Instead of running the code, translates it to ANOTHER language!

```
TinyTalk:     let nums = [3,1,2] _sort
                    ↓
JavaScript:   let nums = [3,1,2].sort((a,b) => a-b)
                    ↓
Python:       nums = sorted([3,1,2])
```

**Files:**
- `realTinyTalk/backends/js/emitter.py` → Translates to JavaScript
- `realTinyTalk/backends/python/emitter.py` → Translates to Python

**Why is this cool?** You can write code ONCE in TinyTalk and run it anywhere!

---

## 📁 Project Structure (What's What)

```
realTinyTalk/
├── lexer.py          # Step 1: Breaks code into tokens
├── parser.py         # Step 2: Builds the syntax tree
├── interpreter.py    # Step 3: Runs the code
├── runtime.py        # Built-in functions (show, len, etc.)
├── __init__.py       # Main entry point
│
├── backends/         # EMITTERS (translators)
│   ├── js/
│   │   └── emitter.py    # TinyTalk → JavaScript
│   └── python/
│       └── emitter.py    # TinyTalk → Python
│
├── web/              # The Monaco IDE website
│   ├── server.py         # Flask web server
│   └── static/
│       └── index.html    # The editor UI
│
└── tests/            # Test files
    ├── test_monaco_ui.py      # Tests the web IDE
    └── test_python_transpiler.py  # Tests Python output
```

---

## 🔧 What to Work On (Beginner Projects)

### Level 1: Easy (No coding experience needed)
- [ ] Add more example programs in `server.py` → `get_examples()`
- [ ] Change colors/themes in `index.html`
- [ ] Write documentation

### Level 2: Medium (Some Python)
- [ ] Add a new property like `.titlecase` in `runtime.py`
- [ ] Add a new step chain like `_shuffle` in `runtime.py`
- [ ] Fix bugs found by running tests

### Level 3: Advanced (Understanding the pipeline)
- [ ] Add a new keyword to `lexer.py`
- [ ] Add new syntax to `parser.py`
- [ ] Add new operation to emitters

---

## 🧪 Testing Your Changes

```bash
# Run all Monaco UI tests (38 tests)
python realTinyTalk/tests/test_monaco_ui.py

# Run Python transpiler tests (52 tests)
python -m realTinyTalk.tests.test_python_transpiler

# Quick manual test
python -c "from realTinyTalk import run; print(run('show(1 + 2)'))"
```

---

## 📝 Example: Adding a New Property

Let's add `.titlecase` so `"hello world".titlecase` → `"Hello World"`

### Step 1: Find where properties are defined

Open `realTinyTalk/runtime.py` and find the string properties:

```python
# Around line 50-ish, you'll see:
'upcase': lambda s: s.upper(),
'lowcase': lambda s: s.lower(),
```

### Step 2: Add your property

```python
'upcase': lambda s: s.upper(),
'lowcase': lambda s: s.lower(),
'titlecase': lambda s: s.title(),  # ← ADD THIS LINE
```

### Step 3: Test it!

```bash
python -c "from realTinyTalk import run; run('show(\"hello world\".titlecase)')"
# Output: Hello World
```

🎉 You just extended a programming language!

---

## 🌐 Remote Development Options

| Method | Pros | Cons |
|--------|------|------|
| **GitHub Codespaces** | Nothing to install, full VS Code | Needs GitHub account |
| **Replit** | Super easy, shareable | Slower, free tier limits |
| **GitPod** | Fast, full IDE | Needs account |
| **Library PC + Python** | No account needed | Need to install Python |

---

## 🆘 Common Issues

### "Module not found" error
```bash
pip install flask
```

### "Port already in use" error
```bash
# Windows
netstat -ano | findstr :5555
taskkill /PID <number> /F

# Mac/Linux
lsof -i :5555
kill -9 <number>
```

### Changes not showing in browser
- Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
- Restart server: `Ctrl+C` then run again

---

## 📖 Glossary

| Term | Meaning |
|------|---------|
| **Token** | A single "word" in your code (like `let`, `"hello"`, `+`) |
| **AST** | Abstract Syntax Tree - the "grammar diagram" of your code |
| **Lexer** | Breaks text into tokens |
| **Parser** | Builds the AST from tokens |
| **Interpreter** | Runs the AST directly |
| **Emitter** | Converts AST to another language |
| **Transpiler** | Emitter (same thing, fancier word) |
| **Runtime** | Built-in functions and features |

---

## 🎯 Challenge Projects

1. **Add `_shuffle`** - Randomly shuffle an array
2. **Add `.reverse`** - Reverse a string (not array)
3. **Add `_drop(n)`** - Remove first n items from array
4. **Add `elif` support** - Allow `else if` chains
5. **Add string interpolation** - `"Hello {name}!"` syntax

---

## 💬 Getting Help

- Read the test files - they show how everything works
- Run tests to see what's expected
- Start small - change one thing, test, repeat

**Remember:** Every programmer started somewhere. The lexer, parser, interpreter pattern is used in EVERY programming language - Python, JavaScript, Java, all of them. You're learning the real stuff! 🚀

---

*Last updated: February 2026*
*realTinyTalk - The friendliest programming language*
