# TinyTalk Language Specification

## Overview
TinyTalk is a lightweight, high-level programming language designed for simplicity and readability. It is particularly suited for educational purposes, prototyping, and small-scale applications. TinyTalk emphasizes clarity and ease of use, making it accessible to beginners while still being powerful enough for advanced users.

---

## Language Features

### 1. **Blueprints**
Blueprints are used to define structured data types (similar to classes in other languages).

#### Syntax:
```tinytalk
blueprint BlueprintName
    field fieldName1
    field fieldName2
    ...
end
```

#### Example:
```tinytalk
blueprint Player
    field name
    field health
    field attack
    field defense
end
```

---

### 2. **Functions**
Functions are reusable blocks of code that can take arguments and return values.

#### Syntax:
```tinytalk
fn functionName(arg1, arg2, ...) {
    // Function body
    reply returnValue
}
```

#### Example:
```tinytalk
fn calculate_damage(attacker, defender) {
    let damage = attacker.attack - defender.defense
    reply damage > 0 ? damage : 0
}
```

---

### 3. **Variables**
Variables are used to store data. Use the `let` keyword to declare variables.

#### Syntax:
```tinytalk
let variableName = value
```

#### Example:
```tinytalk
let player1 = Player("Knight", 100, 20, 10)
```

---

### 4. **Control Structures**

#### **Conditionals**
Conditionals allow you to execute code based on conditions.

##### Syntax:
```tinytalk
if condition {
    // Code to execute if condition is true
} else {
    // Code to execute if condition is false
}
```

##### Example:
```tinytalk
if player1.health <= 0 {
    show(player1.name "has been defeated!")
} else {
    show(player1.name "is still standing!")
}
```

#### **Loops**
Loops allow you to repeat code while a condition is true.

##### Syntax:
```tinytalk
while condition {
    // Code to execute while condition is true
}
```

##### Example:
```tinytalk
while player1.health > 0 {
    show(player1.name "is fighting!")
}
```

---

### 5. **Operators**

#### **Arithmetic Operators**
- `+` : Addition
- `-` : Subtraction
- `*` : Multiplication
- `/` : Division

#### **Comparison Operators**
- `==` : Equal to
- `!=` : Not equal to
- `<` : Less than
- `>` : Greater than
- `<=` : Less than or equal to
- `>=` : Greater than or equal to

#### **Logical Operators**
- `and` : Logical AND
- `or` : Logical OR
- `not` : Logical NOT

---

### 6. **Built-in Functions**

#### **`show`**
Displays a message to the user.

##### Syntax:
```tinytalk
show(message)
```

##### Example:
```tinytalk
show("Hello, TinyTalk!")
```

#### **`reply`**
Returns a value from a function.

##### Syntax:
```tinytalk
reply value
```

##### Example:
```tinytalk
reply 42
```

---

### 7. **Comments**
Comments are used to annotate code and are ignored during execution.

#### Syntax:
```tinytalk
// This is a single-line comment
```

#### Example:
```tinytalk
// Initialize the player
let player1 = Player("Knight", 100, 20, 10)
```

---

### 8. **Error Handling**
TinyTalk does not currently support advanced error handling mechanisms. Ensure that your code is well-tested to avoid runtime errors.

---

## Example Program
```tinytalk
// Define a Player blueprint
blueprint Player
    field name
    field health
    field attack
    field defense
end

// Define a function to calculate damage
fn calculate_damage(attacker, defender) {
    let damage = attacker.attack - defender.defense
    reply damage > 0 ? damage : 0
}

// Define the main game loop
fn game_loop(player1, player2) {
    while player1.health > 0 and player2.health > 0 {
        show(player1.name "HP:" player1.health "|" player2.name "HP:" player2.health)
        
        // Player 1 attacks Player 2
        let damage = calculate_damage(player1, player2)
        player2.health = player2.health - damage
        show(player1.name "deals" damage "damage to" player2.name)
        if player2.health <= 0 {
            show(player2.name "has been defeated!")
            break
        }

        // Player 2 attacks Player 1
        damage = calculate_damage(player2, player1)
        player1.health = player1.health - damage
        show(player2.name "deals" damage "damage to" player1.name)
        if player1.health <= 0 {
            show(player1.name "has been defeated!")
            break
        }
    }
}

// Initialize players
let player1 = Player("Knight", 100, 20, 10)
let player2 = Player("Orc", 120, 15, 5)

// Start the game
show("The battle begins!")
game_loop(player1, player2)
```