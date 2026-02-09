# tinyTalk for CodeHS: Course Specification

**Version**: 1.0
**Date**: January 6, 2026
**Author**: Newton Education Team
**Target Platform**: CodeHS
**Grade Level**: 9-12 (with AP track)

---

## Executive Summary

This specification outlines a full-year course teaching **constraint-first programming** through tinyTalk, designed for the CodeHS platform. The course inverts traditional programming pedagogy: instead of teaching students to write code that *does things*, we teach them to define *what cannot happen* first.

### Why This Matters

Traditional CS education:
- "Write code → hope it works → catch errors"
- Teaches debugging as an afterthought
- Students learn to fear edge cases

Constraint-first education (tinyTalk):
- "Define boundaries → prove safety → execute within bounds"
- Safety is foundational, not remedial
- Students learn to *think in constraints*

This aligns with where the industry is heading: formal verification, AI safety, regulatory compliance, and provably correct systems.

---

## Course Overview

### Course Title Options
1. **"Constraint-First Programming with tinyTalk"** (academic)
2. **"No-First: Programming with Boundaries"** (conceptual)
3. **"Verified Computing: From Games to Safety-Critical Systems"** (applied)
4. **"The Physics of Code"** (philosophical)

### Duration
- **Full Year**: 36 weeks (180 class periods @ 50 minutes)
- **Semester Option**: 18 weeks (condensed, Levels 1-4 only)
- **AP Supplement**: 9 weeks (for students who completed AP CSP/CSA)

### Prerequisites
- Algebra I (for ratio concepts)
- Basic computer literacy
- No prior programming required (course is self-contained)

---

## Complexity Level Mapping

Based on your framework, here's how the 8 levels map to the curriculum:

| Level | Name | Curriculum Position | Target Student |
|-------|------|---------------------|----------------|
| **1** | "Oh That's Easy" | Units 1-2 | All students, Q1 |
| **2** | "Getting Interesting" | Units 3-4 | All students, Q1-Q2 |
| **3** | "Wait, What?" | Units 5-6 | All students, Q2 |
| **4** | "Oh God Why" | Units 7-8 | All students, Q3 |
| **5** | "Is This Even Possible?" | Unit 9 | AP/Honors, Q3-Q4 |
| **6** | "This Shouldn't Be Possible" | Unit 10 | AP/Honors, Q4 |
| **7** | "Dear God" | Extension | Post-AP enrichment |
| **8** | "The Theoretical Limit" | Research | Independent study |

---

## Unit Structure

### Semester 1: Foundations (Levels 1-3)

---

#### Unit 1: The Philosophy of No-First (3 weeks)
**Level 1 · Complexity: "Oh That's Easy"**

##### Learning Objectives
By the end of this unit, students will be able to:
- Explain the difference between "Yes-First" and "No-First" thinking
- Identify real-world examples of constraint systems (traffic lights, ATMs, elevators)
- Write their first tinyTalk law using `when` and `finfr`
- Understand why constraints prevent bugs rather than catch them

##### Key Concepts
- **Presence vs. Branching**: `when` acknowledges what IS, not what might be
- **Finality**: `finfr` = forbidden forever (ontological death)
- **The Three Layers**: Governance, Executive, Application

##### Lessons

| # | Title | Duration | Type | Description |
|---|-------|----------|------|-------------|
| 1.1 | Why Bugs Exist | 50 min | Lecture + Demo | Show how traditional code fails; introduce the idea of prevention |
| 1.2 | Real-World Constraints | 50 min | Discussion | Explore ATMs, traffic lights, nuclear reactors as constraint systems |
| 1.3 | The Five Sacred Words | 50 min | Vocabulary | when, and, fin, finfr, ratio |
| 1.4 | Your First Law | 50 min | Hands-on | Write a simple `when(value < 0, finfr)` law |
| 1.5 | The Bank Account | 50 min | Lab | Build a no-overdraft bank account |
| 1.6 | Constraints in Games | 50 min | Creative | Design constraints for a simple game |
| 1.7 | Unit 1 Assessment | 50 min | Quiz + Project | Demonstrate understanding |

##### Sample Code Progression

