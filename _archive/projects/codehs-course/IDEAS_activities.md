# Activity Ideas
## Hands-On Learning for Newton/tinyTalk Course

---

## Unit 1 Activities: What Is A Computer?

### Activity 1.1: Human Logic Gates
**Type:** Unplugged / Group Activity
**Time:** 20 minutes

Students form groups of 3:
- Two "input" students hold cards (0 or 1)
- One "gate" student performs the logic

Run through AND, OR, NOT with physical movement.

**Learning:** Logic gates are just decision-making rules.

---

### Activity 1.2: Layer Cake Telephone
**Type:** Game
**Time:** 15 minutes

Pass a simple instruction through 6 "layers":
1. Physics: Flash a light
2. Gates: "Light ON means GO"
3. CPU: "Execute GO"
4. Assembly: "MOV GO, READY"
5. C: "if (go) ready();"
6. Python: "make_it_ready()"

Time how long the message takes. Discuss overhead.

**Learning:** Each layer adds translation time.

---

### Activity 1.3: Performance Prediction
**Type:** Worksheet / Calculation
**Time:** 25 minutes

Given:
- Layer 1: 0.001ms
- Each additional layer: 10x slower

Calculate:
- How long for 3 layers?
- How long for 6 layers?
- What if we could skip 2 layers?

**Learning:** Exponential slowdown is real.

---

## Unit 2 Activities: tinyTalk Basics

### Activity 2.1: Translate to Constraints
**Type:** Exercise
**Time:** 30 minutes

Take real-world rules and convert to tinyTalk:

**Example 1:** "Students can only enter the library if they have their ID and the library is open"
```tinytalk
when enter_library
  and has_id
  and library_open
fin entry_allowed
```

**Example 2:** "You can withdraw money if you have enough balance and haven't exceeded daily limit"
```tinytalk
when withdraw_money
  and balance >= amount
  and daily_total < 500
fin withdrawal_ok
```

Students create 5 of their own.

**Learning:** Constraints map naturally to real rules.

---

### Activity 2.2: Debug the Constraint
**Type:** Debugging Challenge
**Time:** 20 minutes

Find what's wrong:

```tinytalk
# Bug 1: Always fails
when login
  and password_correct
  and not_password_correct
fin access_granted

# Bug 2: Never triggers
when button_click
  and button_enabled
  and button_disabled
fin show_menu

# Bug 3: Logic error
when purchase
  or has_money
  or in_stock
fin purchase_complete
```

**Learning:** Boolean logic matters!

---

### Activity 2.3: Build a Door Lock
**Type:** Mini-Project
**Time:** 45 minutes

Build a constraint system for a smart door:
- Must have correct PIN
- Must be during allowed hours
- Must not be in lockdown mode
- Bonus: Guest access codes

**Learning:** Real-world constraint application.

---

## Unit 3 Activities: Why Newton Is Fast

### Activity 3.1: Race Condition
**Type:** Live Coding Demo
**Time:** 20 minutes

Show side-by-side:
```python
# Traditional (slow)
def check_permission(user):
    if user.is_verified:
        if not user.is_banned:
            if user.role == "admin":
                return True
    return False
```

vs.

```python
# Newton-style (fast)
def check_permission(user):
    return (user.is_verified and
            not user.is_banned and
            user.role == "admin")
```

Run 1 million times. Compare times.

**Learning:** Boolean expressions are faster than nested conditionals.

---

### Activity 3.2: CPU Simulator
**Type:** Interactive Tool
**Time:** 30 minutes

Use an online CPU simulator to:
1. Count cycles for division operation
2. Count cycles for subtraction
3. Count cycles for AND operation

See the hardware difference.

**Learning:** CPUs are optimized for boolean logic.

---

### Activity 3.3: Performance Detective
**Type:** Investigation
**Time:** 40 minutes

Given slow code, students identify:
- How many function calls?
- How many conditionals?
- How many database queries?
- How to reduce logic distance?

**Learning:** Analyze real performance issues.

---

## Unit 4 Activities: The Three Operations

### Activity 4.1: Operation Matching
**Type:** Card Game
**Time:** 20 minutes

Cards with scenarios, students match to:
- **Division** (proportional check)
- **Subtraction** (difference check)
- **Multiply-zero** (kill switch)

Scenarios:
- "User at 80% of storage limit" → Division
- "User has 5 requests remaining" → Subtraction
- "Account terminated for fraud" → Multiply-zero
- "Token usage at 50%" → Division
- "2 hours until reset" → Subtraction

**Learning:** Choose the right tool for the job.

---

### Activity 4.2: Emergency Stop Design
**Type:** Design Challenge
**Time:** 30 minutes

Design multiply-by-zero scenarios for:
- A social media platform
- A banking app
- A game server
- A school management system

What conditions require instant termination?

**Learning:** Safety-critical thinking.

---

## Unit 5 Activities: Real Applications

### Activity 5.1: Rate Limiter
**Type:** Build Project
**Time:** 60 minutes

Build a rate limiter in tinyTalk:
- 100 requests per minute
- Graceful degradation at 80%
- Hard stop at 100%
- Reset every minute

Test with simulated traffic.

**Learning:** Real API protection.

---

### Activity 5.2: Game State Machine
**Type:** Build Project
**Time:** 90 minutes

Build tic-tac-toe rules:
```tinytalk
when place_mark
  and current_player_turn
  and cell_empty
  and game_not_over
fin mark_placed

when check_win
  and three_in_row
fin game_won
```

**Learning:** State machines with constraints.

---

## Unit 6 Activities: Verification

### Activity 6.1: Hash Detective
**Type:** Puzzle
**Time:** 25 minutes

Given hashes, students:
- Verify which inputs produce which hashes
- Try to reverse a hash (impossible!)
- Understand one-way functions

**Learning:** Cryptographic fundamentals.

---

### Activity 6.2: Proof Chain
**Type:** Group Activity
**Time:** 35 minutes

Each student is a "block":
- Receives previous hash
- Adds their transaction
- Computes new hash
- Passes to next student

One student tries to modify history. Class detects it.

**Learning:** Tamper-evident systems.

---

## Assessment Activities

### Quiz: Logic Distance
Multiple choice:
- Which is faster: nested if or boolean expression?
- How many layers between Python and logic gates?
- When should you use multiply-by-zero?

### Practical: Debug & Optimize
Given slow constraint code:
- Identify problems
- Rewrite for performance
- Measure improvement

### Project: Build Something Real
Choose from:
- API Gateway with rate limiting
- Game engine with rules
- Permission system with proofs

---

## Unplugged Activities (No Computer Needed)

### Boolean Simon Says
"Simon says stand up IF you're wearing blue AND you have brown hair"

### Constraint Charades
Act out constraint violations, others guess the rule

### Logic Gate Relay Race
Teams race to compute boolean expressions

### Permission Role Play
Students are users, admins, constraints. Act out access attempts.

---

## Extension Activities (Advanced Students)

### Activity: Write a Mini-Newton
Build a simple constraint evaluator in Python:
- Parse tinyTalk-like syntax
- Evaluate boolean expressions
- Return true/false

### Activity: Benchmark Real Code
Profile actual Newton vs. traditional approaches
- Use Python timeit
- Generate performance graphs
- Write analysis report

### Activity: Design New Operations
Beyond division, subtraction, multiply-zero:
- What other mathematical operations have performance implications?
- Design a new constraint type
- Justify the use case
