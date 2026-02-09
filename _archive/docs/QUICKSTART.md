# Newton Quick Start (5 Minutes)

**Get Newton running in 5 minutes. No prior experience needed.**

```
╭──────────────────────────────────────────────────────────────╮
│                                                              │
│   🍎 Newton Quick Start                                      │
│                                                              │
│   Three commands. Five minutes. You're done.                 │
│                                                              │
╰──────────────────────────────────────────────────────────────╯
```

## Prerequisites

✅ **Python 3.9+** (check with `python3 --version`)  
✅ **10 minutes** of your time  
✅ **An open mind** about verification-first programming

That's it. No database, no Docker, no cloud account needed.

---

## Step 1: Install (2 minutes)

```bash
# Clone the repo
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# Run the setup script (does everything for you)
./setup_newton.sh
```

**What happens:**
- Creates a Python virtual environment
- Installs all dependencies
- Installs Newton SDK (`newton` command)
- Runs verification tests
- Tests the server

**Expected output:**
```
═══════════════════════════════════════════════════════════════
                SETUP COMPLETE!
═══════════════════════════════════════════════════════════════
Newton is ready!
```

**Manual Install (Windows or if script fails):**
```bash
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
pip install -e .    # Required for 'newton' command to work!
```

---

## Step 2: Test It (1 minute)

Open a **new terminal** and run:

```bash
cd Newton-api
source venv/bin/activate
python newton_supercomputer.py
```

**Expected output:**
```
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
```

**✅ Server is running!** Leave this terminal open.

---

## Step 3: Verify It Works (2 minutes)

Open **another terminal** and run these tests:

```bash
# Test 1: Health check
curl http://localhost:8000/health

# Expected: {"status": "ok", ...}
```

```bash
# Test 2: Verify something
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "test input"}'

# Expected: {"verified": true, ...}
```

```bash
# Test 3: Calculate something
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "+", "args": [2, 3]}}'

# Expected: {"result": 5, ...}
```

**All three work?** 🎉 **You're done!**

---

## What Just Happened?

Newton is now running on your machine. It's:

1. **Verifying** inputs against constraints
2. **Computing** with guaranteed bounds
3. **Recording** everything in an immutable ledger

You just installed a **verified computation system** in 5 minutes.

---

## Next Steps

### Option 1: Try the Demo (Recommended)

```bash
python examples/demo_bank_account.py
```

You'll see how Newton prevents invalid states (like overdrafts) **before** they happen.

### Option 2: Read the Tutorial

Open [GETTING_STARTED.md](GETTING_STARTED.md) for a complete walkthrough.

### Option 3: Start Building

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class MyFirstBlueprint(Blueprint):
    value = field(int, default=0)
    
    @law
    def no_negatives(self):
        when(self.value < 0, finfr)
    
    @forge
    def set_value(self, n):
        self.value = n
        return f"Value set to {n}"

# Use it
obj = MyFirstBlueprint()
obj.set_value(10)  # ✓ Works
obj.set_value(-5)  # ✗ Blocked by law!
```

---

## Troubleshooting

### Problem: `./setup_newton.sh` fails

**Solution 1:** Make it executable first
```bash
chmod +x setup_newton.sh
./setup_newton.sh
```

**Solution 2:** Run it directly with bash
```bash
bash setup_newton.sh
```

### Problem: "Python 3.9+ required"

**Install Python 3.9+:**

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv
```

**On Mac:**
```bash
brew install python@3.10
```

**On Windows:**
Download from [python.org](https://www.python.org/downloads/)

### Problem: Server won't start

**Check if something is using port 8000:**
```bash
# On Mac/Linux
lsof -i :8000

# On Windows
netstat -ano | findstr :8000
```

**Use a different port:**
```bash
python newton_supercomputer.py --port 8001
```

### Problem: curl commands fail

**Install curl:**

**On Ubuntu/Debian:**
```bash
sudo apt install curl
```

**On Mac:**
```bash
brew install curl
```

**On Windows:**
Use PowerShell's `Invoke-WebRequest` instead:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health
```

### Problem: Tests fail

**Run the test suite to see details:**
```bash
source venv/bin/activate
python -m pytest tests/ -v
```

**Still stuck?**
1. Check [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup
2. Open an issue on [GitHub](https://github.com/jaredlewiswechs/Newton-api/issues)
3. Read [DEVELOPERS.md](DEVELOPERS.md) for development setup

---

## What's Different About Newton?

**Traditional Programming:**
```python
def withdraw(account, amount):
    account.balance -= amount  # Hope this doesn't go negative
    if account.balance < 0:    # Check AFTER it happened
        raise ValueError("Overdraft!")
```

**Newton Programming:**
```python
class Account(Blueprint):
    balance = field(float, default=1000)
    
    @law  # Define what CANNOT happen
    def no_overdraft(self):
        when(self.balance < 0, finfr)  # Check BEFORE it happens
    
    @forge
    def withdraw(self, amount):
        self.balance -= amount  # Law prevents invalid state
```

**The constraint IS the instruction. The verification IS the computation.**

---

## Platform-Specific Notes

### macOS

Works out of the box. If you use Homebrew:
```bash
brew install python@3.10
```

### Linux (Ubuntu/Debian)

Works out of the box. Install Python 3.10+:
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

### Windows

Use PowerShell or Windows Terminal. Replace:
- `./setup_newton.sh` → `bash setup_newton.sh` (install Git Bash first)
- `source venv/bin/activate` → `venv\Scripts\activate`
- `curl` → `Invoke-WebRequest`

**Or use WSL2** (Windows Subsystem for Linux) for the full Linux experience.

---

## Success Checklist

- [ ] `./setup_newton.sh` completes without errors
- [ ] `python newton_supercomputer.py` starts the server
- [ ] `curl http://localhost:8000/health` returns `{"status": "ok"}`
- [ ] `/verify` endpoint works
- [ ] `/calculate` endpoint works
- [ ] You understand what "finfr" means (ontological death / forbidden state)

**All checked?** Welcome to verified computation! 🎉

---

## Learn More

| Document | Description | Time |
|----------|-------------|------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Complete tutorial with examples | 30 min |
| [TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md) | Full language guide | 1-2 hours |
| [TINYTALK_BIBLE.md](TINYTALK_BIBLE.md) | Philosophy and architecture | 30 min |
| [README.md](README.md) | Complete project overview | 10 min |

---

**The constraint IS the instruction. 1 == 1.**

*Now go build something impossible to break.*