**Day 1: What Goes Wrong**
```python
# Traditional approach - BREAKS
balance = 100
def withdraw(amount):
    global balance
    balance -= amount  # What if amount > balance?
    return balance

withdraw(150)  # balance = -50 (BAD!)
```

**Day 4: The tinyTalk Way**
```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class BankAccount(Blueprint):
    balance = field(float, default=100.0)

    @law
    def no_overdraft(self):
        when(self.balance < 0, finfr)

    @forge
    def withdraw(self, amount):
        self.balance -= amount

account = BankAccount()
account.withdraw(150)  # BLOCKED - law prevents execution
```

##### Assessment: Unit 1 Project
**"The Vending Machine"**
- Create a vending machine with constraints:
  - Cannot dispense if insufficient payment
  - Cannot dispense if item out of stock
  - Cannot accept negative payment
- Rubric: Laws defined (40%), Forges work (30%), Edge cases handled (30%)

---

#### Unit 2: Fields and State (3 weeks)
**Level 1-2 · Complexity: "Oh That's Easy" → "Getting Interesting"**

##### Learning Objectives
- Define typed fields with appropriate defaults
- Understand state as "what exists right now"
- Combine multiple fields in a Blueprint
- Use Matter types for type-safe values

##### Key Concepts
- **Fields as Presence**: State is not variable; it's "what is"
- **Type Safety**: Money is not Mass is not Distance
- **Defaults**: What the world looks like before anything happens

##### Lessons

| # | Title | Duration | Type |
|---|-------|----------|------|
| 2.1 | What is State? | 50 min | Conceptual |
| 2.2 | Primitive Fields | 50 min | Hands-on |
| 2.3 | Matter Types | 50 min | Lab |
| 2.4 | The Mars Climate Orbiter | 50 min | Case Study |
| 2.5 | Complex Fields (lists, dicts) | 50 min | Advanced |
| 2.6 | State Snapshots | 50 min | Lab |
| 2.7 | Unit 2 Assessment | 50 min | Quiz + Project |

##### Case Study: Mars Climate Orbiter
NASA lost a $125 million spacecraft because one team used metric units and another used imperial. tinyTalk's Matter types make this impossible:

```python
from tinytalk_py import Meters, Feet

# These are different types - cannot mix!
distance_metric = Meters(100)
distance_imperial = Feet(100)

# This would be a TYPE ERROR, not a runtime bug
# distance_total = distance_metric + distance_imperial  # BLOCKED
```

##### Assessment: Unit 2 Project
**"The Character Sheet"**
- Create an RPG character with:
  - Health (cannot exceed max, cannot go below 0)
  - Mana (same constraints)
  - Position (x, y within world bounds)
  - Inventory (list of items)
- Demonstrate type safety with Matter types

---

#### Unit 3: Laws in Depth (3 weeks)
**Level 2 · Complexity: "Getting Interesting"**

##### Learning Objectives
- Write laws with multiple conditions using `and`
- Use parentheses for logical grouping
- Distinguish between `fin` (soft closure) and `finfr` (hard stop)
- Design law hierarchies for complex systems

##### Key Concepts
- **Combinatorics**: Multiple conditions create "shapes" of reality
- **Precedence**: Parentheses define what gets evaluated first
- **Soft vs. Hard**: `fin` can be reopened; `finfr` is forever

##### Lessons

| # | Title | Duration | Type |
|---|-------|----------|------|
| 3.1 | The AND Operator | 50 min | Hands-on |
| 3.2 | Logical Grouping | 50 min | Lab |
| 3.3 | fin vs. finfr | 50 min | Conceptual |
| 3.4 | Multiple Laws | 50 min | Design |
| 3.5 | Law Composition | 50 min | Advanced |
| 3.6 | The Traffic Intersection | 50 min | Case Study |
| 3.7 | Unit 3 Assessment | 50 min | Quiz + Project |

##### Code Example: Composed Constraints

