# TinyTalk IDE

**No-First Programming Environment with Newton Verification**

```
╭──────────────────────────────────────────────────────────╮
│                                                          │
│   🍎 TinyTalk IDE                                        │
│   "Define what CANNOT happen."                           │
│                                                          │
│   Monaco Editor + Real-time Verification + Ledger        │
│                                                          │
╰──────────────────────────────────────────────────────────╯
```

## Overview

TinyTalk IDE is a browser-based development environment for writing and running TinyTalk programs with real-time constraint verification. It features:

- **Monaco Editor** with TinyTalk syntax highlighting
- **Live AST visualization** showing parsed blueprint structure
- **Real-time verification** (`fin`/`finfr` status)
- **Immutable ledger** tracking all state changes
- **WebSocket streaming** for live logs

---

## Prerequisites

Before installing, ensure you have:

- **Node.js** (v18 or later recommended)
- **npm** (comes with Node.js)

### Installing Node.js

#### Windows

1. Download the Windows installer from [nodejs.org](https://nodejs.org/)
2. Run the installer (`.msi` file)
3. Follow the installation wizard (accept defaults)
4. Verify installation by opening **Command Prompt** or **PowerShell**:
   ```cmd
   node --version
   npm --version
   ```

Alternatively, use **winget** (Windows Package Manager):
```cmd
winget install OpenJS.NodeJS.LTS
```

Or use **Chocolatey**:
```cmd
choco install nodejs-lts
```

#### macOS

Using Homebrew:
```bash
brew install node
```

Or download from [nodejs.org](https://nodejs.org/)

#### Linux (Ubuntu/Debian)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

---

## Installation

### Step 1: Clone the Repository (if you haven't already)

```bash
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api
```

### Step 2: Navigate to TinyTalk IDE

```bash
cd tinytalk-ide
```

### Step 3: Install Dependencies

```bash
npm install
```

This installs all required packages including:
- Express (backend server)
- Vite (frontend build tool)
- React (UI framework)
- Monaco Editor (code editor)
- WebSocket support

---

## Running the IDE

### Development Mode (Recommended for First-Time Users)

Development mode runs both the backend server and frontend with hot-reloading:

```bash
npm run dev
```

This starts:
- **Backend server** at `http://localhost:3000`
- **Frontend dev server** at `http://localhost:5173`

Open your browser to `http://localhost:5173` to use the IDE.

### Production Mode

For production deployment:

```bash
# Build the frontend
npm run build

# Start the server
npm start
```

The server runs at `http://localhost:3000` serving both API and built frontend.

---

## Windows-Specific Instructions

### Running from Command Prompt

```cmd
cd path\to\Newton-api\tinytalk-ide
npm install
npm run dev
```

### Running from PowerShell

```powershell
cd path\to\Newton-api\tinytalk-ide
npm install
npm run dev
```

### Running from Git Bash

```bash
cd /c/path/to/Newton-api/tinytalk-ide
npm install
npm run dev
```

### Troubleshooting Windows Issues

#### Port Already in Use

If you see `EADDRINUSE`, another process is using the port:

```cmd
# Find the process using port 3000
netstat -ano | findstr :3000

# Kill the process (replace PID with the actual process ID)
taskkill /PID <PID> /F
```

#### Permission Errors

Run your terminal as Administrator, or try:

```cmd
npm cache clean --force
npm install
```

#### Long Path Issues

Enable long paths in Windows (run as Administrator):

```cmd
git config --system core.longpaths true
```

#### Node.js Not Recognized

If `node` is not recognized, add Node.js to your PATH:

1. Open **System Properties** → **Advanced** → **Environment Variables**
2. Under **System Variables**, find `Path` and click **Edit**
3. Add the Node.js installation directory (typically `C:\Program Files\nodejs\`)
4. Click **OK** and restart your terminal

---

## Quick Start Guide

Once the IDE is running:

1. **Write TinyTalk code** in the editor (left panel)
2. **View the AST** in the center panel
3. **Run forges** using the Run button
4. **Check the ledger** to see state history (right panel)
5. **Load examples** from the Examples dropdown

### Example: Bank Account

```tinytalk
blueprint BankAccount {
    field balance: 100.0

    law no_overdraft {
        when(balance < 0, finfr)
    }

    forge deposit(amount) {
        balance = balance + amount
        reply("Deposited $" + amount)
    }

    forge withdraw(amount) {
        balance = balance - amount
        reply("Withdrew $" + amount)
    }
}
```

Try running:
1. `deposit(50)` → ✓ fin
2. `withdraw(30)` → ✓ fin
3. `withdraw(200)` → ✗ finfr (blocked by `no_overdraft`)

---

## Project Structure

```
tinytalk-ide/
├── server/                 # Backend server
│   ├── index.js           # Express + WebSocket server
│   └── engine/            # TinyTalk engine
│       ├── tokenizer.js   # Lexical analysis
│       ├── parser.js      # AST generation
│       ├── runner.js      # Verification & execution
│       └── ledger.js      # Immutable state history
│
├── src/                    # Frontend (React + Vite)
│   ├── App.jsx            # Main application
│   ├── main.jsx           # Entry point
│   ├── components/        # UI components
│   │   ├── Editor.jsx     # Monaco editor wrapper
│   │   └── ASTPanel.jsx   # AST visualization
│   ├── language/          # TinyTalk language support
│   │   └── tinytalk.js    # Syntax highlighting
│   └── styles/            # CSS styles
│       └── ide.css        # IDE styling
│
├── examples/               # Example TinyTalk programs
├── index.html             # HTML entry point
├── package.json           # Dependencies & scripts
└── vite.config.mjs        # Vite configuration
```

---

## API Endpoints

The server exposes these REST endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/parse` | POST | Parse source, return AST |
| `/api/verify` | POST | Verify a forge action |
| `/api/run` | POST | Run a forge (verify + execute) |
| `/api/run-sequence` | POST | Run multiple forges |
| `/api/state/:blueprint` | GET | Get current state |
| `/api/omega/:blueprint` | GET | Get constraint space |
| `/api/ledger/:blueprint` | GET | Get ledger entries |
| `/api/reset/:blueprint` | POST | Reset to initial state |
| `/api/blueprints` | GET | List loaded blueprints |
| `/api/examples` | GET | List example files |
| `/api/examples/:name` | GET | Get example source |

WebSocket available at `ws://localhost:3000/ws` for streaming logs.

---

## Need Help?

| Resource | Link |
|----------|------|
| TinyTalk Language Guide | [TINYTALK_PROGRAMMING_GUIDE.md](../TINYTALK_PROGRAMMING_GUIDE.md) |
| TinyTalk Bible | [TINYTALK_BIBLE.md](../TINYTALK_BIBLE.md) |
| Getting Started | [GETTING_STARTED.md](../GETTING_STARTED.md) |
| Developer Guide | [DEVELOPERS.md](../DEVELOPERS.md) |

---

## License

Part of the Newton project.

- **Open Source (Non-Commercial)**: Personal projects, academic research, non-profit
- **Commercial License Required**: SaaS, enterprise, revenue-generating applications

See [LICENSE](../LICENSE) for details.

---

© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company

*"The constraint IS the instruction."*
