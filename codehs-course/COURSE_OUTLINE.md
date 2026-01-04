# CodeHS Course: Newton & tinyTalk
## Course Outline (DRAFT)

*Teaching constraint-based programming and computer architecture*

---

## Course Philosophy

Teach computer science fundamentals through the lens of:
1. **tinyTalk** - A constraint-based language that reads like English
2. **Newton** - A verification engine that proves constraints are satisfied
3. **Logic Distance** - Understanding why some code is fast and some is slow

---

## Target Audience
- High school students (grades 9-12)
- Beginner to intermediate programming experience
- Interest in understanding "how computers really work"

---

## Unit 1: What Is A Computer, Really?

### Lesson 1.1: Electricity and Switches
- Computers are just switches (transistors)
- ON = 1, OFF = 0
- Everything else is abstraction

### Lesson 1.2: Logic Gates
- AND, OR, NOT - the building blocks
- How switches combine to make decisions
- Activity: Build a logic gate simulator

### Lesson 1.3: The Layer Cake
- Physics → Gates → CPU → Assembly → C → Python
- Each layer adds translation overhead
- Why "high-level" means "far from metal"

### Lesson 1.4: The Logic Distance Concept
- How many steps from your code to logic gates?
- Why some code runs fast and some runs slow
- Introduce the performance hierarchy

---

## Unit 2: Introduction to tinyTalk

### Lesson 2.1: Constraints vs. Commands
- Traditional programming: "Do this, then do that"
- Constraint programming: "Make sure this is true"
- Why constraints are more natural for rules

### Lesson 2.2: Your First tinyTalk Rule
```tinytalk
when button_clicked
  and user_logged_in
fin show_dashboard
```
- The `when...fin` structure
- Boolean conditions
- Trigger → Conditions → Result

### Lesson 2.3: The Three Constraint Types
- **Permission constraints** - Can this happen?
- **Validation constraints** - Is this data valid?
- **State constraints** - What changes?

### Lesson 2.4: Building a Simple App with tinyTalk
- Student project: Build a login gate
- Student project: Build a permission checker
- Student project: Build a game state machine

---

## Unit 3: Why Newton Is Fast

### Lesson 3.1: The Traditional Approach
```python
if user.is_verified:
    if not user.is_banned:
        if post.size < limit:
            # Finally do the thing
```
- Nested if statements
- Each check = function call = overhead

### Lesson 3.2: The Newton Approach
```tinytalk
when user_posts
  and verified
  and not_banned
  and size_ok
fin post_saved
```
- Compiles to single boolean expression
- CPU does AND/OR natively

### Lesson 3.3: Boolean Algebra in Hardware
- CPUs are literally logic gates
- AND/OR/NOT in 1 nanosecond
- Why pure boolean = pure speed

### Lesson 3.4: Measuring Performance
- Activity: Time traditional code vs. Newton
- See the difference in real numbers
- Understand: 23ms → 0.01ms for validation

---

## Unit 4: The Three Operations

### Lesson 4.1: Division - Proportional Checks
- "Has this reached X% of limit?"
- Example: Token usage, rate limiting
- When to use division

### Lesson 4.2: Subtraction - Difference Checks
- "How far from the boundary?"
- Example: Quota remaining, time left
- Faster than division

### Lesson 4.3: Multiply by Zero - Emergency Stop
- "Kill this immediately"
- Hardware-optimized instant termination
- The nuclear option

### Lesson 4.4: Choosing Your Operation
- Activity: Match scenarios to operations
- Performance implications
- Real-world applications

---

## Unit 5: Building Real Applications

### Lesson 5.1: API Rate Limiting
- Prevent abuse with constraints
- Graceful degradation
- tinyTalk implementation

### Lesson 5.2: User Permissions
- Role-based access control
- Hierarchical permissions
- Constraint-based security

### Lesson 5.3: Game Logic
- Turn-based game rules
- State machines
- Win conditions

### Lesson 5.4: Content Moderation
- Input validation
- Content filtering
- Automated enforcement

---

## Unit 6: Verification and Proofs

### Lesson 6.1: What Is Verification?
- Traditional auth: "Trust me, I'm allowed"
- Newton: "Here's mathematical proof I'm allowed"
- Why proofs matter

### Lesson 6.2: Cryptographic Proofs (Simplified)
- Hash functions (one-way)
- Signatures (proving identity)
- Merkle proofs (proving state)

### Lesson 6.3: The Newton Proof System
- How Newton generates proofs
- How anyone can verify them
- Zero-knowledge concepts (intro)

### Lesson 6.4: Building Verifiable Systems
- Trust but verify
- Audit logs
- Transparency

---

## Unit 7: Final Project

### Option A: Build a Social Media Backend
- User registration constraints
- Posting permissions
- Content validation
- Rate limiting

### Option B: Build a Game Engine
- Player actions
- Game rules
- Win/lose conditions
- Multiplayer sync

### Option C: Build a Smart Contract Simulator
- Token transfers
- Balance constraints
- Transaction validation

---

## Assessment Ideas

### Formative
- Code challenges in each lesson
- Logic gate quizzes
- Performance estimation exercises

### Summative
- Unit projects
- Final project presentation
- Written reflection on logic distance concept

---

## Resources Needed

### From Newton Repo
- tinyTalk documentation
- Example constraint files
- Performance benchmarks

### External
- Logic gate simulator (online tool)
- CPU visualization tools
- Performance profiling intro

---

## Notes for Development

### Key Differentiators from Other CS Courses
1. Start with "why" not "how"
2. Performance-first thinking
3. Constraint-based paradigm
4. Real-world verification concepts

### Potential Challenges
- Abstract concepts need concrete examples
- Performance measurement can be tricky
- Cryptography needs careful simplification

### Open Questions
- [ ] What CodeHS tools/features can we leverage?
- [ ] How do we sandbox Newton for student use?
- [ ] What's the right balance of theory vs. practice?
- [ ] Partner with CodeHS for custom environment?