```python
class TransferFunds(Blueprint):
    sender_balance = field(float, default=1000.0)
    receiver_exists = field(bool, default=True)
    fraud_flagged = field(bool, default=False)
    amount = field(float, default=0.0)
    daily_limit = field(float, default=500.0)
    manager_approved = field(bool, default=False)
    domestic = field(bool, default=True)
    kyc_verified = field(bool, default=False)

    @law
    def transfer_constraints(self):
        # Basic requirements
        when(self.amount > self.sender_balance, finfr)
        when(not self.receiver_exists, finfr)
        when(self.fraud_flagged, finfr)

        # Composed constraints with OR
        when(
            self.amount >= self.daily_limit
            and not self.manager_approved,
            finfr
        )
        when(
            not self.domestic
            and not self.kyc_verified,
            finfr
        )
```

##### Assessment: Unit 3 Project
**"The Elevator System"**
- Design an elevator with:
  - Cannot move while doors are open
  - Cannot exceed weight capacity
  - Cannot go below floor 1 or above max floor
  - Fire mode overrides normal constraints
- Students must compose multiple laws that work together

---

#### Unit 4: Forges and Actions (3 weeks)
**Level 2 · Complexity: "Getting Interesting"**

##### Learning Objectives
- Write forges that mutate state safely
- Understand automatic rollback on law violation
- Return meaningful values from forges
- Chain forges for complex operations

##### Key Concepts
- **Projection**: Newton checks what WOULD happen before doing it
- **Rollback**: If a law would be violated, state reverts
- **The Forge Contract**: "I will change state, but only if allowed"

##### Lessons

| # | Title | Duration | Type |
|---|-------|----------|------|
| 4.1 | What is a Forge? | 50 min | Conceptual |
| 4.2 | Simple Forges | 50 min | Hands-on |
| 4.3 | Rollback Mechanics | 50 min | Deep Dive |
| 4.4 | Return Values | 50 min | Lab |
| 4.5 | Multi-Field Forges | 50 min | Advanced |
| 4.6 | Forge Chains | 50 min | Design |
| 4.7 | Unit 4 Assessment | 50 min | Quiz + Project |

##### Demonstrating Rollback

```python
class MultiField(Blueprint):
    a = field(int, default=10)
    b = field(int, default=20)

    @law
    def sum_limit(self):
        when(self.a + self.b > 50, finfr)

    @forge
    def update_both(self, da, db):
        self.a += da  # Changes a
        self.b += db  # Changes b
        # If sum > 50, BOTH changes roll back

mf = MultiField()
print(mf.a, mf.b)  # 10, 20

try:
    mf.update_both(30, 30)  # Would make sum = 90
except LawViolation:
    print(mf.a, mf.b)  # STILL 10, 20 - both rolled back
```

##### Assessment: Unit 4 Project
**"The Trading System"**
- Build a simple stock trading system:
  - Buy/sell forges
  - Portfolio balance constraints
  - Daily trading limits
  - Demonstrate rollback on failed trades

---

#### Unit 5: Recursive Constraints (4 weeks)
**Level 3 · Complexity: "Wait, What?"**

##### Learning Objectives
- Define constraints that reference other constraints
- Build constraint hierarchies for complex domains
- Understand constraint inheritance
- Model real-world approval workflows

##### Key Concepts
- **Constraint Chaining**: One law can depend on another
- **Hierarchy**: Child constraints inherit parent constraints
- **Domain Modeling**: Real systems have layers of rules

##### The Medical Procedure Example

```python
class MedicalProcedure(Blueprint):
    patient_consents = field(bool, default=False)
    doctor_licensed = field(bool, default=False)
    is_routine = field(bool, default=True)
    ethics_approved = field(bool, default=False)

    # Sub-requirements for ethics approval
    three_doctors_agree = field(bool, default=False)
    legal_reviewed = field(bool, default=False)
    risks_explained = field(bool, default=False)
    is_experimental = field(bool, default=False)
    fda_compassionate = field(bool, default=False)

    @law
    def basic_requirements(self):
        when(not self.patient_consents, finfr)
        when(not self.doctor_licensed, finfr)

    @law
    def ethics_requirement(self):
        # Non-routine procedures need ethics approval
        when(not self.is_routine and not self.ethics_approved, finfr)

    @law
    def ethics_sub_requirements(self):
        # What ethics approval requires
        if self.ethics_approved:
            when(not self.three_doctors_agree, finfr)
            when(not self.legal_reviewed, finfr)
            when(not self.risks_explained, finfr)

    @law
    def experimental_requirements(self):
        # Experimental needs FDA compassionate use
        when(self.is_experimental and not self.fda_compassionate, finfr)
```

