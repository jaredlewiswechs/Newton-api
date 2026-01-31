# TinyTalk Quick Start Guide

**Turing-Complete Constraint-First Programming**

Choose your path:

## 🐍 Python Version (Easiest)

No compilers needed! Just Python.

```bash
# From Newton-api root
pip install -e .
newton demo
```

Use in Python:
```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class Player(Blueprint):
    health = field(int, default=100)
```

**Turing complete** with bounded loops for guaranteed termination.

---

## 💻 C Version (Standalone Executable)

Build a native executable for maximum performance.

```bash
cd tinytalk-lang
./install.sh  # macOS/Linux
# OR
install.bat   # Windows
```

Use from command line:
```bash
tinytalk run myprogram.tt
tinytalk repl
```

**Full C implementation** - fast, portable, Turing complete with deterministic execution.

### Installation Guide

See [`tinytalk-lang/INSTALL.md`](tinytalk-lang/INSTALL.md) for complete installation instructions including:
- Compiler requirements (GCC/Clang)
- Platform-specific setup (Windows/macOS/Linux)
- Troubleshooting

---

## 🌐 Web IDE (Browser-Based)

Code in your browser with Monaco editor. Turing complete with live feedback.

```bash
cd tinytalk-ide
npm install
npm run dev
```

Open: http://localhost:5173

**Features:**
- Monaco editor (VS Code engine)
- Syntax highlighting & autocomplete
- Live error checking
- Hover documentation
- Code snippets

### Prerequisites

Requires **Node.js 18+**. Installation instructions:
- Windows: `winget install OpenJS.NodeJS.LTS` or download from nodejs.org
- macOS: `brew install node`
- Linux: `curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs`

See [`tinytalk-ide/README.md`](tinytalk-ide/README.md) for details.

---

## 📖 What's What?

| Folder | What | When to Use | Turing Complete |
|--------|------|-------------|-----------------|
| `tinytalk_py/` | Python implementation | Quick scripts, integration | ✅ Yes (bounded) |
| `tinytalk-lang/` | C implementation | Standalone programs, learning | ✅ Yes (bounded) |
| `tinytalk-ide/` | Web editor | Visual development, teaching | ✅ Yes (bounded) |

All implementations are **Turing complete** with bounded loops, meaning they can compute anything a Turing machine can while guaranteeing termination.

---

## 🎓 Next Steps

1. **Read the guide**: `TINYTALK_PROGRAMMING_GUIDE.md`
2. **Try examples**: `tinytalk-lang/examples/`
3. **Read the spec**: `tinytalk-lang/SPEC.md`
4. **Language reference**: `tinytalk-lang/README.md`

---

## 🚀 Quick Examples

### Hello World
```tinytalk
blueprint Greeter
  starts name at "World"

when say_hello
  set Screen.text to "Hello, " & name
finfr "Greeting displayed"
```

### Calculator (Turing Complete)
```tinytalk
blueprint Calculator
  starts result at 0
  
when add(a, b)
  calc a plus b as sum
  set result to sum
finfr result

when multiply(a, b)
  calc a times b as product
  set result to product
finfr result
```

### Bank Account (ACID Transactions)
```tinytalk
blueprint BankAccount
  starts balance at 1000

when withdraw(amount)
  must balance is above amount
    otherwise "Insufficient funds"
  
  calc balance minus amount as new_balance
  set balance to new_balance
finfr "Withdrawal successful"
```

If the `must` constraint fails, the entire transaction rolls back automatically - that's ACID semantics!

---

## 💡 Key Concepts

### Turing Completeness
TinyTalk can compute anything a Turing machine can, but with **bounded execution** to guarantee termination:
- No infinite loops
- Maximum iteration limits
- Deterministic execution paths

### ACID Semantics
Every `when` action is a transaction:
- **Atomic**: All or nothing
- **Consistent**: Constraints enforced
- **Isolated**: No partial states
- **Durable**: Immutable ledger

### Constraint-First
Define what **CANNOT** happen:
```tinytalk
must balance is above 0
  otherwise "Account must have positive balance"
```

The system prevents invalid states before they occur, not after.

---

## 🛠️ Troubleshooting

### C Version Won't Build
1. Install compiler: `gcc --version` or `clang --version`
2. Install make: `make --version`
3. See [`tinytalk-lang/INSTALL.md`](tinytalk-lang/INSTALL.md)

### IDE Won't Start
1. Check Node.js: `node --version` (need 18+)
2. Clear cache: `rm -rf node_modules && npm install`
3. See [`tinytalk-ide/README.md`](tinytalk-ide/README.md)

### Python Version Issues
```bash
pip install -e .
python -c "from tinytalk_py import Blueprint; print('OK')"
```

---

**The constraint IS the instruction. 1 == 1.**

*Now go build something impossible to break.*
