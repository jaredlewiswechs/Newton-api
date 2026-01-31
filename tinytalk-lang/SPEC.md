# tinyTalk 1.0 Language Specification

## 1. Introduction

tinyTalk is a **constraint-first programming language** where the constraint IS the instruction, and the verification IS the computation.

### Philosophy

Traditional languages are "Yes-First": they explore every branch until finding an error.
tinyTalk is "No-First": it defines the boundary space where reality is allowed to exist.

**Core Principle**: `newton(current, goal) → current == goal`
- When true → execute
- When false → halt

## 2. Lexical Structure

### 2.1 Keywords

Reserved words in tinyTalk:

```
blueprint  starts  can be  when  and  is  above  below  within
make  set  change  create  erase  each  fin  finfr  block  must
calc  plus  minus  times  div  rem  memo  if  otherwise
as  at  to  by  in  not  empty  world  reply  request  end
```

### 2.2 Operators

| Operator | Name | Purpose |
|----------|------|---------|
| `+` | Natural Add | Adds numbers OR joins strings with space |
| `&` | Fuse | Concatenates strings without space |
| `#` | Tag/Interpolation | String interpolation |
| `.` | Field Access | Access object fields |

### 2.3 Literals

**Numbers**: Integer or floating-point
```
42
3.14159
-100
0.5
```

**Strings**: Double-quoted
```
"Hello, World!"
"Newton Supercomputer"
""
```

**Identifiers**: Alphanumeric + underscore, starting with letter
```
player
health_points
item_01
```

### 2.4 Comments

Single-line comments start with `//`:
```tinytalk
// This is a comment
blueprint Player  // Inline comment
```

## 3. Grammar

### 3.1 Program Structure

A tinyTalk program consists of one or more blueprint declarations:

```ebnf
program        = blueprint+
blueprint      = "blueprint" IDENTIFIER field* state* when* "end"?
field          = "starts" IDENTIFIER "at" expression
               | "starts" IDENTIFIER "as" "empty"
state          = "can be" IDENTIFIER
when           = "when" IDENTIFIER params? condition* action* terminator
```

### 3.2 Blueprint Definition

```tinytalk
blueprint TypeName
  starts field_name at initial_value
  starts collection as empty
  can be state_name
  
  when event_name
    // actions
  finfr "message"
end
```

### 3.3 When Clauses

When clauses are event handlers that execute actions:

```tinytalk
when event_name
  condition*
  action*
  terminator
```

**Terminators**:
- `fin`: Normal completion (can be reopened)
- `finfr`: Final completion (ontological death, commits transaction)

### 3.4 Conditions

**Block**: Prevent execution if condition is true
```tinytalk
block if player.health is below 0
```

**Must**: Assert condition (rolls back if false)
```tinytalk
must player.cash is above item.price
  otherwise "Insufficient funds"
```

### 3.5 Actions

**Set**: Assign a value to a field
```tinytalk
set player.health to 100
set Screen.text to "Game Over"
```

**Make**: Change object state
```tinytalk
make player wanted
make enemy defeated
```

**Change**: Modify collection
```tinytalk
change inventory by + item.name
change inventory by - "sword"
```

**Calc**: Perform calculation
```tinytalk
calc health minus damage as new_health
calc price times quantity as total
```

**Memo**: Create temporary variable
```tinytalk
memo message starts "Hello, " & player.name
```

### 3.6 Expressions

**Binary Operations**:
```tinytalk
a plus b
a minus b
a times b
a div b
a rem b
```

**Comparisons**:
```tinytalk
value is above threshold
value is below limit
value is within range
value is equal_to expected
```

**Logic**:
```tinytalk
condition and other_condition
value in collection
value not in collection
```

**String Operations**:
```tinytalk
"Hello" + "World"        // "Hello World" (with space)
"Hello" & "World"        // "HelloWorld" (no space)
"Price: $#amount"        // Interpolation
```

## 4. Standard Kit

The Standard Kit provides 5 built-in blueprints:

### 4.1 Clock

Manages time in your simulation:

```tinytalk
blueprint Clock
  starts time_of_day at 0      // 0-2399 (24-hour time)
  starts day_count at 0         // Days elapsed
  starts paused at false        // Pause state
```

### 4.2 Random

Provides random number generation:

```tinytalk
blueprint Random
  starts number at 0.0-1.0      // Random float
  starts percent at 0-100       // Random percentage
  starts dice at 1-6            // Random dice roll
```

### 4.3 Input

Captures user input:

```tinytalk
blueprint Input
  starts mouse_x at 0           // Mouse X position
  starts mouse_y at 0           // Mouse Y position
  starts keys as empty          // Pressed keys array
```

### 4.4 Screen

Manages display output:

