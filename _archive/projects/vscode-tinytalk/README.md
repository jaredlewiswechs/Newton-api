# TinyTalk VS Code Extension

**The No-First programming language** — now in VS Code.

## Features

✨ **Syntax Highlighting** — Full TinyTalk grammar support  
📝 **Snippets** — Quick templates for laws, forges, blueprints  
▶️ **Run Files** — Ctrl+Shift+R to run your TinyTalk code  
🔄 **Transpile to JS** — Convert TinyTalk to JavaScript  
🔍 **Real-time Linting** — Catch syntax errors as you type  

## Installation

### From Marketplace (Recommended)
Search for "TinyTalk" in the VS Code Extensions panel.

### From VSIX (Manual)
1. Download the `.vsix` file from releases
2. In VS Code: Extensions → ... → Install from VSIX

## Usage

### File Extensions
- `.tt` — TinyTalk files
- `.tinytalk` — Alternative extension

### Commands
| Command | Keybinding | Description |
|---------|------------|-------------|
| Run TinyTalk File | `Ctrl+Shift+R` | Execute the current file |
| Run Selection | Right-click menu | Run selected code |
| Transpile to JS | Command palette | Convert to JavaScript |

### Snippets
Type these prefixes and press Tab:

| Prefix | Creates |
|--------|---------|
| `law` | Law (pure function) definition |
| `forge` | Forge (action) definition |
| `blueprint` | Blueprint (struct) definition |
| `let` | Variable declaration |
| `when` | Constant declaration |
| `if` / `ife` | If / If-else statement |
| `for` | For loop |
| `while` | While loop |
| `_map` | Map step |
| `_filter` | Filter step |
| `main` | Main program template |
| `newton` | Newton verification pattern |

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `tinytalk.pythonPath` | `python` | Path to Python interpreter |
| `tinytalk.showOutputOnRun` | `true` | Show output panel on run |
| `tinytalk.enableLinting` | `true` | Enable syntax checking |

## Example

```tinytalk
-- Hello TinyTalk!
let name = "World"

law greet(who)
    reply "Hello, " + who + "!"
end

show(greet(name))

-- Step chains
let nums = [5, 2, 8, 1, 9]
show(nums _sort _unique _reverse)
```

## Requirements

- VS Code 1.85.0+
- Python 3.9+ (for running TinyTalk)
- realTinyTalk interpreter in workspace

## Links

- [TinyTalk Programming Guide](../TINYTALK_PROGRAMMING_GUIDE.md)
- [TinyTalk Quickstart](../TINYTALK_QUICKSTART.md)
- [Newton Supercomputer](https://github.com/newton-supercomputer)

## License

MIT © Newton Supercomputer

---

*"The constraint is the instruction. The verification is the computation."*
