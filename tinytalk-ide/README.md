# TinyTalk IDE

**Turing-Complete Constraint-First Programming Environment**

```
╭──────────────────────────────────────────────────────────╮
│                                                          │
│   🍎 TinyTalk IDE                                        │
│   "Define what CANNOT happen."                           │
│                                                          │
│   Monaco Editor + Real-time Verification + Ledger        │
│   Turing Complete with Bounded Loops                     │
│                                                          │
╰──────────────────────────────────────────────────────────╯
```

## Overview

TinyTalk IDE is a browser-based development environment for writing and running **Turing-complete** TinyTalk programs with real-time constraint verification. It features:

- **Monaco Editor** with TinyTalk syntax highlighting (same engine as VS Code)
- **Turing Complete** computation with bounded loops for guaranteed termination
- **ACID Semantics** with automatic transaction rollback
- **Live AST visualization** showing parsed blueprint structure
- **Real-time verification** (`fin`/`finfr` status)
- **Immutable ledger** tracking all state changes
- **WebSocket streaming** for live logs

---

## 🎯 What You Need

Before starting, you need **Node.js** installed. That's it!

### Quick Check
```bash
node --version   # Should show v18 or higher
npm --version    # Should show 9 or higher
```

### Don't Have Node.js?

**Windows:**
```powershell
# Option 1: Download installer
https://nodejs.org/  (get LTS version)

# Option 2: Use winget
winget install OpenJS.NodeJS.LTS

# Option 3: Use Chocolatey
choco install nodejs-lts
```

**macOS:**
```bash
# Option 1: Homebrew
brew install node

# Option 2: Download from nodejs.org
https://nodejs.org/
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

---

## 🚀 Installation

```bash
# 1. Navigate to IDE folder
cd tinytalk-ide

# 2. Install dependencies (one time only)
npm install

# 3. Start the IDE
npm run dev
```

Open your browser to: **http://localhost:5173**

---

## ✨ Features

The IDE includes:

✅ **Monaco Editor** - Same engine as VS Code  
✅ **Turing Complete** - Full computational power with bounded loops  
✅ **Syntax Highlighting** - All TinyTalk keywords  
✅ **Autocomplete** - Smart suggestions as you type  
✅ **Hover Docs** - Hover over keywords for help  
✅ **Error Markers** - Real-time syntax checking  
✅ **Code Snippets** - Templates for common patterns  
✅ **ACID Transactions** - Automatic rollback on constraint violations  
✅ **Dark Theme** - Easy on the eyes  
✅ **Live Execution** - Run code in browser (planned)

---

## 📝 Example Programs

Try these in the editor:

### Hello World
```tinytalk
blueprint Greeter
  starts name at "World"

when say_hello
  set Screen.text to "Hello, " & name
finfr "Greeting displayed"
```

### Calculator
```tinytalk
blueprint Calculator
  starts result at 0

when add(a, b)
  calc a plus b as sum
  set result to sum
finfr result
```

### Bank Account (ACID)
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

### Game Character (Turing Complete)
```tinytalk
blueprint Player
  starts health at 100
  starts max_health at 100
  can be wanted
  can be dead

when take_damage(amount)
  must health is above 0
    otherwise "Already dead"
  
  calc health minus amount as new_health
  set health to new_health
  
  block if health is below 0
finfr "Damage applied"

when heal(amount)
  calc health plus amount as new_health
  
  block if new_health is above max_health
  
  set health to new_health
finfr "Healed"
```

---

## 🛠️ Development

### Project Structure
```
tinytalk-ide/
├── server/              # Backend (optional)
│   └── index.js        # Express + WebSocket
├── src/
│   ├── App.jsx         # Main UI
│   ├── components/
│   │   └── Editor.jsx  # Monaco wrapper
│   └── language/
│       └── tinytalk.js # Language definition ⭐
├── package.json
└── vite.config.js
```

### Key File: `src/language/tinytalk.js`

This file defines ALL editor features:
- Syntax highlighting (tokenizer)
- Autocomplete (completion provider)
- Hover docs (hover provider)
- Theme colors

**Updated for C implementation** with keywords like `blueprint`, `starts`, `when`, `set`, `calc`, `must`, `block`, `finfr`.

### Customizing the Editor

**Add a new keyword:**
```javascript
// In tinytalk.js
keywords: [
  'blueprint', 'starts', 'when',
  'yournewkeyword',  // Add here
],
```

**Add autocomplete:**
```javascript
suggestions.push({
  label: 'yournewkeyword',
  kind: monaco.languages.CompletionItemKind.Keyword,
  insertText: 'yournewkeyword ${1:arg}',
  insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
  documentation: 'What it does',
});
```

**Change colors:**
```javascript
// In defineTheme()
{ token: 'keyword', foreground: 'FF0000' },  // Red keywords
```

---

## 🐛 Troubleshooting

### "npm: command not found"
Install Node.js (see above).

### "Port 5173 already in use"
```bash
# Kill the process
lsof -ti:5173 | xargs kill  # macOS/Linux
# Or change port in vite.config.js
```

### Changes not showing?
```bash
# Clear cache
rm -rf node_modules
npm install
npm run dev
```

### Windows: "cannot find module"
```cmd
# Clean install
rmdir /s /q node_modules
del package-lock.json
npm install
```

---

## 📚 Learn More

- **Monaco Editor Docs**: https://microsoft.github.io/monaco-editor/
- **TinyTalk Spec**: See `../tinytalk-lang/SPEC.md`
- **Language Reference**: See `../tinytalk-lang/README.md`
- **TinyTalk Guide**: See `../TINYTALK_PROGRAMMING_GUIDE.md`

---

## 🎓 Language Features

TinyTalk is **Turing complete** with bounded loops, meaning:
- Can compute anything a Turing machine can compute
- Guaranteed to terminate (no infinite loops)
- Deterministic execution
- ACID transaction semantics

### Core Keywords

| Keyword | Purpose |
|---------|---------|
| `blueprint` | Define a new type |
| `starts` | Declare a field with initial value |
| `can be` | Declare a possible state |
| `when` | Define an event handler |
| `set` | Assign a value |
| `calc` | Perform calculation |
| `must` | Assert constraint (rollback if false) |
| `block` | Prevent execution if condition true |
| `finfr` | Final termination (commit transaction) |

### Operators

**Arithmetic:** `plus`, `minus`, `times`, `div`, `mod`  
**Comparison:** `is`, `above`, `below`, `within`  
**String:** `&` (concatenation), `+` (join with space)

### Standard Kit

Pre-built blueprints available:
- **Screen** - Display output (`text`, `color`, `brightness`)
- **Clock** - Time management (`time_of_day`, `day_of_week`, `paused`)
- **Random** - Random values (`number`, `percent`, `dice`)
- **Input** - User input (`mouse_x`, `mouse_y`, `keys`)
- **Storage** - Persistence (`save_file`)

---

## License

Part of the Newton project.

- **Open Source (Non-Commercial)**: Personal projects, academic research, non-profit
- **Commercial License Required**: SaaS, enterprise, revenue-generating applications

See [LICENSE](../LICENSE) for details.

---

© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company

*"The constraint IS the instruction."*
