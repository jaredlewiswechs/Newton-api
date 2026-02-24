# TinyTalk for Dummies

**A friendly, no-jargon guide to the TinyTalk programming language.**

> TinyTalk is a small, expressive language inspired by Smalltalk — but way easier to pick up.
> It has two "flavors" of syntax (modern and classic), a killer data-pipeline feature called
> **step chains**, and reads almost like English in places.

---

## Table of Contents

1. [Your First Program](#1-your-first-program)
2. [Variables — Storing Stuff](#2-variables--storing-stuff)
3. [Data Types — What Stuff Can Be](#3-data-types--what-stuff-can-be)
4. [Math — Crunching Numbers](#4-math--crunching-numbers)
5. [Strings — Working with Text](#5-strings--working-with-text)
6. [Booleans & Comparisons — True or False?](#6-booleans--comparisons--true-or-false)
7. [Lists — Collections of Things](#7-lists--collections-of-things)
8. [Maps — Key-Value Pairs](#8-maps--key-value-pairs)
9. [If / Else — Making Decisions](#9-if--else--making-decisions)
10. [Loops — Doing Things Repeatedly](#10-loops--doing-things-repeatedly)
11. [Functions — Reusable Blocks of Code](#11-functions--reusable-blocks-of-code)
12. [Lambdas — Quick Throwaway Functions](#12-lambdas--quick-throwaway-functions)
13. [Step Chains — TinyTalk's Superpower](#13-step-chains--tinytalk-s-superpower)
14. [Natural Comparisons — Code That Reads Like English](#14-natural-comparisons--code-that-reads-like-english)
15. [Property Conversions — Dot Magic](#15-property-conversions--dot-magic)
16. [String Methods — Text Tricks](#16-string-methods--text-tricks)
17. [Match — Pattern Matching](#17-match--pattern-matching)
18. [Try / Catch — Handling Errors Gracefully](#18-try--catch--handling-errors-gracefully)
19. [Structs — Custom Data Shapes](#19-structs--custom-data-shapes)
20. [Blueprints — Objects with Behavior](#20-blueprints--objects-with-behavior)
21. [The Pipe Operator — Left-to-Right Flow](#21-the-pipe-operator--left-to-right-flow)
22. [Classic Style — The Smalltalk Flavor](#22-classic-style--the-smalltalk-flavor)
23. [Data I/O — Reading & Writing Files](#23-data-io--reading--writing-files)
24. [HTTP — Fetching Data from the Web](#24-http--fetching-data-from-the-web)
25. [Dates & Time — Working with Dates](#25-dates--time--working-with-dates)
26. [Built-in Functions — The Standard Toolkit](#26-built-in-functions--the-standard-toolkit)
27. [Running Your Code](#27-running-your-code)
28. [Quick Reference Cheat Sheet](#28-quick-reference-cheat-sheet)

---

## 1. Your First Program

```
show(Hello, World!)
```

That's it. One line. `show()` prints things to the screen with a newline at the end.

> **No quotes needed!** In TinyTalk, bare words inside function calls are
> automatically treated as strings. `show(Hello)` prints `Hello` — no `"` required.
> If a variable with that name exists, TinyTalk uses its value instead.

You can still use quotes when you want to — they work the same as in any other language:

```
show("Hello, World!")
```

You can print multiple things separated by commas or spaces:

```
show("My name is" "TinyTalk" "and I am" 1 "years old")
```

Output: `My name is TinyTalk and I am 1 years old`

Mix bare words and variables freely:

```
let name = "Alice"
show(Hello, name!)
```

Output: `Hello Alice!`

> **Tip:** `show()` automatically puts spaces between each argument.
> If you don't want a newline at the end, use `print()` instead.

---

## 2. Variables — Storing Stuff

### `let` — A variable you can change later

```
let name = "Alice"
let age = 25
show("Hi, I'm {name} and I'm {age}")
```

Output: `Hi, I'm Alice and I'm 25`

You can update `let` variables:

```
let score = 0
score = 10
score += 5      // score is now 15
score -= 3      // score is now 12
score *= 2      // score is now 24
```

### `const` — A variable that never changes

```
const MAX_LIVES = 3
MAX_LIVES = 5   // ERROR! Can't reassign a constant.
```

Use `const` for values you know should never be modified. TinyTalk will yell at you
(with an error) if you try to change one.

---

## 3. Data Types — What Stuff Can Be

TinyTalk has these built-in types:

| Type      | Examples                         | What it is                |
|-----------|----------------------------------|---------------------------|
| `int`     | `42`, `0`, `-7`                  | Whole numbers             |
| `float`   | `3.14`, `-0.5`, `1.0`           | Decimal numbers           |
| `string`  | `"hello"`, `"it's me"`          | Text                      |
| `boolean` | `true`, `false`                  | Yes or no                 |
| `null`    | `null`                           | Nothing / empty           |
| `list`    | `[1, 2, 3]`                     | Ordered collection        |
| `map`     | `{"name": "Alice", "age": 25}`  | Key-value pairs           |

### Special number formats

```
let hex = 0xFF       // 255 in hexadecimal
let oct = 0o77       // 63 in octal
let bin = 0b1010     // 10 in binary
```

---

## 4. Math — Crunching Numbers

```
show(2 + 3)       // 5       (addition)
show(10 - 4)      // 6       (subtraction)
show(3 * 7)       // 21      (multiplication)
show(10 / 3)      // 3.333…  (division — always gives a decimal)
show(10 // 3)     // 3       (floor division — whole number only)
show(10 % 3)      // 1       (remainder / modulo)
show(2 ** 10)     // 1024    (exponentiation — 2 to the 10th)
```

### Order of operations

TinyTalk follows standard math order: `**` first, then `* / // %`, then `+ -`.
Use parentheses to override:

```
show(2 + 3 * 4)     // 14   (multiplication first)
show((2 + 3) * 4)   // 20   (parentheses first)
```

### String math

```
show("ha" * 3)            // "hahaha"  (repeat a string)
show("hello" + " world")  // "hello world"  (join strings)
```

---

## 5. Strings — Working with Text

### Creating strings

```
let greeting = "Hello, World!"
```

### String interpolation (the cool way to build strings)

Instead of gluing strings together with `+`, just put expressions inside `{}`:

```
let name = "Alice"
let age = 25
show("My name is {name} and next year I'll be {age + 1}")
```

Output: `My name is Alice and next year I'll be 26`

You can put **any expression** inside `{}` — math, function calls, whatever:

```
show("5 squared is {5 * 5}")   // "5 squared is 25"
```

### Escape sequences

| Escape | Meaning         |
|--------|-----------------|
| `\n`   | New line        |
| `\t`   | Tab             |
| `\\`   | Literal `\`     |
| `\"`   | Literal `"`     |
| `\{`   | Literal `{`     |

---

## 6. Booleans & Comparisons — True or False?

### Standard comparisons

```
show(5 == 5)     // true
show(5 != 3)     // true
show(3 < 5)      // true
show(5 > 3)      // true
show(5 <= 5)     // true
show(3 >= 5)     // false
```

### Logical operators

```
show(true and false)   // false
show(true or false)    // true
show(not true)         // false
```

### What counts as "truthy"?

Everything is truthy **except**:
- `false`
- `null`
- `0` and `0.0`
- `""` (empty string)
- `[]` (empty list)
- `{}` (empty map)

---

## 7. Lists — Collections of Things

### Creating lists

```
let fruits = ["apple", "banana", "cherry"]
let numbers = [1, 2, 3, 4, 5]
let mixed = [1, "two", true, null]   // any types allowed!
```

### Accessing items

```
let colors = ["red", "green", "blue"]
show(colors[0])    // "red"     (first item — indexing starts at 0)
show(colors[1])    // "green"
show(colors[-1])   // "blue"    (negative = count from the end)
```

### Modifying lists

```
let items = [1, 2]
append(items, 3)   // items is now [1, 2, 3]
pop(items)         // removes and returns 3
```

### List length

```
show(len([10, 20, 30]))      // 3
show([10, 20, 30] .len)      // 3  (property style — same thing)
```

---

## 8. Maps — Key-Value Pairs

Maps are like dictionaries: every value has a name (key).

```
let person = {"name": "Alice", "age": 25, "likes": "coding"}

show(person["name"])   // "Alice"  (bracket access)
show(person.name)      // "Alice"  (dot access — cleaner!)
show(person.age)       // 25
```

### Useful map functions

```
let m = {"a": 1, "b": 2, "c": 3}
show(keys(m))      // [a, b, c]
show(values(m))    // [1, 2, 3]
```

---

## 9. If / Else — Making Decisions

### Basic if

```
let temp = 35

if temp > 30 {
    show("It's hot!")
}
```

### If / else

```
let age = 16

if age >= 18 {
    show("You can vote!")
} else {
    show("Not old enough yet.")
}
```

### If / elif / else

```
let score = 85

if score >= 90 {
    show("A")
} elif score >= 80 {
    show("B")
} elif score >= 70 {
    show("C")
} else {
    show("Keep trying!")
}
```

Output: `B`

### Ternary (inline if)

```
let x = 10
let label = x > 5 ? "big" : "small"
show(label)   // "big"
```

---

## 10. Loops — Doing Things Repeatedly

### For loop

```
for i in range(5) {
    show(i)
}
// Prints: 0, 1, 2, 3, 4 (each on its own line)
```

Loop over a list:

```
let fruits = ["apple", "banana", "cherry"]
for fruit in fruits {
    show("I like {fruit}")
}
```

### Range variations

```
range(5)         // [0, 1, 2, 3, 4]          — 0 up to (not including) 5
range(2, 6)      // [2, 3, 4, 5]              — start at 2, up to 6
range(0, 10, 2)  // [0, 2, 4, 6, 8]           — count by 2s
```

### While loop

```
let count = 0
while count < 5 {
    show(count)
    count += 1
}
```

### Break and continue

```
// break — stop the loop entirely
for i in range(10) {
    if i == 5 { break }
    show(i)
}
// Prints: 0, 1, 2, 3, 4

// continue — skip this iteration, move to the next
for i in range(5) {
    if i == 2 { continue }
    show(i)
}
// Prints: 0, 1, 3, 4
```

---

## 11. Functions — Reusable Blocks of Code

### Defining a function

```
fn greet(name) {
    show("Hello, {name}!")
}

greet("Alice")   // "Hello, Alice!"
greet("Bob")     // "Hello, Bob!"
```

### Returning values

```
fn square(x) {
    return x * x
}

show(square(5))    // 25
show(square(12))   // 144
```

### Multiple parameters

```
fn add(a, b) {
    return a + b
}

show(add(3, 4))   // 7
```

### Default parameter values

Parameters can have default values. If a caller doesn't provide an argument,
the default kicks in:

```
fn greet(name = "World") {
    show("Hello, {name}!")
}

greet()          // "Hello, World!"
greet("Alice")   // "Hello, Alice!"
```

You can mix required and optional parameters:

```
fn repeat_str(s, n = 3) {
    return s * n
}

show(repeat_str("ha"))      // "hahaha"
show(repeat_str("ho", 2))   // "hoho"
```

### Recursion (a function calling itself)

```
fn factorial(n) {
    if n <= 1 { return 1 }
    return n * factorial(n - 1)
}

show(factorial(5))   // 120   (5 * 4 * 3 * 2 * 1)
```

---

## 12. Lambdas — Quick Throwaway Functions

Sometimes you need a tiny function for just one thing. Lambdas are anonymous
(unnamed) functions:

```
let double = (x) => x * 2
show(double(5))    // 10

let add = (a, b) => a + b
show(add(3, 4))    // 7
```

### Multi-line lambdas

Need more than one line? Use curly braces:

```
let classify = (x) => {
    if x > 0 { return "positive" }
    if x < 0 { return "negative" }
    return "zero"
}

show(classify(5))    // "positive"
show(classify(-3))   // "negative"
```

The last expression in a block is returned automatically, so you can skip `return` for simple cases:

```
let calc = (x) => {
    let y = x + 10
    y * 2
}
show(calc(5))   // 30
```

Lambdas really shine when combined with step chains and higher-order functions:

```
let nums = [1, 2, 3, 4, 5]
show(nums _filter((x) => x > 3))     // [4, 5]
show(nums _map((x) => x * 10))       // [10, 20, 30, 40, 50]
```

---

## 13. Step Chains — TinyTalk's Superpower

This is the feature that makes TinyTalk special. Step chains let you transform
data by chaining operations with an underscore `_` prefix — like a conveyor belt
in a factory.

### The idea

Instead of writing nested function calls like this (hard to read):

```
take(reverse(sort(data)), 3)
```

You write it as a chain (reads left to right, like English):

```
data _sort _reverse _take(3)
```

**Read it as:** "Take data, sort it, reverse it, take the first 3."

### All step chain operations

#### Ordering

```
let nums = [5, 3, 8, 1, 9]

show(nums _sort)       // [1, 3, 5, 8, 9]    sort ascending
show(nums _reverse)    // [9, 1, 8, 3, 5]     reverse the order
```

#### Filtering

```
let data = [1, 2, 3, 4, 5, 6, 7, 8]

show(data _filter((x) => x > 5))            // [6, 7, 8]
show(data _filter((x) => x % 2 == 0))       // [2, 4, 6, 8]   (evens only)
```

#### Transforming

```
let prices = [10, 20, 30]

show(prices _map((p) => p * 1.1))    // [11.0, 22.0, 33.0]  (add 10% tax)
```

#### Slicing

```
let items = [1, 2, 3, 4, 5, 6, 7, 8]

show(items _take(3))     // [1, 2, 3]      first 3
show(items _drop(5))     // [6, 7, 8]      drop first 5
show(items _first)       // 1               just the first one
show(items _last)        // 8               just the last one
```

#### Aggregating (crunching a list down to one value)

```
let scores = [85, 92, 78, 95, 88]

show(scores _sum)     // 438
show(scores _avg)     // 87.6
show(scores _min)     // 78
show(scores _max)     // 95
show(scores _count)   // 5
```

#### Reducing (combining all items into one value)

```
// Sum with explicit initial value
show([1, 2, 3, 4, 5] _reduce((acc, x) => acc + x, 0))   // 15

// Product
show([1, 2, 3, 4, 5] _reduce((acc, x) => acc * x, 1))   // 120

// Without an initial value, uses the first item as the starting point
show([1, 2, 3, 4] _reduce((acc, x) => acc + x))          // 10

// String concatenation
show(["a", "b", "c"] _reduce((acc, x) => acc + x, ""))   // "abc"
```

`_reduce` is the general-purpose aggregation — `_sum`, `_min`, `_max`, `_avg` are just
shortcuts for common cases.

#### Deduplication

```
let dupes = [1, 2, 2, 3, 3, 3, 4]

show(dupes _unique)   // [1, 2, 3, 4]
```

#### Grouping

```
let nums = [1, 2, 3, 4, 5, 6]
let grouped = nums _group((x) => x % 2 == 0 ? "even" : "odd")
show(grouped)
// {"even": [2, 4, 6], "odd": [1, 3, 5]}
```

#### Restructuring

```
show([[1, 2], [3, 4], [5, 6]] _flatten)   // [1, 2, 3, 4, 5, 6]
show([1, 2, 3, 4, 5, 6] _chunk(2))        // [[1, 2], [3, 4], [5, 6]]
```

#### Zipping (pairing up two lists)

```
let names = ["Alice", "Bob", "Charlie"]
let ages = [25, 30, 35]
show(names _zip(ages))
// [[Alice, 25], [Bob, 30], [Charlie, 35]]
```

#### Custom sorting

```
let people = [{"name": "Charlie", "age": 20}, {"name": "Alice", "age": 30}]
let sorted = people _sortBy((p) => p["age"])
show(sorted[0]["name"])   // "Charlie"  (youngest first)
```

#### Joining two datasets

```
let users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
let scores = [{"id": 1, "score": 95}, {"id": 2, "score": 87}]

// Join on a common key — like a SQL JOIN
let joined = users _join(scores, (r) => r["id"])
show(joined)
// [{"id": 1, "name": "Alice", "score": 95}, {"id": 2, "name": "Bob", "score": 87}]
```

#### Transforming map values

```
// After _group, transform each group's values
let grouped = {"math": [90, 85, 92], "science": [88, 76, 95]}
let avgs = grouped _mapValues((scores) => scores _avg)
show(avgs)   // {"math": 89.0, "science": 86.33...}
```

#### Side effects with _each

```
// _each runs a function on every item but returns the original list
[1, 2, 3] _each((x) => show("Processing {x}"))
// Prints: Processing 1, Processing 2, Processing 3
// Returns: [1, 2, 3]
```

### Chaining it all together

The real magic is chaining multiple steps:

```
let data = [42, 17, 93, 5, 68, 31, 84, 12, 56, 29]

// "Give me the top 3 numbers, each multiplied by 10"
let result = data _filter((x) => x > 20) _sort _reverse _take(3) _map((x) => x * 10)
show(result)   // [930, 840, 680]
```

Read it step by step:
1. Start with `data`
2. `_filter((x) => x > 20)` — keep only numbers above 20
3. `_sort` — sort ascending
4. `_reverse` — flip to descending
5. `_take(3)` — grab the top 3
6. `_map((x) => x * 10)` — multiply each by 10

---

## 14. Natural Comparisons — Code That Reads Like English

TinyTalk has special comparison operators that read like plain English:

### `is` / `isnt` — equality

```
show(5 is 5)      // true
show(5 isnt 3)    // true
```

### `has` / `hasnt` — does a list contain something?

```
let fruits = ["apple", "banana", "cherry"]

show(fruits has "banana")     // true
show(fruits has "grape")      // false
show(fruits hasnt "grape")    // true
```

### `isin` — is something in a list? (reverse of `has`)

```
show("banana" isin fruits)   // true

// Same as: fruits has "banana"
// But reads differently — pick whichever feels more natural!
```

### `islike` — wildcard pattern matching

```
show("hello" islike "hel*")     // true   (* matches anything)
show("hello" islike "h?llo")    // true   (? matches one character)
show("hello" islike "world*")   // false
```

Wildcards:
- `*` — matches any number of characters (including zero)
- `?` — matches exactly one character

---

## 15. Property Conversions — Dot Magic

You can convert values between types using dot properties:

```
// Number → String
show(42 .str)          // "42"

// String → Number
show("42" .int)        // 42
show("3.14" .float)    // 3.14

// Anything → Boolean
show(0 .bool)          // false
show(1 .bool)          // true
show("" .bool)         // false
show("hi" .bool)       // true

// Get the type name
show(42 .type)         // "int"
show("hi" .type)       // "string"
show([1,2] .type)      // "list"

// Get the length
show("hello" .len)     // 5
show([1, 2, 3] .len)   // 3
```

---

## 16. String Methods — Text Tricks

Call these with dot notation on any string:

```
show("hello".upcase)      // "HELLO"
show("HELLO".downcase)    // "hello"
show("  hello  ".trim)    // "hello"
show("abc".reversed)      // "cba"
show("abc".chars)         // [a, b, c]
show("hello world".words) // [hello, world]
```

Or use the function-call style:

```
show(upcase("hello"))                         // "HELLO"
show(downcase("HELLO"))                       // "hello"
show(trim("  hello  "))                       // "hello"
show(replace("hello world", "world", "TinyTalk"))   // "hello TinyTalk"
show(split("a,b,c", ","))                     // [a, b, c]
show(join(["a", "b", "c"], "-"))              // "a-b-c"
show(startswith("hello", "hel"))              // true
show(endswith("hello", "llo"))                // true
```

---

## 17. Match — Pattern Matching

Match is like a super-powered `if/elif` that compares a value against patterns:

```
let day = 3

match day {
    1 => show("Monday"),
    2 => show("Tuesday"),
    3 => show("Wednesday"),
    _ => show("Some other day"),
}
```

Output: `Wednesday`

The `_` is a **wildcard** — it matches anything (like a default/catch-all).

### Match as an expression (returns a value)

```
fn describe(x) {
    let result = match x {
        1 => "one",
        2 => "two",
        3 => "three",
        _ => "many",
    }
    return result
}

show(describe(2))   // "two"
show(describe(99))  // "many"
```

---

## 18. Try / Catch — Handling Errors Gracefully

Sometimes things go wrong. Instead of crashing, you can catch errors:

```
try {
    let result = 10 / 0   // this will cause an error!
    show(result)
} catch(e) {
    show("Oops! Something went wrong: " + e)
}
```

### Throwing your own errors

```
fn divide(a, b) {
    if b == 0 {
        throw "Cannot divide by zero!"
    }
    return a / b
}

try {
    show(divide(10, 0))
} catch(e) {
    show("Error: " + e)
}
```

Output: `Error: Cannot divide by zero!`

---

## 19. Structs — Custom Data Shapes

Structs let you define your own data types with named fields:

```
struct Point {
    x: int,
    y: int,
}

let p = Point(3, 4)
show(p.x)   // 3
show(p.y)   // 4
```

Think of a struct as a template: "A Point always has an `x` and a `y`."

---

## 20. Blueprints — Objects with Behavior

Blueprints are like structs but with **methods** (functions attached to the data).
This is the classic Smalltalk-inspired feature.

```
blueprint Counter
    field value = 0

    forge inc()
        self.value = self.value + 1
        reply self.value
    end

    forge reset()
        self.value = 0
        reply self.value
    end
end

let c = Counter(0)
show(c.inc())     // 1
show(c.inc())     // 2
show(c.inc())     // 3
show(c.reset())   // 0
```

Key concepts:
- `field` declares data the object holds
- `forge` defines a method (a function that belongs to the object)
- `self` refers to the current object (like `this` in JavaScript)
- `reply` returns a value from a method

---

## 21. The Pipe Operator — Left-to-Right Flow

The pipe operator passes a value as the first argument to the next function.
TinyTalk supports two styles — pick whichever you prefer:

| Style | Syntax | Inspired by |
|-------|--------|-------------|
| `|>`  | Elixir / F# style | `5 |> double |> add_one` |
| `%>%` | R / tidyverse style | `5 %>% double %>% add_one` |

Both do exactly the same thing. You can even mix them:

```
fn double(x) { return x * 2 }
fn add_one(x) { return x + 1 }

// All three are equivalent:
show(5 |> double |> add_one)     // 11
show(5 %>% double %>% add_one)   // 11
show(5 |> double %>% add_one)    // 11  (mixing is fine!)
```

This is equivalent to `add_one(double(5))` but reads left-to-right.

**Pipe vs Step Chains — what's the difference?**
- **Pipe `|>` / `%>%`** works with regular named functions
- **Step chains `_sort`** are built-in list operations with the underscore prefix

Use whichever feels right for the situation!

---

## 22. Classic Style — The Smalltalk Flavor

TinyTalk supports two syntax styles. Everything above used the **modern** style.
Here's the **classic** style, inspired by Smalltalk:

### Constants with `when`

```
when PI = 3.14159
when MAX_SIZE = 100
```

Same as `const PI = 3.14159` in modern style.

### Functions with `law`

```
law circle_area(r)
    reply PI * r * r
end

show(circle_area(5))   // 78.53975
```

Same as:
```
fn circle_area(r) {
    return PI * r * r
}
```

### Functions with `forge`

```
forge greet(name)
    reply "Hello, " + name
end

show(greet("World"))   // "Hello, World"
```

### Functions with `when...do...fin`

```
when double(x)
    do x * 2
fin

show(double(7))   // 14
```

### Classes with `blueprint`

```
blueprint Dog
    field name = ""
    field energy = 100

    forge bark()
        self.energy = self.energy - 10
        reply "{self.name} says Woof! (energy: {self.energy})"
    end

    forge rest()
        self.energy = self.energy + 20
        reply "{self.name} rests. (energy: {self.energy})"
    end
end
```

### Mix and match!

Both styles work together. You can use `let` in one line and `law` in the next.
TinyTalk doesn't care — use whatever feels natural to you.

---

## 23. Data I/O — Reading & Writing Files

TinyTalk can read and write CSV and JSON files, making it a real data tool.

### CSV — Tabular Data

```
// Read a CSV file — each row becomes a map
let people = read_csv("people.csv")
// If the file has headers: name,age,score
// people is: [{"name": "Alice", "age": 25, "score": 95.5}, ...]

// Numbers and booleans are auto-detected!
show(people[0]["name"])    // "Alice"
show(people[0]["age"])     // 25   (int, not string)

// Process it with step chains
let top = people
    _filter((p) => p["score"] > 90)
    _sortBy((p) => p["score"])
    _reverse
show(top)

// Write results back to CSV
write_csv(top, "top_scorers.csv")
```

### JSON — Structured Data

```
// Read a JSON file
let config = read_json("config.json")
show(config["database"]["host"])

// Write any value as JSON
let data = {"users": 42, "active": true}
write_json(data, "stats.json")

// Parse a JSON string (no file needed)
let obj = parse_json('{"x": 1, "y": 2}')
show(obj["x"])   // 1

// Convert a value to a JSON string
let s = to_json([1, 2, 3])
show(s)   // "[1, 2, 3]"
```

---

## 24. HTTP — Fetching Data from the Web

Pull JSON data from any API with one function call:

```
// Fetch JSON from an API
let data = http_get("https://api.example.com/users")

// data is already parsed — use it immediately
for user in data {
    show("{user["name"]}: {user["email"]}")
}

// Combine with step chains for instant analysis
let active = http_get("https://api.example.com/users")
    _filter((u) => u["active"] is true)
    _sortBy((u) => u["name"])
show(active)
```

---

## 25. Dates & Time — Working with Dates

TinyTalk has built-in date functions for parsing, formatting, arithmetic, and bucketing.

### Getting the current time

```
show(date_now())   // "2024-03-15 14:30:00"
```

### Parsing dates

TinyTalk auto-detects common formats:

```
show(date_parse("2024-03-15"))              // "2024-03-15 00:00:00"
show(date_parse("2024-03-15T10:30:00"))     // "2024-03-15 10:30:00"
show(date_parse("03/15/2024"))              // "2024-03-15 00:00:00"
```

### Date arithmetic

```
// Add or subtract time
show(date_add("2024-03-15", 10, "days"))    // "2024-03-25 00:00:00"
show(date_add("2024-03-15", -1, "weeks"))   // "2024-03-08 00:00:00"
show(date_add("2024-03-15", 3, "hours"))    // "2024-03-15 03:00:00"

// Difference between dates
show(date_diff("2024-03-20", "2024-03-15", "days"))   // 5.0
```

### Truncating dates (for grouping by period)

```
show(date_floor("2024-03-15", "week"))    // "2024-03-11 00:00:00"  (Monday)
show(date_floor("2024-03-15", "month"))   // "2024-03-01 00:00:00"
show(date_floor("2024-03-15", "year"))    // "2024-01-01 00:00:00"
```

This is incredibly useful for time-series analysis:

```
// Group sales by week
let weekly = sales
    _map((s) => {
        let week = date_floor(s["date"], "week")
        return {"week": week, "amount": s["amount"]}
    })
    _group((s) => s["week"])
    _mapValues((rows) => rows _map((r) => r["amount"]) _sum)
```

### Formatting dates

```
show(date_format("2024-03-15", "%B %d, %Y"))   // "March 15, 2024"
show(date_format("2024-03-15", "%A"))           // "Friday"
```

---

## 26. Built-in Functions — The Standard Toolkit

### Output

| Function     | Description                           | Example                        |
|-------------|---------------------------------------|--------------------------------|
| `show(...)` | Print with newline                    | `show("hi")` → `hi`           |
| `print(...)` | Print without newline                | `print("hi")` → `hi`          |

### Math

| Function       | Description          | Example                            |
|---------------|----------------------|------------------------------------|
| `abs(n)`      | Absolute value        | `abs(-5)` → `5`                   |
| `round(n, d)` | Round to d places     | `round(3.456, 2)` → `3.46`        |
| `floor(n)`    | Round down            | `floor(3.7)` → `3`                |
| `ceil(n)`     | Round up              | `ceil(3.2)` → `4`                 |
| `sqrt(n)`     | Square root           | `sqrt(16)` → `4.0`                |
| `pow(b, e)`   | Power                 | `pow(2, 10)` → `1024`             |
| `min(...)`    | Minimum               | `min(3, 1, 2)` → `1`              |
| `max(...)`    | Maximum               | `max(3, 1, 2)` → `3`              |
| `sum(list)`   | Sum of list           | `sum([1,2,3])` → `6`              |

### Trigonometry

| Function   | Description      |
|-----------|------------------|
| `sin(x)`  | Sine (radians)   |
| `cos(x)`  | Cosine (radians) |
| `tan(x)`  | Tangent (radians)|
| `log(x)`  | Natural log      |
| `exp(x)`  | e^x              |

### Collections

| Function              | Description                     | Example                                  |
|----------------------|---------------------------------|------------------------------------------|
| `len(x)`             | Length                          | `len([1,2,3])` → `3`                    |
| `range(n)`           | Numbers 0 to n-1               | `range(4)` → `[0,1,2,3]`               |
| `range(a, b)`        | Numbers a to b-1                | `range(2,5)` → `[2,3,4]`               |
| `range(a, b, s)`     | Numbers a to b-1, step s        | `range(0,10,3)` → `[0,3,6,9]`          |
| `append(list, val)`  | Add to end (modifies list)      | `append([1,2], 3)` → `[1,2,3]`         |
| `push(list, val)`    | Same as append                  | —                                        |
| `pop(list)`          | Remove & return last            | `pop([1,2,3])` → `3`                   |
| `sort(list)`         | Sort ascending                  | `sort([3,1,2])` → `[1,2,3]`            |
| `reverse(x)`         | Reverse list or string          | `reverse([1,2,3])` → `[3,2,1]`         |
| `contains(x, val)`   | Check membership                | `contains([1,2], 2)` → `true`          |
| `slice(x, a, b)`     | Slice from a to b               | `slice([1,2,3,4], 1, 3)` → `[2,3]`    |
| `keys(map)`          | Get all keys                    | `keys({"a":1})` → `[a]`                |
| `values(map)`        | Get all values                  | `values({"a":1})` → `[1]`              |
| `zip(a, b)`          | Pair up elements                | `zip([1,2],[3,4])` → `[[1,3],[2,4]]`   |
| `enumerate(list)`    | Index-value pairs               | `enumerate(["a","b"])` → `[[0,a],[1,b]]`|

### Strings

| Function                  | Description              | Example                                     |
|--------------------------|--------------------------|---------------------------------------------|
| `split(s, delim)`        | Split string             | `split("a,b", ",")` → `[a, b]`             |
| `join(list, delim)`      | Join to string           | `join(["a","b"], "-")` → `"a-b"`           |
| `replace(s, old, new)`   | Replace substring        | `replace("hi all", "all", "you")` → `"hi you"` |
| `trim(s)`                | Strip whitespace         | `trim("  hi  ")` → `"hi"`                  |
| `upcase(s)`              | Uppercase                | `upcase("hi")` → `"HI"`                    |
| `downcase(s)`            | Lowercase                | `downcase("HI")` → `"hi"`                  |
| `startswith(s, prefix)`  | Check start              | `startswith("hello", "hel")` → `true`      |
| `endswith(s, suffix)`    | Check end                | `endswith("hello", "llo")` → `true`        |

### Type Conversions

| Function    | Description            | Example                        |
|------------|------------------------|--------------------------------|
| `str(x)`   | Convert to string      | `str(42)` → `"42"`            |
| `int(x)`   | Convert to integer     | `int("42")` → `42`            |
| `float(x)` | Convert to float       | `float("3.14")` → `3.14`      |
| `bool(x)`  | Convert to boolean     | `bool(0)` → `false`           |
| `type(x)`  | Get type name          | `type(42)` → `"int"`          |

### Testing / Assertions

| Function                     | Description                      |
|-----------------------------|----------------------------------|
| `assert(cond, msg)`         | Fail if condition is false       |
| `assert_equal(a, b, msg)`   | Fail if a ≠ b                    |
| `assert_true(val, msg)`     | Fail if val is not truthy        |
| `assert_false(val, msg)`    | Fail if val is not falsy         |

### File I/O

| Function                  | Description                           |
|--------------------------|---------------------------------------|
| `read_csv(path)`         | Read CSV → list of maps               |
| `write_csv(data, path)`  | Write list of maps → CSV              |
| `read_json(path)`        | Read JSON file → value                |
| `write_json(data, path)` | Write value → JSON file               |
| `parse_json(string)`     | Parse JSON string → value             |
| `to_json(value)`         | Value → JSON string                   |

### HTTP

| Function         | Description                              |
|-----------------|------------------------------------------|
| `http_get(url)` | GET URL → parsed JSON (or string)        |

### Dates

| Function                          | Description                    |
|----------------------------------|--------------------------------|
| `date_now()`                     | Current date-time string       |
| `date_parse(string)`            | Parse → normalized date string |
| `date_format(date, fmt)`        | Format with strftime codes     |
| `date_floor(date, unit)`        | Truncate to day/week/month/year|
| `date_add(date, amount, unit)`  | Add/subtract days/hours/etc.   |
| `date_diff(date1, date2, unit)` | Difference between two dates   |

### Built-in Constants

| Name    | Value            |
|---------|------------------|
| `PI`    | 3.14159265...    |
| `E`     | 2.71828182...    |
| `TAU`   | 6.28318530...    |
| `INF`   | Infinity         |
| `true`  | Boolean true     |
| `false` | Boolean false    |
| `null`  | Null / nothing   |

---

## 27. Running Your Code

### From the command line

Save your code in a `.tt` file (e.g., `hello.tt`) and run it:

```bash
# Run a file
tinytalk run hello.tt

# Start an interactive REPL (type code, see results live)
tinytalk repl

# Check syntax without running
tinytalk check hello.tt
```

### Via the API

TinyTalk includes a web API. Start the server:

```bash
python -m newTinyTalk.server
```

Then send code to it:

```bash
curl -X POST http://localhost:5000/api/run \
  -H "Content-Type: application/json" \
  -d '{"code": "show(\"Hello from the API!\")"}'
```

**API Endpoints:**

| Endpoint           | Method | Description            |
|-------------------|--------|------------------------|
| `/api/run`        | POST   | Execute TinyTalk code  |
| `/api/health`     | GET    | Check if server is up  |
| `/api/examples`   | GET    | Get example programs   |

### From Python

```python
from newTinyTalk import TinyTalkKernel

kernel = TinyTalkKernel()
result = kernel.run('show("Hello from Python!")')

print(result.output)    # "Hello from Python!"
print(result.success)   # True
```

---

## 28. Quick Reference Cheat Sheet

### Variables
```
let x = 10           // mutable
const y = 20         // immutable
when z = 30          // immutable (classic style)
```

### Functions
```
fn add(a, b) { return a + b }           // modern
fn greet(name = "World") { ... }        // default params
law add(a, b) reply a + b end           // classic
let add = (a, b) => a + b               // lambda (single expr)
let f = (x) => { let y = x + 1; y }    // lambda (multi-line)
```

### Control flow
```
if x > 0 { ... } elif x == 0 { ... } else { ... }
for i in range(10) { ... }
while cond { ... }
match x { 1 => "one", 2 => "two", _ => "other" }
```

### Step chains
```
data _sort _reverse _take(5)
data _filter((x) => x > 10) _map((x) => x * 2) _sum
data _unique _count
data _group((x) => x.category)
data _reduce((acc, x) => acc + x, 0)
data _sortBy((r) => r["score"])
left _join(right, (r) => r["id"])
grouped _mapValues((xs) => xs _avg)
data _each((x) => show(x))
```

### Data I/O
```
read_csv("data.csv")              // list of maps
write_csv(data, "out.csv")        // maps to CSV
read_json("data.json")            // any value
write_json(data, "out.json")      // value to JSON
http_get("https://api.example.com/data")
```

### Dates
```
date_now()
date_parse("2024-03-15")
date_add(date, 7, "days")
date_diff(date1, date2, "days")
date_floor(date, "week")
date_format(date, "%B %d, %Y")
```

### Natural comparisons
```
list has item          // contains?
item isin list         // member of?
str islike "pattern*"  // wildcard match?
a is b                 // equal?
a isnt b               // not equal?
```

### Properties
```
value .str   .int   .float   .bool   .type   .len
```

### String methods
```
"text".upcase   .downcase   .trim   .chars   .words   .reversed
```

### Pipe operators
```
value |> fn1 |> fn2       // Elixir-style pipe
value %>% fn1 %>% fn2     // R-style pipe (same thing)
```

### Bare-word strings
```
show(Hello, world!)        // No quotes needed — bare words become strings
print(Hello, world!)       // Same for print
show(Hello, name)          // If name is defined, its value is used
```

### Comments
```
// This is a comment
# This is also a comment
/* This is a
   multi-line comment */
```

---

## You Made It!

That's TinyTalk. A language that's small enough to learn in an afternoon but expressive
enough to write real programs. The key things that make it unique:

1. **Step chains** — Transform data like a pipeline, not a pile of nested calls
2. **Natural comparisons** — `has`, `isin`, `islike` read like English
3. **Two styles** — Use curly braces or `end` blocks, whatever feels right
4. **String interpolation** — Just put `{expressions}` in your strings
5. **Bare-word strings** — `print(Hello, world!)` just works, no quotes needed
6. **R-style pipes** — Use `%>%` alongside `|>` for data pipelines
7. **Default parameters** — `fn greet(name = "World")` — skip args you don't need
8. **Multi-line lambdas** — `(x) => { ... }` for complex anonymous functions
9. **Data I/O** — `read_csv`, `read_json`, `http_get` — ingest real data
10. **Date handling** — Parse, format, diff, floor — time-series ready
11. **Joins** — `_join`, `_sortBy`, `_mapValues` — real data wrangling

Now go build something cool. Happy coding!