##### Assessment: Unit 5 Project
**"The Approval Workflow"**
- Model a document approval system:
  - Multiple approval levels (manager, director, VP)
  - Each level has its own sub-requirements
  - Some approvals can be delegated
  - Emergency bypass with proper authorization

---

#### Unit 6: The Three Layers (3 weeks)
**Level 3 · Complexity: "Wait, What?"**

##### Learning Objectives
- Understand the Governance/Executive/Application model
- Separate concerns correctly across layers
- Design systems that prevent "prompt drift"
- Recognize when layers are being violated

##### The Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: APPLICATION (What you're building)                │
│  - BankingApp, GameEngine, MedicalSystem                    │
│  - Combines L0 and L1 into solutions                        │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: EXECUTIVE (How things move)                       │
│  - field() = State definitions                              │
│  - forge() = State mutations                                │
│  - The "engine" of the system                               │
├─────────────────────────────────────────────────────────────┤
│  LAYER 0: GOVERNANCE (What cannot happen)                   │
│  - law() = Constraints                                      │
│  - finfr = Forbidden states                                 │
│  - The "physics" of the system                              │
└─────────────────────────────────────────────────────────────┘
```

##### Why This Matters

Traditional code mixes everything:
```python
# BAD: Logic and constraints intertwined
def withdraw(amount):
    if amount > balance:  # Constraint mixed with logic
        return "Error"    # Error handling mixed in
    balance -= amount     # State change
    log(f"Withdrew {amount}")  # Side effect
    return balance        # Return value
```

tinyTalk separates:
```python
# GOOD: Layers are distinct
class Account(Blueprint):
    # L1: State
    balance = field(float, default=0.0)

    # L0: Governance (constraints)
    @law
    def no_overdraft(self):
        when(self.balance < 0, finfr)

    # L1: Executive (actions)
    @forge
    def withdraw(self, amount):
        self.balance -= amount
        return self.balance
```

##### Assessment: Unit 6 Project
**"Refactor a Legacy System"**
- Given a messy, single-file program
- Students must separate into three layers
- Demonstrate how constraints are clearer when isolated

---

### Semester 2: Advanced Topics (Levels 4-6)

---

#### Unit 7: Temporal Constraints (4 weeks)
**Level 4 · Complexity: "Oh God Why"**

##### Learning Objectives
- Define time-based constraints (before, after, within)
- Handle cooling-off periods and rate limiting
- Model sequences of events that must occur in order
- Understand the `finfr` variant for delayed finality

##### The Stock Trading Example

```python
class StockTrade(Blueprint):
    trade_initiated = field(bool, default=False)
    trade_time = field(float, default=0.0)  # Unix timestamp
    is_insider = field(bool, default=False)
    in_trading_window = field(bool, default=True)
    earnings_announcement_time = field(float, default=0.0)

    @law
    def insider_trading_prevention(self):
        # If insider, must not trade within 30 days of earnings
        if self.is_insider:
            days_before_earnings = (self.earnings_announcement_time - self.trade_time) / 86400
            when(days_before_earnings < 30, finfr)

    @law
    def trading_window(self):
        when(self.is_insider and not self.in_trading_window, finfr)

    @law
    def cooling_off(self):
        # T+2 settlement - trade settles after 2 days
        # This is enforced at settlement time, not trade time
        pass
