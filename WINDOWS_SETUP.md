# Newton Supercomputer - Windows Setup Guide

```
    ╭──────────────────────────────────────────────────────────────╮
    │                                                              │
    │   🍎 Newton on Windows                                       │
    │                                                              │
    │   "The constraint IS the instruction."                      │
    │   Works on your laptop. No cloud needed.                    │
    │                                                              │
    ╰──────────────────────────────────────────────────────────────╯
```

**Complete guide for running Newton Supercomputer on Windows**

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step-by-Step Installation](#step-by-step-installation)
- [Running Newton](#running-newton)
- [Testing Newton](#testing-newton)
- [Using Newton](#using-newton)
- [Troubleshooting](#troubleshooting)
- [Common Windows Issues](#common-windows-issues)
- [Development Tools](#development-tools)

---

## Prerequisites

### Required Software

1. **Python 3.9 or higher**
   - Download from: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation
   - Verify installation: Open Command Prompt and type `python --version`

2. **Git for Windows**
   - Download from: https://git-scm.com/download/win
   - Use default installation options
   - Verify: Open Command Prompt and type `git --version`

3. **Windows Terminal** (Optional but Recommended)
   - Install from Microsoft Store or https://aka.ms/terminal
   - Makes working with multiple terminals much easier

### System Requirements

- **OS:** Windows 10 or Windows 11
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB free space
- **Internet:** Required for initial setup only

---

## Step-by-Step Installation

### Method 1: Quick Install (Recommended)

Open **Command Prompt** or **PowerShell** as Administrator:

```cmd
REM 1. Navigate to where you want to install Newton
cd C:\Users\YourName\Documents

REM 2. Clone the repository
git clone https://github.com/jaredlewiswechs/Newton-api.git

REM 3. Enter the directory
cd Newton-api

REM 4. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 5. Install Newton SDK
pip install -e .

REM 6. Test the installation
python test_full_system.py
```

### Method 2: With Virtual Environment (Best Practice)

Using a virtual environment keeps Newton's dependencies isolated:

```cmd
REM 1. Clone repository
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

REM 2. Create virtual environment
python -m venv venv

REM 3. Activate virtual environment
venv\Scripts\activate.bat

REM You should see (venv) in your prompt

REM 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

REM 5. Verify installation
python test_full_system.py
```

### Method 3: PowerShell (Alternative)

If you prefer PowerShell:

```powershell
# 1. Enable script execution (one-time setup)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Clone repository
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 6. Test installation
python .\test_full_system.py
```

---

## Running Newton

### Starting the Server

**Option 1: Command Prompt**

```cmd
REM Navigate to Newton directory
cd C:\path\to\Newton-api

REM Activate virtual environment (if using one)
venv\Scripts\activate.bat

REM Start the server
python newton_supercomputer.py
```

**Option 2: PowerShell**

```powershell
# Navigate to Newton directory
cd C:\path\to\Newton-api

# Activate virtual environment (if using one)
.\venv\Scripts\Activate.ps1

# Start the server
python .\newton_supercomputer.py
```

**Option 3: Windows Terminal (Recommended)**

1. Open Windows Terminal
2. Navigate to Newton directory
3. Split pane: `Ctrl+Shift+D` (or click the + dropdown → Split)
4. Left pane: `python newton_supercomputer.py`
5. Right pane: Run tests or use the API

**Expected Output:**
```
═══════════════════════════════════════════════════════════════
              NEWTON SUPERCOMPUTER - STARTING
═══════════════════════════════════════════════════════════════

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

Newton is ready. The constraint IS the instruction. 1 == 1.
```

### Accessing the Web Interface

Once the server is running:

1. Open your browser
2. Go to: http://localhost:8000
3. You should see the Newton interface

---

## Testing Newton

### Quick System Test (5 seconds)

Open a **second terminal** while Newton is running:

```cmd
REM Command Prompt
cd C:\path\to\Newton-api
python test_full_system.py

REM PowerShell
cd C:\path\to\Newton-api
python .\test_full_system.py
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

RESULTS: 10/10 tests passed
✓ ALL SYSTEMS OPERATIONAL
```

### Comprehensive Test (30 seconds)

Tests all 118+ endpoints and features:

```cmd
python test_comprehensive_system.py
```

### Unit Tests (2 minutes)

```cmd
REM Run all unit tests
pytest tests\ -v

REM Run specific test file
pytest tests\test_properties.py -v
```

---

## Using Newton

### From Command Line (curl)

If you have curl installed (comes with Git Bash or Windows 10+):

```cmd
REM Health check
curl http://localhost:8000/health

REM Verify content
curl -X POST http://localhost:8000/verify ^
  -H "Content-Type: application/json" ^
  -d "{\"input\": \"What is 2+2?\"}"

REM Calculate
curl -X POST http://localhost:8000/calculate ^
  -H "Content-Type: application/json" ^
  -d "{\"expression\": {\"op\": \"+\", \"args\": [2, 2]}}"
```

### From PowerShell (Invoke-WebRequest)

```powershell
# Health check
Invoke-WebRequest -Uri http://localhost:8000/health

# Verify content
$body = @{
    input = "What is 2+2?"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/verify `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

# Calculate
$calc = @{
    expression = @{
        op = "+"
        args = @(2, 2)
    }
} | ConvertTo-Json -Depth 3

Invoke-WebRequest -Uri http://localhost:8000/calculate `
  -Method POST `
  -ContentType "application/json" `
  -Body $calc
```

### From Python

Create a file `test_newton.py`:

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print("Health:", response.json())

# Verify content
response = requests.post(
    "http://localhost:8000/verify",
    json={"input": "What is 2+2?"}
)
print("Verify:", response.json())

# Calculate
response = requests.post(
    "http://localhost:8000/calculate",
    json={"expression": {"op": "+", "args": [2, 2]}}
)
print("Calculate:", response.json())
```

Run it:
```cmd
python test_newton.py
```

### Using Newton SDK

```python
from newton_sdk import NewtonClient

# Create client
client = NewtonClient(base_url="http://localhost:8000")

# Verify content
result = client.verify("What is 2+2?")
print(f"Verified: {result['verified']}")

# Evaluate constraint
result = client.constraint(
    constraint={"field": "age", "operator": "ge", "value": 18},
    obj={"age": 25}
)
print(f"Passed: {result['passed']}")

# Calculate
result = client.calculate({"op": "+", "args": [2, 2]})
print(f"Result: {result['result']}")
```

---

## Troubleshooting

### Python Not Found

**Problem:** `'python' is not recognized as an internal or external command`

**Solution:**
1. Reinstall Python from https://www.python.org/downloads/
2. ⚠️ **Check "Add Python to PATH"** during installation
3. Restart Command Prompt
4. Try `py` instead of `python`

### Port Already in Use

**Problem:** `Address already in use: 127.0.0.1:8000`

**Solution:**
```cmd
REM Find process using port 8000
netstat -ano | findstr :8000

REM Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Permission Denied

**Problem:** `Access is denied` when running scripts

**Solution:**
1. Run Command Prompt or PowerShell as Administrator
   - Right-click on the app → "Run as Administrator"
2. Or change PowerShell execution policy:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```cmd
REM Make sure virtual environment is activated
venv\Scripts\activate.bat

REM Reinstall dependencies
pip install -r requirements.txt
```

### Git Clone Fails

**Problem:** Git commands not working

**Solution:**
1. Install Git for Windows: https://git-scm.com/download/win
2. Restart Command Prompt
3. Configure Git:
   ```cmd
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

### Firewall Blocking

**Problem:** Windows Firewall blocks Python

**Solution:**
1. When prompted, click "Allow access"
2. Or manually add exception:
   - Windows Security → Firewall & network protection
   - Allow an app through firewall
   - Find Python and check both Private and Public

---

## Common Windows Issues

### Line Ending Issues

Windows uses CRLF (`\r\n`) while Linux uses LF (`\n`). Git handles this automatically, but if you see issues:

```cmd
REM Configure Git to handle line endings
git config --global core.autocrlf true
```

### Path Length Issues

Windows has a 260 character path limit (older versions):

```cmd
REM Enable long paths (Windows 10+)
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

Or install in a shorter path like `C:\Newton`

### Antivirus Interference

Some antivirus software may flag Python scripts:

1. Add Newton directory to antivirus exclusions
2. Or temporarily disable real-time protection during installation

---

## Development Tools

### Recommended IDE Setup

**Visual Studio Code** (Free, Recommended)
- Download: https://code.visualstudio.com/
- Install Python extension
- Open Newton folder: `code .`
- Integrated terminal: `Ctrl+` `

**PyCharm** (Professional or Community)
- Download: https://www.jetbrains.com/pycharm/
- Open Newton folder
- Configure Python interpreter to use virtual environment

### Useful Tools

**Windows Terminal**
- Best terminal for Windows
- Install from Microsoft Store

**Git Bash**
- Unix-like terminal on Windows
- Comes with Git for Windows

**Postman**
- Test API endpoints visually
- Download: https://www.postman.com/downloads/

---

## Running as Windows Service

To run Newton as a background service:

### Using NSSM (Non-Sucking Service Manager)

```cmd
REM 1. Download NSSM from https://nssm.cc/download

REM 2. Install Newton as service
nssm install Newton "C:\path\to\venv\Scripts\python.exe" "C:\path\to\Newton-api\newton_supercomputer.py"

REM 3. Start the service
nssm start Newton

REM 4. Check status
nssm status Newton

REM 5. Stop the service
nssm stop Newton

REM 6. Remove service
nssm remove Newton confirm
```

### Using Python Script

Create `run_newton_service.py`:

```python
import subprocess
import sys

def run_service():
    """Run Newton as a background service"""
    subprocess.Popen(
        [sys.executable, "newton_supercomputer.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    print("Newton service started in background")

if __name__ == "__main__":
    run_service()
```

---

## Batch Scripts for Convenience

### `start_newton.bat`

```batch
@echo off
echo Starting Newton Supercomputer...

cd /d %~dp0
call venv\Scripts\activate.bat
python newton_supercomputer.py

pause
```

### `test_newton.bat`

```batch
@echo off
echo Testing Newton...

cd /d %~dp0
call venv\Scripts\activate.bat
python test_full_system.py

pause
```

### `stop_newton.bat`

```batch
@echo off
echo Stopping Newton...

FOR /F "tokens=5" %%A IN ('netstat -ano ^| findstr :8000') DO taskkill /PID %%A /F

echo Newton stopped.
pause
```

Save these in the Newton-api directory and double-click to run.

---

## Performance Tips for Windows

1. **Disable Windows Defender real-time scanning** for Newton directory (improves startup time)
2. **Use SSD** instead of HDD (faster I/O)
3. **Close unnecessary applications** (more RAM for Newton)
4. **Use Windows Terminal** instead of cmd.exe (better performance)
5. **Enable hardware virtualization** in BIOS (if running in VM)

---

## Next Steps

Now that Newton is installed:

1. ✅ **Test it** - Run `python test_full_system.py`
2. 📚 **Learn tinyTalk** - Read `TINYTALK_PROGRAMMING_GUIDE.md`
3. 🚀 **Try examples** - Check `examples/` directory
4. 🔨 **Build something** - Use the Newton SDK
5. 📖 **Read docs** - See `GETTING_STARTED.md`

---

## Support

If you're stuck:

1. Check this troubleshooting guide
2. Review `TESTING.md` for test help
3. Read `README.md` for overview
4. Check GitHub Issues: https://github.com/jaredlewiswechs/Newton-api/issues

---

## Summary

```cmd
REM Quick start on Windows:

1. Install Python 3.9+ (Add to PATH!)
2. git clone https://github.com/jaredlewiswechs/Newton-api.git
3. cd Newton-api
4. pip install -r requirements.txt
5. pip install -e .
6. python newton_supercomputer.py    (Terminal 1)
7. python test_full_system.py         (Terminal 2)

If all tests pass: Newton is ready! 1 == 1.
```

---

**Last Updated:** January 31, 2026

**Tested on:** Windows 10 (21H2), Windows 11 (22H2)

**Maintained by:** Jared Lewis Conglomerate
