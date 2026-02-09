# tinyTalk Objective-C Implementation

A complete implementation of the **tinyTalk constraint-first programming language** built on Objective-C and the Foundation framework.

## Philosophy

> "1 == 1. The cloud is weather. We're building shelter."

Traditional languages are **"Yes-First"**: they explore every branch until finding an error.

**tinyTalk is "No-First"**: it defines the boundary space where reality is allowed to exist. You are not writing a script; you are defining the **Physics of your World**.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: APPLICATION (Sovereign App)                       │
│  The Solution - Specific interfaces                         │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: EXECUTIVE (Forges)                               │
│  The Engine - Handles state mutation                        │
├─────────────────────────────────────────────────────────────┤
│  LAYER 0: GOVERNANCE (Laws)                                │
│  The Physics - Defines "Vault Walls"                        │
└─────────────────────────────────────────────────────────────┘
```

## Components

| File | Purpose |
|------|---------|
| `TTToken.h/m` | Token types and token objects |
| `TTLexer.h/m` | Tokenizer - converts source to tokens |
| `TTAST.h/m` | Abstract Syntax Tree node definitions |
| `TTParser.h/m` | Parser - builds AST from tokens |
| `TTValue.h/m` | Runtime value types with operations |
| `TTRuntime.h/m` | Execution engine with ACID semantics |
| `main.m` | CLI interface |

## Building

### macOS

```bash
make
```

### Requirements

- macOS with Xcode Command Line Tools
- OR GNUstep on Linux

## Usage

```bash
# Run a program
./tinytalk run game.tt

# Check syntax
./tinytalk check player.tt

# Show tokens (debugging)
./tinytalk tokens game.tt

# Show AST (debugging)
./tinytalk ast game.tt

# Interactive REPL
./tinytalk repl
```

## Language Features

### Keywords

| Keyword | Purpose |
|---------|---------|
| `when` | Declares a Fact (present state) |
| `and` | Joins multiple facts |
| `fin` | Semantic completion (can be reopened) |
| `finfr` | Ontological death (state is forbidden) |
| `law` | Defines constraint (the Physics) |
| `forge` | Defines action (the Machinery) |

### Example: Risk Governor

```tinytalk
blueprint RiskGovernor
  # L0: GOVERNANCE (The Law)
  law Insolvency
    when liabilities > assets
    finfr  # This state cannot exist

  # L1: EXECUTIVE (The Machinery)
  field @assets: Money
  field @liabilities: Money

  forge execute_trade(amount: Money)
    liabilities = liabilities + amount
    reply :cleared
  end
end
```

### Example: Player

```tinytalk
blueprint Player
  starts @health at 100
  starts @cash at 50
  starts inventory as empty
  
  can be alive
  can be dead
  
  when take_damage(amount)
    block if @health is below 0
    calc @health minus amount as new_health
    set @health to new_health
    fin
    
  when buy_item(item)
    must @cash is above item.price
      otherwise "Not enough money"
    calc @cash minus item.price as new_cash
    set @cash to new_cash
    change inventory by + item.name
    fin
end
```

## ACID Semantics

The runtime provides **ACID transaction semantics**:

- **Atomicity**: Actions in a `when`/`forge` either all succeed or all rollback
- **Consistency**: Laws are checked before AND after every action
- **Isolation**: Each transaction operates on a snapshot
- **Durability**: Committed state persists in the World

## Execution Bounds

All computations are bounded to ensure **deterministic termination**:

| Bound | Default | Purpose |
|-------|---------|---------|
| `maxIterations` | 10,000 | Prevent infinite loops |
| `maxRecursionDepth` | 100 | Prevent stack overflow |
| `maxOperations` | 1,000,000 | Prevent runaway compute |
| `timeoutSeconds` | 30.0 | Prevent endless waits |

## Core Principle

```
newton(current, goal) → current == goal
```

- When true → execute
- When false → halt (finfr)

This isn't a feature. It's the architecture.

## License

Copyright 2026 Jared Lewis Conglomerate / Newton Supercomputer

- **Open Source (Non-Commercial)**: Personal projects, academic research
- **Commercial License Required**: SaaS, enterprise applications
