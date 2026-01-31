# TinyTalk Installation Guide

## Quick Install (Automated)

### Linux / macOS
```bash
cd tinytalk-lang
chmod +x install.sh
./install.sh
```

### Windows
```cmd
cd tinytalk-lang
install.bat
```

## Manual Installation

### Prerequisites

You need:
- **C Compiler**: GCC or Clang
- **Make**: Build tool
- **C11 Support**: Standard C library

### Installing Prerequisites

#### macOS
```bash
# Install Xcode Command Line Tools (includes clang + make)
xcode-select --install

# OR install GCC via Homebrew
brew install gcc make
```

#### Ubuntu / Debian Linux
```bash
sudo apt-get update
sudo apt-get install build-essential
```

#### Fedora / RHEL Linux
```bash
sudo dnf install gcc make
```

#### Windows

**Option 1: MinGW-w64 (Recommended)**
1. Download from: https://www.mingw-w64.org/downloads/
2. Install to `C:\mingw-w64`
3. Add `C:\mingw-w64\bin` to PATH

**Option 2: Chocolatey**
```powershell
choco install mingw make
```

**Option 3: WSL (Windows Subsystem for Linux)**
```bash
# In WSL terminal
sudo apt-get install build-essential
```

### Build Steps

```bash
cd tinytalk-lang
make
```

This creates the `tinytalk` executable.

### Verify Installation

```bash
# Run a test script
./tinytalk run examples/hello_world.tt

# Start interactive REPL
./tinytalk repl

# Check syntax of a file
./tinytalk check examples/calculator.tt
```

## System-Wide Installation

### Linux / macOS
```bash
sudo cp tinytalk /usr/local/bin/
# Now run from anywhere:
tinytalk run myfile.tt
```

### Windows
Add the `tinytalk-lang` folder to your PATH:
```cmd
setx PATH "%PATH%;C:\path\to\Newton-api\tinytalk-lang"
```

## Troubleshooting

### "gcc: command not found"
Install a C compiler (see Prerequisites above).

### "make: command not found"
Install Make:
- macOS: `brew install make`
- Linux: `sudo apt-get install make`
- Windows: `choco install make`

### Compilation errors
Ensure you have C11 support:
```bash
gcc --version  # Should be 4.9+
clang --version  # Should be 3.1+
```

## What is GCC/Clang?

**GCC** (GNU Compiler Collection) and **Clang** are C compilers that turn human-readable C code into machine code (executables).

Think of them like:
- **Python** needs a Python interpreter
- **Java** needs the JDK
- **TinyTalk** (C version) needs a C compiler

Once compiled, you get a standalone `tinytalk` program that doesn't need the compiler anymore!

## Alternative: Use Python Version

If you don't want to deal with C compilers, use the Python implementation:

```bash
# From Newton-api root
pip install -e .
newton demo
```

This installs TinyTalk as a Python package - no compilers needed!
