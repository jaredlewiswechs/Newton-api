# Contributing to Newton

**A Newbie-Friendly Guide to Development**

Welcome! This guide will help you set up your development environment and start contributing to Newton, even if you're new to programming.

---

## What You Need

### 1. Python (Required)

Newton is built with Python 3.9 or higher.

**Check if you have Python:**
```bash
python3 --version
```

**Install Python:**
- **macOS**: `brew install python` (or download from python.org)
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt install python3 python3-pip`

### 2. Git (Required)

For version control and collaboration.

**Check if you have Git:**
```bash
git --version
```

**Install Git:**
- **macOS**: `brew install git`
- **Windows**: Download from [git-scm.com](https://git-scm.com/)
- **Linux**: `sudo apt install git`

### 3. A Code Editor (Required)

Choose one of these popular options:

---

## IDE Setup

### Option A: VS Code (Recommended for Beginners)

**Why VS Code?**
- Free, lightweight, works everywhere
- Excellent Python support
- Great for beginners

**Installation:**
1. Download from [code.visualstudio.com](https://code.visualstudio.com/)
2. Install it
3. Open VS Code

**Essential Extensions (Install these):**
- **Python** (by Microsoft) - Python language support
- **Pylance** - Fast Python IntelliSense
- **GitLens** - See who changed what code

**How to install extensions:**
1. Click the Extensions icon in the left sidebar (looks like 4 squares)
2. Search for the extension name
3. Click "Install"

**Configure VS Code for Newton:**

Create a file `.vscode/settings.json` in the project root:
```json
{
    "python.defaultInterpreterPath": "python3",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### Option B: PyCharm

**Why PyCharm?**
- Full-featured Python IDE
- Built-in debugger, testing, Git integration
- More features, steeper learning curve

**Installation:**
1. Download PyCharm Community (free) from [jetbrains.com](https://www.jetbrains.com/pycharm/)
2. Open the Newton-api folder as a project
3. PyCharm will auto-detect Python and offer to set up the environment

### Option C: Cursor

**Why Cursor?**
- AI-powered coding assistant built-in
- Great for learning as you code
- Based on VS Code

**Installation:**
1. Download from [cursor.sh](https://cursor.sh/)
2. Follow VS Code extension setup above

### Option D: Vim/Neovim (Advanced)

For experienced developers who prefer terminal-based editing.

---

## First-Time Setup

### Step 1: Clone the Repository

```bash
# Navigate to where you want the project
cd ~/projects  # or wherever you keep code

# Clone the repo
git clone https://github.com/jaredlewiswechs/Newton-api.git

# Enter the project directory
cd Newton-api
```

### Step 2: Create a Virtual Environment

A virtual environment keeps project dependencies isolated.

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You'll see `(venv)` at the start of your terminal prompt when activated.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Server

```bash
python newton_supercomputer.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 5: Test It Works

In a new terminal:
```bash
curl http://localhost:8000/health
```

You should see:
```json
{"status": "healthy", ...}
```

---

## Project Structure Explained

```
Newton-api/
│
├── newton_supercomputer.py   # The main server - START HERE
│
├── core/                     # The "brains" of Newton
│   ├── cdl.py               # Constraint Definition Language
│   ├── logic.py             # Verified computation engine
│   ├── forge.py             # Content verification
│   ├── vault.py             # Encrypted storage
│   ├── ledger.py            # Immutable audit trail
│   ├── bridge.py            # Distributed consensus
│   ├── robust.py            # Adversarial statistics
│   ├── grounding.py         # Fact checking
│   ├── cartridges.py        # Media specification
│   └── ...
│
├── tests/                    # Automated tests
│   └── test_*.py            # Test files
│
├── frontend/                 # Web interface
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── docs/                     # Documentation
│
├── TINYTALK_BIBLE.md        # The tinyTalk philosophy
├── README.md                 # Project overview
├── WHITEPAPER.md            # Technical deep-dive
└── requirements.txt          # Python dependencies
```

---

## Running Tests

Always run tests before submitting changes:

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_integration.py -v

# Run tests with coverage report
pytest tests/ --cov=core --cov-report=html
```

All tests should pass (47 tests currently).

---

## Making Changes

### 1. Create a Branch

```bash
# Make sure you're on main
git checkout main
git pull origin main

# Create your feature branch
git checkout -b feature/my-new-thing
```

### 2. Make Your Changes

Edit files in your IDE.

### 3. Test Your Changes

```bash
pytest tests/ -v
```

### 4. Commit Your Changes

```bash
# See what you changed
git status
git diff

# Stage your changes
git add .

# Commit with a meaningful message
git commit -m "Add feature: description of what you did"
```

### 5. Push to GitHub

```bash
git push -u origin feature/my-new-thing
```

### 6. Create a Pull Request

Go to GitHub and create a Pull Request from your branch.

---

## Key Concepts to Understand

### The tinyTalk Philosophy

Read `TINYTALK_BIBLE.md` to understand the "No-First" philosophy:

- **`when`** - Declares a fact/presence
- **`and`** - Combines facts
- **`fin`** - Closure (can be reopened)
- **`finfr`** - Finality (ontological death)

### The Three Layers

| Layer | Purpose | File |
|-------|---------|------|
| L0: Governance | Define what's impossible | Constraints in CDL |
| L1: Executive | Define what happens | Forges in Logic |
| L2: Application | User-facing features | API endpoints |

### The Fundamental Law

```python
def newton(current, goal):
    return current == goal

# 1 == 1 -> execute
# 1 != 1 -> halt
```

---

## Common Tasks

### Add a New API Endpoint

1. Open `newton_supercomputer.py`
2. Find similar endpoints for reference
3. Add your endpoint:

```python
@app.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    # Your logic here
    return {"result": "success"}
```

### Add a New Constraint Type

1. Open `core/cdl.py`
2. Find the operator definitions
3. Add your new operator

### Add a New Test

1. Create or open a test file in `tests/`
2. Add your test function:

```python
def test_my_feature():
    # Setup
    input_data = {"key": "value"}

    # Execute
    result = my_function(input_data)

    # Assert
    assert result == expected_value
```

---

## Troubleshooting

### "Module not found" Error

```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Tests Failing

```bash
# Run with verbose output to see what's wrong
pytest tests/test_integration.py -v -s
```

### Port Already in Use

```bash
# Kill the process on port 8000
# macOS/Linux:
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill

# Or just use a different port:
PORT=8001 python newton_supercomputer.py
```

### Git Merge Conflicts

```bash
# See conflicting files
git status

# Open the file and look for:
# <<<<<<< HEAD
# your changes
# =======
# their changes
# >>>>>>> branch-name

# Edit to keep what you want, then:
git add <file>
git commit -m "Resolve merge conflict"
```

---

## Learning Resources

### Python

- [Python Tutorial](https://docs.python.org/3/tutorial/)
- [Real Python](https://realpython.com/)

### FastAPI (Our Web Framework)

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

### Git

- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [Oh Shit, Git!?!](https://ohshitgit.com/) - For when things go wrong

### Newton-Specific

- `TINYTALK_BIBLE.md` - The philosophy
- `WHITEPAPER.md` - Technical architecture
- `docs/` - API and feature documentation

---

## Getting Help

- **Questions**: Open an issue on GitHub
- **Bugs**: Include steps to reproduce
- **Features**: Describe the use case

---

## Code Style

- Use type hints where possible
- Add docstrings to functions
- Keep functions small and focused
- Write tests for new features
- Follow the patterns in existing code

---

*"1 == 1. Go build something."*