```

##### Temporal Operators in CDL

| Operator | Meaning | Example |
|----------|---------|---------|
| `within` | Must occur within time window | `within(action, 30, "days")` |
| `after` | Must occur after event | `after(approval, submission)` |
| `before` | Must occur before deadline | `before(review, publication)` |

##### Assessment: Unit 7 Project
**"The Auction System"**
- Bidding only during auction window
- Minimum time between bids
- Extension rules if bid in final minutes
- Settlement delay after auction ends

---

#### Unit 8: Ratios and Dimensional Analysis (4 weeks)
**Level 4 · Complexity: "Oh God Why"**

##### Learning Objectives
- Understand f/g ratio constraints
- Handle undefined ratios (division by zero as `finfr`)
- Model leverage, rates, and proportions
- Apply dimensional analysis to prevent unit confusion

##### The f/g Philosophy

Every constraint is a ratio:
- **f** = forge/fact/function (what you're trying to do)
- **g** = ground/goal/governance (what reality allows)
- **f/g > threshold** → violation
- **f/g undefined (g=0)** → ontological death

##### Code Example: Leverage Limit

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr, ratio

class LeverageGovernor(Blueprint):
    debt = field(float, default=0.0)
    equity = field(float, default=1000.0)

    @law
    def max_leverage(self):
        """Debt-to-equity cannot exceed 3:1"""
        when(ratio(self.debt, self.equity) > 3.0, finfr)

    @law
    def no_zero_equity(self):
        """Cannot have zero equity (undefined leverage)"""
        when(self.equity <= 0, finfr)

    @forge
    def borrow(self, amount):
        self.debt += amount
        return f"Total debt: {self.debt}"

gov = LeverageGovernor(equity=1000)
gov.borrow(2000)   # OK (leverage = 2.0)
gov.borrow(1500)   # BLOCKED (would be 3.5)
```

##### Real-World Ratio Examples

| Domain | Constraint | f | g | Max Ratio |
|--------|------------|---|---|-----------|
| Banking | Overdraft | withdrawal | balance | ≤ 1.0 |
| Finance | Leverage | debt | equity | ≤ 3.0 |
| Healthcare | Drug dosage | dose | body_weight | ≤ 0.01 |
| Education | Class size | students | capacity | ≤ 1.0 |
| Manufacturing | Defect rate | defects | total | < 0.01 |
| Flicker safety | Hz | flashes | seconds | < 3.0 |

##### Assessment: Unit 8 Project
**"The Risk Dashboard"**
- Build a financial dashboard showing multiple ratios
- Real-time constraint checking
- Visual indicators (green/yellow/red) based on ratio proximity to limits
- Historical tracking of ratio changes

---

#### Unit 9: Multi-Party Constraints (4 weeks)
**Level 5 · Complexity: "Is This Even Possible?"**

*AP/Honors Track*

##### Learning Objectives
- Model constraints across independent actors
- Handle quorum requirements
- Implement voting and consensus mechanisms
- Understand Byzantine fault tolerance at a conceptual level

##### The Merger Approval Example

```python
class MergerApproval(Blueprint):
    # Board votes
    company_a_board_approved = field(bool, default=False)
    company_b_board_approved = field(bool, default=False)
    company_a_quorum = field(bool, default=False)
    company_b_quorum = field(bool, default=False)

    # Shareholder votes
    a_shares_yes_percent = field(float, default=0.0)
    b_shares_yes_percent = field(float, default=0.0)
    vote_deadline = field(float, default=0.0)
    current_time = field(float, default=0.0)

    # Regulatory
    ftc_approved = field(bool, default=False)
    sec_filed = field(bool, default=False)

    @law
    def board_requirements(self):
        when(not self.company_a_quorum and self.company_a_board_approved, finfr)
        when(not self.company_b_quorum and self.company_b_board_approved, finfr)

    @law
    def shareholder_requirements(self):
        when(self.a_shares_yes_percent < 50.0, finfr)
        when(self.b_shares_yes_percent < 50.0, finfr)

    @law
    def vote_timing(self):
        days_since_start = (self.current_time - self.vote_start) / 86400
        when(days_since_start > 60, fin)  # Soft close - can extend

    @law
    def regulatory_requirements(self):
        when(not self.ftc_approved, finfr)
        when(not self.sec_filed, finfr)

    @forge
    def complete_merger(self):
        return "Merger completed - all constraints satisfied"
```

##### Consensus Concepts

