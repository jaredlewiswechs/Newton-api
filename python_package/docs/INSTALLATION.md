# Newton Installation Guide

Complete installation instructions for all platforms and use cases.

## Quick Install

```bash
pip install newton-computer
```

## Installation Options

### Client Only (Minimal)

For using TinyTalk locally and connecting to remote Newton servers:

```bash
pip install newton-computer
```

Dependencies: `requests`

### With Server Support

To run your own Newton server locally:

```bash
pip install newton-computer[server]
```

Additional dependencies: `fastapi`, `uvicorn`, `pydantic`, `cryptography`

### With Grounding (Fact-Checking)

For fact-checking with web search:

```bash
pip install newton-computer[grounding]
```

Additional dependencies: `googlesearch-python`

### Development

For contributing to Newton:

```bash
pip install newton-computer[dev]
```

Additional dependencies: `pytest`, `hypothesis`, `black`, `ruff`, `mypy`

### Everything

Install all optional dependencies:

```bash
pip install newton-computer[all]
```

## Installation from Source

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# Install in development mode
pip install -e .

# Or with all dependencies
pip install -e ".[all]"
```

### Install from GitHub

```bash
pip install git+https://github.com/jaredlewiswechs/Newton-api.git
```

## Verify Installation

### Check Version

```bash
python -c "import newton; print(newton.__version__)"
```

### Run Demo

```bash
newton demo
```

### Test TinyTalk

```python
from newton import Blueprint, field, law, forge, when, finfr

class Test(Blueprint):
    value = field(int, default=0)

    @law
    def positive(self):
        when(self.value < 0, finfr)

    @forge
    def set(self, v):
        self.value = v

t = Test()
t.set(10)
print(f"Success! Value: {t.value}")
```

## Platform-Specific Notes

### macOS

Works out of the box with Python 3.9+.

```bash
# Using Homebrew Python
brew install python@3.11
pip3 install newton-computer
```

### Linux

Works with most distributions. Ensure you have Python 3.9+.

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip
pip3 install newton-computer

# Fedora
sudo dnf install python3 python3-pip
pip3 install newton-computer
```

### Windows

Install Python from python.org, then:

```powershell
pip install newton-computer
```

## Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install newton
RUN pip install newton-computer[server]

# Copy your code
COPY . .

# Run server
CMD ["newton", "serve", "--port", "8000"]
```

## Virtual Environments

Recommended for isolation:

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install
pip install newton-computer
```

## Troubleshooting

### "Module not found: newton"

Make sure you installed the package:
```bash
pip install newton-computer
pip list | grep newton
```

### "Server dependencies not installed"

Install with server support:
```bash
pip install newton-computer[server]
```

### Python version issues

Newton requires Python 3.9+. Check your version:
```bash
python --version
```

### Permission errors

Use `--user` flag or virtual environment:
```bash
pip install --user newton-computer
```

## Upgrading

```bash
pip install --upgrade newton-computer
```

## Uninstalling

```bash
pip uninstall newton-computer
```

## Next Steps

1. [Quick Start Guide](QUICKSTART.md)
2. [API Reference](api/TINYTALK_REFERENCE.md)
3. [Examples](../examples/)