```tinytalk
blueprint Screen
  starts text at ""             // Text to display
  starts color at "white"       // Text color
  starts cleared at false       // Clear flag
```

### 4.5 Storage

Handles persistent data:

```tinytalk
blueprint Storage
  starts save_file at ""        // Save file path
  starts saved at false         // Save status
  starts loaded at false        // Load status
```

## 5. ACID Semantics

Every `when` clause executes as a transaction:

1. **Begin**: Transaction starts when `when` is invoked
2. **Execute**: All actions run
3. **Validate**: All `must` conditions checked
4. **Commit/Rollback**:
   - `finfr` → Commit changes
   - `block` or failed `must` → Rollback changes

Example:
```tinytalk
blueprint BankAccount
  starts balance at 1000

when withdraw(amount)
  must balance is above amount
    otherwise "Insufficient funds"
  
  calc balance minus amount as new_balance
  set balance to new_balance
finfr "Success"
```

If `must` fails:
- Transaction rolls back
- Balance unchanged
- Error message returned

## 6. Execution Bounds

All execution is deterministic with hard limits:

| Bound | Default | Purpose |
|-------|---------|---------|
| `max_iterations` | 10,000 | Prevent infinite loops |
| `max_recursion_depth` | 100 | Prevent stack overflow |
| `max_operations` | 1,000,000 | Prevent runaway compute |
| `timeout_seconds` | 30.0 | Prevent endless waits |

These bounds **cannot be exceeded** and guarantee termination.

## 7. Type System

### 7.1 Primitive Types

- **Number**: 64-bit floating-point
- **String**: UTF-8 text
- **Boolean**: `true` or `false`
- **Symbol**: Named identifier
- **Array**: Ordered collection
- **Null**: Absence of value

### 7.2 Blueprint Types

Custom types defined by blueprints:

```tinytalk
blueprint Player
  starts health at 100
```

Creates a new type `Player` with instances that have the `health` field.

## 8. Examples

### 8.1 Hello World

```tinytalk
blueprint Greeter
  starts name at "World"

when say_hello
  set Screen.text to "Hello, " & name
finfr "Greeting displayed"
```

### 8.2 GTA Purchase System

```tinytalk
blueprint Player
  starts cash at 0
  starts inventory as empty
  can be wanted

blueprint Weapon
  starts name at "Pistol"
  starts price at 500
  can be illegal

when buy_item(player, item)
  block if player.health is below 0
  
  must player.cash is above item.price
    otherwise "You need $#item.price to buy this."
  
  calc player.cash minus item.price as new_balance
  
  set player.cash to new_balance
  change player.inventory by + item.name
  
  if item is illegal
    make player wanted
    
    memo alert starts "SUSPECT BOUGHT: " & item.name
    make alert uppercase
    set Screen.text to alert

finfr "Purchase Successful"
```

### 8.3 Inventory Management

```tinytalk
blueprint Inventory
  starts items as empty
  starts capacity at 10
  
when add_item(name)
  block if items.count is above capacity
  change items by + name
finfr "Item added"

when remove_item(name)
  block if name not in items
  change items by - name
finfr "Item removed"
```

## 9. Error Handling

tinyTalk uses **preventive error handling**:

1. **Block**: Prevents execution before it starts
2. **Must**: Validates during execution
3. **Rollback**: Undoes changes on failure

Traditional try/catch is replaced by constraint checking.

## 10. Best Practices

### 10.1 Naming Conventions

- **Blueprints**: PascalCase (`Player`, `GameWorld`)
- **Fields**: snake_case (`health_points`, `item_count`)
- **States**: lowercase (`wanted`, `defeated`)
- **When clauses**: snake_case (`take_damage`, `buy_item`)

### 10.2 Constraint Design

Define what **cannot** happen, not what can:

```tinytalk
// Good: Define the boundary
must balance is above 0
  otherwise "Cannot go negative"

// Less clear: React to violation
if balance is below 0
  set balance to 0
```

### 10.3 Transaction Scope

Keep `when` clauses focused:
- One responsibility per when
- Clear success/failure conditions
- Use `finfr` to commit changes

## 11. Implementation Notes

This specification describes tinyTalk 1.0 as implemented in C.

The current C implementation provides:
- Complete lexer for all keywords
- Basic parser for blueprint and when clause structure
- Runtime with ACID transaction support
- Standard Kit blueprints
- Execution bounds enforcement

Future enhancements may include:
- Advanced constraint evaluation
- Bytecode compilation
- Optimized execution
- Extended standard library

## 12. References

- **tinyTalk Bible**: Philosophy and architecture
- **Programming Guide**: Tutorials and examples
- **Newton Supercomputer**: Verification engine

---

**Version**: 1.0  
**Date**: January 2026  
**Author**: Newton Supercomputer / Jared Lewis Conglomerate