| Term | Meaning | tinyTalk Application |
|------|---------|---------------------|
| **Quorum** | Minimum participants needed | `when(voters < quorum, finfr)` |
| **Supermajority** | More than simple majority | `when(yes_votes < total * 0.66, finfr)` |
| **Byzantine Tolerance** | Survives f faulty actors | `quorum = 2f + 1` |

##### Assessment: Unit 9 Project
**"The DAO Voting System"**
- Token-weighted voting
- Proposal lifecycle (draft → voting → execution)
- Quorum requirements
- Timelock on execution

---

#### Unit 10: Meta-Constraints (4 weeks)
**Level 6 · Complexity: "This Shouldn't Be Possible"**

*AP/Honors Track*

##### Learning Objectives
- Define constraints that modify other constraints
- Handle emergency overrides properly
- Model constitutional vs. statutory rules
- Understand the difference between immutable and mutable constraints

##### The Emergency Override Example

```python
class EmergencySystem(Blueprint):
    # Normal operation
    normal_approval_chain = field(list, default=None)
    current_approvers = field(list, default=None)

    # Emergency state
    emergency_active = field(bool, default=False)
    emergency_authorized_by = field(str, default="")
    emergency_start_time = field(float, default=0.0)

    # Meta-constraints
    emergency_max_duration = field(float, default=86400)  # 24 hours

    @law
    def emergency_authorization(self):
        """Emergency can only be declared by specific roles"""
        valid_authorities = ["president", "cto", "security_officer"]
        if self.emergency_active:
            when(self.emergency_authorized_by not in valid_authorities, finfr)

    @law
    def emergency_duration(self):
        """Emergency cannot last forever"""
        if self.emergency_active:
            elapsed = time.time() - self.emergency_start_time
            when(elapsed > self.emergency_max_duration, fin)

    @law
    def normal_approval(self):
        """Normal operation requires full approval chain"""
        if not self.emergency_active:
            when(self.current_approvers != self.normal_approval_chain, finfr)

    @law
    def emergency_approval(self):
        """Emergency mode uses simplified approval"""
        if self.emergency_active:
            # Only need 2 approvers instead of full chain
            when(len(self.current_approvers or []) < 2, finfr)
```

##### The Constitutional Hierarchy

```
┌────────────────────────────────────────────────────────────────┐
│  CONSTITUTIONAL CONSTRAINTS (Cannot be modified)               │
│  - No system can authorize its own destruction                 │
│  - Audit logs cannot be deleted                                │
│  - Emergency mode has maximum duration                         │
├────────────────────────────────────────────────────────────────┤
│  STATUTORY CONSTRAINTS (Can be modified through process)       │
│  - Approval chain requirements                                 │
│  - Daily limits                                                │
│  - Access levels                                               │
├────────────────────────────────────────────────────────────────┤
│  OPERATIONAL CONSTRAINTS (Can be modified dynamically)         │
│  - Current mode (normal/emergency)                             │
│  - Active sessions                                             │
│  - Temporary overrides                                         │
└────────────────────────────────────────────────────────────────┘
```

##### Assessment: Unit 10 Project
**"The Governance Framework"**
- Model a system with three levels of constraints
- Implement proper amendment process for statutory rules
- Emergency mode that respects constitutional bounds
- Audit trail of all constraint changes

---

### Extensions (Levels 7-8)

---

#### Extension A: Probabilistic Constraints
**Level 7 · Complexity: "Dear God"**

*Post-AP Enrichment*

For students who have completed the main curriculum:

```python
class CreditApproval(Blueprint):
    income_verified = field(bool, default=False)
    credit_score = field(int, default=650)
    debt_to_income = field(float, default=0.0)
    fraud_risk_score = field(float, default=0.0)  # 0-1 probability

    @law
    def basic_requirements(self):
        when(not self.income_verified, finfr)
        when(self.credit_score < 620, finfr)
        when(self.debt_to_income > 0.43, finfr)

    @law
    def fraud_threshold(self):
        """Probabilistic constraint - 15% max fraud risk"""
        when(self.fraud_risk_score > 0.15, finfr)
```

---

#### Extension B: Constraint Synthesis
**Level 8 · Complexity: "The Theoretical Limit"**

*Independent Study / Research*

The theoretical frontier: AI-generated constraints from natural language.

