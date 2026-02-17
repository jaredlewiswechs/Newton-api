# realTinyTalk

**The Verified General-Purpose Programming Language**

> Every loop bounded. Every operation traced. Every output proven.

realTinyTalk is a Turing-complete programming language with a Web IDE, built for verified computation. It combines the readability of Smalltalk with the safety guarantees of bounded, traceable execution.

---

## Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fjaredlewiswechs%2FrealTinyTalk)

Or deploy manually:

```bash
npm i -g vercel
vercel
```

The project is pre-configured with `vercel.json` — just connect the repo and deploy.

## Run Locally

```bash
# Clone the repo
git clone https://github.com/jaredlewiswechs/realTinyTalk.git
cd realTinyTalk

# Install dependencies
pip install -e .

# Start the Web IDE
python -m realTinyTalk.web.server
# Open http://localhost:5555
```

## Use as a Library

```python
from realTinyTalk import run

result = run('show("Hello World!")')
```

## CLI

```bash
# Run a .tt file
tinytalk run hello.tt

# Compile to JavaScript
tinytalk build -t js app.tt -o app.js

# Run tests
tinytalk test

# Interactive REPL
tinytalk repl
```

## Language Overview

```tinytalk
// Variables
let name = "Alice"
when PI = 3.14159

// Functions (law/reply/end)
law square(x)
    reply x * x
end

// Or the new syntax (when/do/finfr)
when double(x)
  do x * 2
finfr

// Control flow
for i in range(10) {
    show(i)
}

// Step chains (dplyr-style)
let top3 = numbers _sort _reverse _take(3)

// Blueprints (OOP)
blueprint Counter
    field value
    forge inc()
        self.value = self.value + 1
        reply self.value
    end
end

// Natural comparisons
show("Alice" islike "A*")
show([1, 2, 3] has 2)
```

## Project Structure

```
realTinyTalk/
├── api/
│   └── index.py           # Vercel serverless entry point
├── realTinyTalk/
│   ├── __init__.py         # Package exports, run(), repl()
│   ├── kernel.py           # Verified execution kernel
│   ├── lexer.py            # Tokenizer
│   ├── parser.py           # Recursive descent parser
│   ├── types.py            # Type system
│   ├── runtime.py          # Interpreter with bounded execution
│   ├── ffi.py              # Foreign function interface (Python, JS, Go, Rust)
│   ├── stdlib.py           # Standard library
│   ├── foghorn_stdlib.py   # Foghorn visual connection stdlib
│   ├── opendoc_stdlib.py   # OpenDoc stdlib
│   ├── cli.py              # CLI tool
│   ├── backends/
│   │   ├── js/             # JavaScript transpiler
│   │   └── python/         # Python transpiler
│   ├── web/
│   │   ├── server.py       # Flask Web IDE server
│   │   ├── static/         # Monaco-powered IDE frontend
│   │   └── tests/          # Server tests
│   ├── tests/              # Language test suite (.tt files + runner)
│   ├── examples/           # Example programs
│   └── hosted/             # Self-contained hosted IDE (single HTML)
├── vercel.json             # Vercel deployment config
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Package metadata
└── runtime.txt             # Python 3.12 (for Vercel)
```

## Web IDE Features

- Monaco-powered code editor with TinyTalk syntax highlighting
- 4 color themes
- Live code execution
- JavaScript and Python transpilation
- Server-side script persistence with versioning
- Multi-file tabs with autosave
- Example programs built in

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Web IDE |
| `POST` | `/api/run` | Execute TinyTalk code |
| `POST` | `/api/transpile/js` | Transpile to JavaScript |
| `POST` | `/api/transpile/python` | Transpile to Python |
| `GET` | `/api/examples` | Get example programs |
| `GET/POST/DELETE` | `/api/scripts` | Script persistence |
| `GET/POST/DELETE` | `/api/projects` | Project management |

## License

Dual Licensed:
- **Educational & Research (Free):** Students, educators, non-profits, open-source projects
- **Commercial (Paid):** Business use requires a commercial license

Attribution required: "realTinyTalk by Jared Nashon Lewis"