**Research Questions for Students:**
1. Can we verify constraints faster than we can execute them?
2. What happens when constraints conflict?
3. Can constraints be "learned" from examples?
4. What's the complexity class of constraint satisfaction in tinyTalk?

---

## Pedagogical Framework

### PRIMM Methodology Integration

CodeHS uses PRIMM (Predict, Run, Investigate, Modify, Make). Here's how it maps to tinyTalk:

| Phase | Traditional | tinyTalk Adaptation |
|-------|-------------|---------------------|
| **Predict** | "What will this code output?" | "Will this action be allowed?" |
| **Run** | Execute and observe | Execute and observe constraint checks |
| **Investigate** | Trace through logic | Trace which laws pass/fail |
| **Modify** | Change behavior | Add/modify constraints |
| **Make** | Create new program | Design constraint system from scratch |

### Constraint-First Thinking Exercises

Each unit includes "Constraint Thinking" exercises:

1. **Given**: A real-world scenario (e.g., "movie theater")
2. **Task**: List everything that CANNOT happen
3. **Convert**: Turn the list into tinyTalk laws
4. **Verify**: Try to break your own system

Example:
```
Scenario: Movie Theater Seating

Cannot Happen:
- Sell more tickets than seats
- Sell same seat twice
- Admit minor to R-rated film without adult
- Start movie before scheduled time

tinyTalk:
@law
def capacity(self):
    when(self.tickets_sold > self.total_seats, finfr)

@law
def no_double_booking(self):
    when(len(self.booked_seats) != len(set(self.booked_seats)), finfr)

# etc.
```

### Error Message Philosophy

Traditional error messages: "Error: Cannot withdraw more than balance"

tinyTalk error messages: "Law 'no_overdraft' prevents this state: balance would be -50"

This teaches students that errors aren't failures—they're the system working correctly.

---

## Assessment Framework

### Formative Assessments

- **Law Audits**: Given a Blueprint, identify missing constraints
- **Forge Reviews**: Given a forge, predict if it will succeed
- **Constraint Debugging**: Given a system that blocks valid actions, find the over-constraint

### Summative Assessments

Each unit ends with:
1. **Written Quiz** (20%): Vocabulary, concepts, trace exercises
2. **Coding Challenge** (40%): Build a constrained system from requirements
3. **Design Document** (40%): Describe constraints for a new domain

### Capstone Projects

**Semester 1 Capstone**: "Safe Game Engine"
- Build a game with comprehensive constraints
- Health can't go below 0 or above max
- No impossible movements
- Fair randomness (no guaranteed wins/losses)

**Semester 2 Capstone**: "Verified System"
- Choose a real-world domain (banking, healthcare, education)
- Model with multi-party constraints
- Include temporal and ratio constraints
- Present as a "safety case"

### AP Alignment

For students pursuing AP CSP credit:

| AP CSP Big Idea | tinyTalk Connection |
|-----------------|---------------------|
| **Creative Development** | Designing constraint systems |
| **Data** | Matter types, type safety |
| **Algorithms** | Constraint satisfaction algorithms |
| **Programming** | Blueprint/Law/Forge pattern |
| **Computer Systems** | Three-layer architecture |
| **Impact of Computing** | Safety-critical systems |

---

## Technical Requirements

### CodeHS Platform Integration

**Language**: Python (tinyTalk Python bindings)

**Required Libraries**:
```python
from tinytalk_py import (
    Blueprint, field, law, forge,
    when, and_, fin, finfr,
    ratio, RatioResult,
    Money, Mass, Distance, Temperature,
    KineticEngine, Presence, Delta
)
```

**Sandbox Configuration**:
- Python 3.10+
- tinytalk_py package installed
- No network access needed (all local)

### Autograder Integration

tinyTalk programs are highly testable because:
1. Laws are deterministic
2. Forges have predictable outcomes
3. State is explicit

Example autograder test:
```python
def test_student_bank_account():
    # Create their account
    account = StudentBankAccount(balance=100)

    # Test valid withdrawal
    account.withdraw(50)
    assert account.balance == 50

    # Test law enforcement
    with pytest.raises(LawViolation):
        account.withdraw(100)  # Would overdraft

    assert account.balance == 50  # Unchanged after violation
```

---

## Teacher Resources

### Professional Development Path

1. **Module 1**: Understanding constraint-first thinking
2. **Module 2**: Teaching tinyTalk syntax and semantics
3. **Module 3**: Designing effective constraint exercises
4. **Module 4**: Grading constraint systems
5. **Module 5**: Connecting to industry (formal verification, AI safety)

### Common Student Misconceptions

| Misconception | Reality | How to Address |
|---------------|---------|----------------|
| "Laws are if statements" | Laws define impossible states, not branches | Show that laws never "choose" between options |
| "finfr means error" | finfr means prevention | The system WORKING is blocking bad states |
| "I need to check constraints in my forge" | Laws are checked automatically | Show that the same law works across all forges |
| "More constraints = slower" | Newton is optimized for constraints | Show benchmarks |

### Differentiation Strategies

**For Struggling Students**:
- Focus on Level 1-2 examples
- Use visual constraint diagrams
- Pair with traditional if/else comparisons

**For Advanced Students**:
- Jump to Level 5-6 content
- Independent research on Level 7-8
- Contribute to open-source Newton projects

---

## Implementation Timeline

### Year 1 Pilot
- Q1: Train 10 pilot teachers
- Q2: Teach Semester 1 content
- Q3: Teach Semester 2 content
- Q4: Gather feedback, iterate

### Year 2 Expansion
- Summer: Update curriculum based on feedback
- Fall: Expand to 50 schools
- Spring: First AP-aligned cohort

### Year 3 Scale
- National CodeHS availability
- AP Board review for official endorsement
- University partnerships for dual enrollment

---

## Appendix A: Standards Alignment

### CSTA K-12 CS Standards

| Standard | Unit Coverage |
|----------|---------------|
| 2-AP-10 | Units 1-4 (algorithms) |
| 2-AP-13 | Units 5-6 (decomposition) |
| 2-AP-16 | Units 3-4 (debugging via constraints) |
| 2-AP-17 | Units 5-6 (documentation) |
| 3A-AP-17 | Units 7-10 (complex systems) |
| 3A-AP-18 | Capstones (design documentation) |

### TEKS Alignment (Texas)

| TEKS | Unit Coverage |
|------|---------------|
| 126.33(c)(4) | Units 1-2 (data types) |
| 126.33(c)(5) | Units 3-4 (control structures via laws) |
| 126.33(c)(6) | Units 5-6 (modularity) |
| 126.33(c)(7) | Units 7-10 (object-oriented) |

---

## Appendix B: Sample Week Plan

### Week 5 (Unit 2, Week 2): Matter Types

| Day | Topic | Activities | Homework |
|-----|-------|------------|----------|
| Mon | Intro to Matter | Lecture: Why types matter, Mars Orbiter video | Read: Matter section of guide |
| Tue | Basic Matter Types | Lab: Create Money, Mass, Distance values | Exercises 2.3.1-5 |
| Wed | Type Safety | Demo: What happens when you mix types | Predict: 5 type error scenarios |
| Thu | Temperature Special Case | Lab: Build thermostat with Celsius/Fahrenheit | Exercises 2.3.6-10 |
| Fri | Review & Quiz | Quiz + Partner debugging challenge | Start Unit 2 Project |

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| **Blueprint** | A template defining fields, laws, and forges |
| **CDL** | Constraint Definition Language |
| **Field** | A typed piece of state |
| **fin** | Soft closure (can be reopened) |
| **finfr** | Hard stop, forbidden forever |
| **Forge** | An action that mutates state |
| **Law** | A constraint defining impossible states |
| **Matter** | Type-safe value with units |
| **Presence** | A snapshot of state |
| **Ratio** | f/g relationship between values |
| **when** | Declaration of a fact |

---

## Contact & Support

- **Curriculum Questions**: education@newton-compute.com
- **Technical Support**: support@codehs.com
- **Research Partnerships**: research@newton-compute.com

---

*"The constraint IS the instruction. The verification IS the computation."*

**finfr.**
