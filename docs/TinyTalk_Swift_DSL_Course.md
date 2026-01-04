# TinyTalk Swift DSL: The Constraint-First Guide to iOS Development

**A Complete Course on Building Verified Applications**

---

**Author:** Jared Nashon Lewis
**Organization:** Jared Lewis Conglomerate
**Brands:** Newton · tinyTalk · Ada Computing Company · parcRI
**Copyright:** © 2026 Jared Lewis Conglomerate. All rights reserved.
**License:** Educational Use with Attribution

---

## Course Overview

This course teaches you a fundamentally different way to build iOS, macOS, watchOS, and visionOS applications. Instead of checking every possible invalid state, you'll learn to define what **can** exist—and let the system handle the rest.

### What You'll Learn

1. **The Combos Pattern** - Think in combinations, not permutations
2. **The TinyTalk Lexicon** - `fin`, `finfr`, `when`, `ratio`
3. **Blueprint/Law/Forge Architecture** - Constraint-governed types
4. **SwiftUI Integration** - Verified views and components
5. **Real-World Applications** - From bank accounts to lesson plans

### Prerequisites

- Basic Swift knowledge
- Familiarity with SwiftUI
- Xcode 15+ or Swift Playgrounds

### Time Estimate

- **Quick Start:** 1 hour
- **Full Course:** 4-6 hours
- **Mastery with Projects:** 2 weeks

---

## Part I: The Philosophy

### Chapter 1: Combos, Not Permutations

#### The Problem with Traditional Code

Consider a simple banking function:

```swift
// Traditional approach: checking permutations
func withdraw(amount: Double, from account: Account) -> Result<Double, Error> {
    if amount <= 0 {
        return .failure(InvalidAmount())
    }
    if account.frozen {
        return .failure(AccountFrozen())
    }
    if amount > account.balance {
        return .failure(InsufficientFunds())
    }
    if amount > account.dailyLimit {
        return .failure(ExceedsDailyLimit())
    }
    if account.requiresApproval && !account.approved {
        return .failure(NeedsApproval())
    }
    // ... more conditions

    // Finally, do the thing
    account.balance -= amount
    return .success(amount)
}
```

This code checks **permutations of invalid states**. Each new business rule adds another layer of nesting. With 5 conditions, you have 2^5 = 32 possible paths through the code.

#### The TinyTalk Approach

```swift
// TinyTalk approach: defining valid combinations
let withdrawalCombo = Combo<WithdrawalRequest, Transaction>(
    "withdrawal",
    when: [
        { $0.amount > 0 },
        { !$0.account.frozen },
        { ratio($0.amount, $0.account.balance) <= 1.0 },
        { ratio($0.amount, $0.account.dailyLimit) <= 1.0 },
        { !$0.account.requiresApproval || $0.account.approved }
    ]
) { request in
    Transaction(amount: request.amount, type: .withdrawal)
}

// Usage
switch withdrawalCombo.execute(request) {
case .success(let transaction):
    // It worked
case .failure(let finfr):
    // State cannot exist
}
```

This code defines a **combination of valid states**. Either all conditions are true and the operation succeeds, or it fails. No nesting. No exponential growth.

#### The Core Insight

> **Permutations** enumerate what **cannot** exist.
> **Combos** define what **can** exist.

When you check permutations, you're playing defense against every possible invalid state. When you define combos, you're stating the positive case: "This is what a valid withdrawal looks like."

### Chapter 2: The f/g Ratio

The most powerful primitive in TinyTalk is the **ratio**:

```
f/g = finfr

where:
  f = forge/fact/function (what you're trying to do)
  g = ground/goal/governance (what reality allows)
```

#### When Ratios Work

```swift
let withdrawal = 500.0
let balance = 1000.0

let r = ratio(withdrawal, balance)  // 0.5
if r <= 1.0 {
    // Withdrawal is within bounds
}
```

#### When Ratios Fail (finfr)

```swift
let withdrawal = 1500.0
let balance = 1000.0

let r = ratio(withdrawal, balance)  // 1.5
if r > 1.0 {
    // finfr: attempting more than reality allows
}
```

#### When Ratios Are Undefined (Ontological Death)

```swift
let withdrawal = 500.0
let balance = 0.0

let r = ratio(withdrawal, balance)  // undefined (division by zero)
if r.isUndefined {
    // finfr: the operation cannot exist
}
```

The ratio captures a fundamental truth about computation: **you cannot do more than reality allows**. When the denominator is zero, the operation is ontologically impossible.

---

## Part II: The Lexicon

### Chapter 3: The Four Primitives

TinyTalk has four core primitives. Learn these, and you understand the entire language.

#### 1. `fin` - Closure

`fin` means "finished" or "closed." It's a pause point that can be reopened.

```swift
// A task is fin when completed
when(task.isComplete, fin("Task completed"))

// A session is fin when ended
when(session.duration > maxDuration, fin("Session ended"))
```

Use `fin` for:
- Normal termination conditions
- Pause points in workflows
- Temporary stops

#### 2. `finfr` - Finality

`finfr` means "finality" or "ontological death." The state **cannot exist**.

```swift
// Balance cannot be negative
when(balance < 0, finfr("Balance cannot be negative"))

// Division by zero is impossible
when(denominator == 0, finfr("Cannot divide by zero"))
```

Use `finfr` for:
- Impossible states
- Constraint violations
- Security boundaries

#### 3. `when` - State Declaration

`when` declares a fact about the current state.

```swift
// If condition is true and result is finfr, throws
try when(liabilities > assets, finfr("Insolvent"))

// Returns the condition for chaining
if when(user.isAdmin) {
    // Admin actions
}
```

#### 4. `ratio` - Dimensional Analysis

`ratio` computes the f/g relationship.

```swift
let r = ratio(withdrawal, balance)

// Check bounds
if r <= 1.0 { /* within limits */ }
if r > 1.0 { /* exceeds limits */ }
if r.isUndefined { /* impossible */ }
```

### Chapter 4: Using the Lexicon

#### Pattern 1: Guard with finfr

```swift
func processPayment(amount: Double, available: Double) throws -> Payment {
    try when(ratio(amount, available) > 1.0, finfr("Exceeds available funds"))
    try when(available == 0, finfr("No available funds"))

    return Payment(amount: amount)
}
```

#### Pattern 2: Check with fin

```swift
func checkTask(task: Task) throws {
    if try when(task.isComplete, fin("Already completed")) {
        return // Task is done
    }

    // Continue processing
}
```

#### Pattern 3: Ratio Monitoring

```swift
struct SystemMonitor: View {
    let memoryUsed: Double
    let memoryTotal: Double

    var body: some View {
        VStack {
            RatioIndicator(
                f: memoryUsed,
                g: memoryTotal,
                threshold: 0.9,
                label: "Memory"
            )

            if ratio(memoryUsed, memoryTotal) > 0.9 {
                Text("Warning: High memory usage")
                    .foregroundColor(.orange)
            }
        }
    }
}
```

---

## Part III: The Architecture

### Chapter 5: Blueprint - Constraint-Governed Types

A **Blueprint** is a type with built-in constraints. Think of it as a class that can never be in an invalid state.

```swift
@Observable
final class BankAccount: Blueprint {
    typealias State = AccountState

    var state: AccountState

    init(balance: Double) {
        self.state = AccountState(balance: balance, frozen: false)
    }

    // Laws define what states are valid
    var laws: [Law<AccountState>] {
        [
            Law("no_negative_balance") { state in
                if state.balance < 0 {
                    return .finfr("Balance cannot be negative")
                }
                return .allowed
            }
        ]
    }

    func saveState() -> AccountState { state }
    func restoreState(_ saved: AccountState) { state = saved }
}
```

### Chapter 6: Laws - Defining Valid States

**Laws** are constraints that must always hold. They're checked after every state mutation.

```swift
var laws: [Law<AccountState>] {
    [
        // Law 1: No overdraft beyond limit
        Law("no_overdraft") { state in
            if state.balance < -state.overdraftLimit {
                return .finfr("Exceeds overdraft limit")
            }
            return .allowed
        },

        // Law 2: f/g ratio check
        Law("withdrawal_ratio") { state in
            // Check happens in forge, not here
            return .allowed
        },

        // Law 3: Business rule
        Law("minimum_balance") { state in
            if state.accountType == .premium && state.balance < 1000 {
                return .finfr("Premium accounts require $1000 minimum")
            }
            return .allowed
        }
    ]
}
```

#### Law DSL Syntax

Use the `laws` builder for cleaner syntax:

```swift
var laws: [Law<State>] {
    laws {
        Law("rule_1") { state in ... }
        Law("rule_2") { state in ... }
        Law("rule_3") { state in ... }
    }
}
```

### Chapter 7: Forge - Atomic Mutations

A **Forge** performs atomic state mutations with automatic rollback.

```swift
func withdraw(_ amount: Double) -> Result<Double, Finfr> {
    // Pre-checks (optional but recommended)
    let r = ratio(amount, state.balance)
    if r > 1.0 {
        return .failure(Finfr("Exceeds balance", law: "withdrawal_ratio"))
    }

    // Execute with automatic rollback on law violation
    return Forge(self).execute { state in
        state.balance -= amount
        return amount
    }
}
```

#### How Forge Works

1. **Save** - Current state is saved
2. **Execute** - Your mutation runs
3. **Check** - All laws are evaluated
4. **Commit or Rollback** - If any law is violated, state is restored

```swift
// This is what Forge does internally:
let saved = saveState()
do {
    let result = try operation(&state)

    let check = checkLaws()
    if !check.passed {
        restoreState(saved)
        return .failure(...)
    }

    return .success(result)
} catch {
    restoreState(saved)
    return .failure(...)
}
```

---

## Part IV: SwiftUI Integration

### Chapter 8: Verified Views

#### The `verified(by:)` Modifier

Only render a view if a blueprint's laws are satisfied:

```swift
struct AccountView: View {
    @State private var account = BankAccount(balance: 1000)

    var body: some View {
        VStack {
            BalanceDisplay(balance: account.state.balance)
        }
        .verified(by: account, fallback: InvalidStateView())
    }
}
```

#### The `@Verified` Property Wrapper

Create state that silently rejects invalid values:

```swift
struct ScoreEntry: View {
    @Verified(wrappedValue: 0.0) { score in
        score >= 0 && score <= 100 ? .allowed : .finfr("Score must be 0-100")
    }
    var score: Double

    var body: some View {
        Slider(value: $score, in: 0...100)
        // Values outside 0-100 are silently rejected
    }
}
```

### Chapter 9: Status Components

#### RatioIndicator

Display real-time f/g ratio status:

```swift
RatioIndicator(
    f: withdrawal,
    g: balance,
    threshold: 1.0,
    label: "withdrawal/balance"
)
```

The indicator shows:
- **Green** when ratio ≤ threshold
- **Yellow** when ratio is within 120% of threshold
- **Red** when ratio exceeds threshold or is undefined

#### NewtonBadge

Display verification status:

```swift
NewtonBadge(
    verified: account.checkLaws().passed,
    fingerprint: prove(account).fingerprint
)
```

This shows "1 == 1" with a checkmark when all laws pass.

### Chapter 10: Live Validation

Implement real-time constraint feedback:

```swift
struct WithdrawalForm: View {
    @State private var account = BankAccount(balance: 1000)
    @State private var amount: String = ""

    var parsedAmount: Double? {
        Double(amount)
    }

    var canWithdraw: Bool {
        guard let amt = parsedAmount, amt > 0 else { return false }
        return ratio(amt, account.state.balance) <= 1.0
    }

    var body: some View {
        Form {
            TextField("Amount", text: $amount)
                .keyboardType(.decimalPad)

            if let amt = parsedAmount {
                RatioIndicator(
                    f: amt,
                    g: account.state.balance,
                    threshold: 1.0
                )
            }

            Button("Withdraw") {
                // ...
            }
            .disabled(!canWithdraw)
        }
    }
}
```

---

## Part V: The Combo Pattern

### Chapter 11: Building Combo Sets

**Combos** are the heart of TinyTalk. Each combo defines a valid combination of preconditions and a transformation.

```swift
struct PaymentRequest: Sendable {
    var amount: Double
    var method: PaymentMethod
    var balance: Double
    var creditLimit: Double
    var verified: Bool
}

let paymentCombos = combos {
    // Combo 1: Debit payment
    Combo<PaymentRequest, Payment>(
        "debit",
        when: [
            { $0.method == .debit },
            { $0.amount > 0 },
            { ratio($0.amount, $0.balance) <= 1.0 }
        ]
    ) { request in
        Payment(amount: request.amount, method: .debit)
    }

    // Combo 2: Credit payment
    Combo<PaymentRequest, Payment>(
        "credit",
        when: [
            { $0.method == .credit },
            { $0.amount > 0 },
            { ratio($0.amount, $0.creditLimit) <= 1.0 }
        ]
    ) { request in
        Payment(amount: request.amount, method: .credit)
    }

    // Combo 3: Verified large payment
    Combo<PaymentRequest, Payment>(
        "large_verified",
        when: [
            { $0.amount > 10000 },
            { $0.verified }
        ]
    ) { request in
        Payment(amount: request.amount, method: request.method, verified: true)
    }
}
```

### Chapter 12: Combo Execution

Execute the first matching combo:

```swift
let request = PaymentRequest(
    amount: 500,
    method: .debit,
    balance: 1000,
    creditLimit: 5000,
    verified: false
)

switch paymentCombos.execute(request) {
case .success(let payment):
    print("Payment processed: \(payment)")
case .failure(let finfr):
    print("Cannot process: \(finfr.reason)")
}
```

### Chapter 13: Combo Design Principles

#### Principle 1: Mutually Exclusive Combos

Each request should match **at most one** combo. If multiple combos could match, the first one wins.

```swift
// Good: Mutually exclusive conditions
Combo("small_order", when: [{ $0.amount < 100 }]) { ... }
Combo("large_order", when: [{ $0.amount >= 100 }]) { ... }

// Bad: Overlapping conditions
Combo("order_a", when: [{ $0.amount > 50 }]) { ... }
Combo("order_b", when: [{ $0.amount < 150 }]) { ... }
// If amount is 75, both could match!
```

#### Principle 2: Exhaustive Coverage

Define combos for all valid states. If no combo matches, the request fails.

```swift
// Ensure you have combos for all valid cases
let orderCombos = combos {
    Combo("online") { ... }
    Combo("instore") { ... }
    Combo("phone") { ... }
    // What about "mail"? If valid, add a combo!
}
```

#### Principle 3: Single Responsibility

Each combo should handle one scenario completely.

```swift
// Good: Each combo is self-contained
Combo("express_shipping", when: [
    { $0.shipping == .express },
    { $0.weight <= 5 },
    { $0.destination.isExpress }
]) { request in
    ShippingLabel(method: .express, price: 25.00)
}

// Bad: Combo relies on external state
Combo("shipping", when: [{ $0.isValid }]) { request in
    // What does "isValid" mean? Not clear from combo.
}
```

---

## Part VI: Real-World Examples

### Chapter 14: Teacher's Aide

A lesson plan generator that uses combos to handle different classroom scenarios.

```swift
struct LessonRequest: Sendable {
    var grade: Int
    var subject: String
    var topic: String
    var duration: Int // minutes
    var masteryRate: Double // 0.0 to 1.0
}

let lessonCombos = combos {
    // High mastery: enrichment
    Combo<LessonRequest, LessonPlan>(
        "enrichment",
        when: [
            { $0.masteryRate >= 0.7 },
            { $0.duration >= 30 }
        ]
    ) { request in
        LessonPlan(
            title: "\(request.topic) - Enrichment",
            activities: ["Challenge problems", "Peer teaching", "Extension project"],
            differentiation: [
                .mastery: "Lead peer groups",
                .approaching: "Collaborative work",
                .developing: "Guided practice",
                .reteach: "Small group with teacher"
            ]
        )
    }

    // Low mastery: reteach
    Combo<LessonRequest, LessonPlan>(
        "reteach",
        when: [
            { $0.masteryRate < 0.3 },
            { $0.duration >= 30 }
        ]
    ) { request in
        LessonPlan(
            title: "\(request.topic) - Reteach",
            activities: ["Concrete examples", "Guided practice", "Check for understanding"],
            differentiation: [
                .mastery: "Peer tutor role",
                .approaching: "Standard practice",
                .developing: "Visual aids",
                .reteach: "One-on-one support"
            ]
        )
    }

    // Mixed class: stations
    Combo<LessonRequest, LessonPlan>(
        "balanced",
        when: [
            { $0.masteryRate >= 0.3 && $0.masteryRate < 0.7 }
        ]
    ) { request in
        LessonPlan(
            title: request.topic,
            activities: ["Hook", "Direct instruction", "Station rotation", "Closure"],
            differentiation: [:]
        )
    }
}
```

### Chapter 15: Content Safety

A verification system using f/g ratios for severity analysis.

```swift
@Observable
final class ContentSafety: Blueprint {
    typealias State = SafetyState

    var state: SafetyState

    var laws: [Law<SafetyState>] {
        [
            Law("severity_limit") { state in
                guard state.totalChecks > 0 else { return .allowed }
                let severity = ratio(
                    Double(state.violations.count),
                    Double(state.totalChecks)
                )
                if severity > 0.3 {
                    return .finfr("Content severity too high")
                }
                return .allowed
            }
        ]
    }

    func check(_ content: String) -> SafetyResult {
        // Run pattern checks
        let violations = patterns.flatMap { category, keywords in
            keywords.filter { content.lowercased().contains($0) }
                .map { _ in category }
        }

        state.violations = violations
        state.totalChecks = patterns.count

        let severity = state.totalChecks > 0
            ? Double(violations.count) / Double(state.totalChecks)
            : 0

        return SafetyResult(
            safe: violations.isEmpty,
            severity: severity,
            proof: prove(self)
        )
    }
}
```

### Chapter 16: Gradebook

A complete grade tracking system with verification.

```swift
@Observable
final class Gradebook: Blueprint {
    typealias State = GradebookState
    var state: GradebookState

    var laws: [Law<GradebookState>] {
        [
            // Scores cannot exceed max
            Law("score_bounds") { state in
                for entry in state.entries {
                    if ratio(entry.score, entry.maxScore) > 1.0 {
                        return .finfr("Score exceeds maximum")
                    }
                }
                return .allowed
            },

            // Max entries per student
            Law("entry_limit") { state in
                let grouped = Dictionary(grouping: state.entries, by: \.student)
                for (student, entries) in grouped {
                    if entries.count > state.maxEntriesPerStudent {
                        return .finfr("\(student) has too many entries")
                    }
                }
                return .allowed
            }
        ]
    }

    func addGrade(student: String, score: Double, max: Double) -> Result<GradeEntry, Finfr> {
        // Pre-check ratio
        if ratio(score, max) > 1.0 {
            return .failure(Finfr("Score exceeds maximum", law: "score_bounds"))
        }

        return Forge(self).execute { state in
            let entry = GradeEntry(student: student, score: score, maxScore: max)
            state.entries.append(entry)
            return entry
        }
    }
}
```

---

## Part VII: Best Practices

### Chapter 17: Design Guidelines

#### Guideline 1: Define Laws First

Before writing any forges, define your laws. What states are invalid?

```swift
// Start with laws
var laws: [Law<State>] {
    [
        Law("balance_non_negative") { ... },
        Law("no_overdraft") { ... },
        Law("frozen_cannot_transact") { ... }
    ]
}

// Then write forges
func withdraw(_ amount: Double) -> Result<...> { ... }
func deposit(_ amount: Double) -> Result<...> { ... }
```

#### Guideline 2: Use Ratios for Bounds Checking

Whenever you're checking if something exceeds a limit, use `ratio()`:

```swift
// Good: ratio clearly shows the relationship
if ratio(withdrawal, balance) > 1.0 { ... }
if ratio(score, maxScore) > 1.0 { ... }
if ratio(usedMemory, totalMemory) > 0.9 { ... }

// Avoid: raw comparison obscures the relationship
if withdrawal > balance { ... }
```

#### Guideline 3: Make Constraints Visible

Use `RatioIndicator` and `NewtonBadge` to show constraint status in UI:

```swift
var body: some View {
    Form {
        // Input
        TextField("Amount", text: $amount)

        // Live constraint feedback
        if let amt = Double(amount) {
            RatioIndicator(f: amt, g: balance, threshold: 1.0)
        }

        // Verification status
        NewtonBadge(verified: account.checkLaws().passed)
    }
}
```

#### Guideline 4: Fail Fast with Pre-Checks

Check preconditions before calling Forge:

```swift
func withdraw(_ amount: Double) -> Result<Double, Finfr> {
    // Pre-checks (fast, no state save)
    if amount <= 0 {
        return .failure(Finfr("Amount must be positive"))
    }
    if ratio(amount, state.balance) > 1.0 {
        return .failure(Finfr("Exceeds balance"))
    }

    // Forge (saves state, runs laws)
    return Forge(self).execute { state in
        state.balance -= amount
        return amount
    }
}
```

### Chapter 18: Common Patterns

#### Pattern: Compound Laws

Combine multiple checks in a single law:

```swift
Law("valid_transaction") { state in
    guard state.balance >= 0 else {
        return .finfr("Negative balance")
    }
    guard !state.frozen else {
        return .finfr("Account frozen")
    }
    guard state.balance >= state.minimumBalance else {
        return .finfr("Below minimum balance")
    }
    return .allowed
}
```

#### Pattern: Contextual Laws

Laws that only apply in certain contexts:

```swift
Law("premium_minimum") { state in
    // Only applies to premium accounts
    guard state.accountType == .premium else {
        return .allowed
    }
    if state.balance < 1000 {
        return .finfr("Premium requires $1000 minimum")
    }
    return .allowed
}
```

#### Pattern: Combo Fallback

Add a default combo that catches unmatched requests:

```swift
let requestCombos = combos {
    Combo("case_a", when: [...]) { ... }
    Combo("case_b", when: [...]) { ... }

    // Fallback: always matches if nothing else did
    Combo<Request, Response>("default", when: [{ _ in true }]) { request in
        Response.default(for: request)
    }
}
```

### Chapter 19: Testing Blueprints

Test that laws properly reject invalid states:

```swift
@Test
func testOverdraftPrevention() {
    let account = BankAccount(balance: 100)

    // Should fail: exceeds balance
    let result = account.withdraw(150)

    #expect(result.isFailure)
    if case .failure(let finfr) = result {
        #expect(finfr.lawName == "no_overdraft")
    }
}

@Test
func testValidWithdrawal() {
    let account = BankAccount(balance: 100)

    // Should succeed: within balance
    let result = account.withdraw(50)

    #expect(result.isSuccess)
    #expect(account.state.balance == 50)
}

@Test
func testRollbackOnViolation() {
    let account = BankAccount(balance: 100)

    // This forge would violate the law
    let result = Forge(account).execute { state in
        state.balance = -500  // Invalid!
    }

    #expect(result.isFailure)
    #expect(account.state.balance == 100)  // Rolled back
}
```

---

## Part VIII: Advanced Topics

### Chapter 20: Async Forges

For operations that require network or database access:

```swift
func transferAsync(to recipient: Account, amount: Double) async -> Result<Transfer, Finfr> {
    // Pre-check
    if ratio(amount, state.balance) > 1.0 {
        return .failure(Finfr("Exceeds balance"))
    }

    return await Forge(self).executeAsync { state in
        // Call remote service
        let transfer = try await transferService.initiate(
            from: self.id,
            to: recipient.id,
            amount: amount
        )

        state.balance -= amount
        return transfer
    }
}
```

### Chapter 21: Verification Proofs

Generate cryptographic proof of constraint satisfaction:

```swift
let proof = prove(account)

print(proof.fingerprint)          // "A3F8C2E1"
print(proof.constraintsSatisfied) // 3
print(proof.signature)            // "N2_B7E4D9F2A1C38E5D"
```

Use proofs for:
- Audit trails
- Compliance verification
- Third-party validation

### Chapter 22: Cross-Blueprint Coordination

When multiple blueprints need to coordinate:

```swift
func transfer(from source: BankAccount, to dest: BankAccount, amount: Double) -> Result<Transfer, Finfr> {
    // Check source
    if ratio(amount, source.state.balance) > 1.0 {
        return .failure(Finfr("Source has insufficient funds"))
    }

    // Execute atomically
    let sourceResult = source.withdraw(amount)
    guard case .success = sourceResult else {
        return .failure(Finfr("Source withdrawal failed"))
    }

    let destResult = dest.deposit(amount)
    guard case .success = destResult else {
        // Rollback source
        _ = source.deposit(amount)
        return .failure(Finfr("Destination deposit failed"))
    }

    return .success(Transfer(amount: amount, from: source.id, to: dest.id))
}
```

---

## Appendix A: Quick Reference

### Lexicon

| Primitive | Meaning | Usage |
|-----------|---------|-------|
| `fin` | Closure (can reopen) | `fin("Task complete")` |
| `finfr` | Finality (ontological death) | `finfr("Cannot exist")` |
| `when` | State declaration | `try when(x > y, finfr("..."))` |
| `ratio` | f/g dimensional analysis | `ratio(attempt, limit)` |

### Architecture

| Component | Purpose |
|-----------|---------|
| `Blueprint` | Constraint-governed type protocol |
| `Law` | Constraint definition |
| `Forge` | Atomic mutation with rollback |
| `Combo` | Valid state combination |
| `ComboSet` | Collection of mutually exclusive combos |

### SwiftUI Components

| Component | Purpose |
|-----------|---------|
| `verified(by:)` | View modifier for constraint checking |
| `@Verified` | Property wrapper for validated state |
| `RatioIndicator` | Visual f/g ratio display |
| `NewtonBadge` | Verification status indicator |

### Operators on Ratio

```swift
let r = ratio(f, g)

r < 1.0      // Below threshold
r <= 1.0     // At or below threshold
r > 1.0      // Exceeds threshold
r >= 1.0     // At or above threshold
r == 1.0     // At threshold (within epsilon)
r.isUndefined // g ≈ 0 (ontological death)
r.value      // The computed ratio (Double)
```

---

## Appendix B: Migration Guide

### From Traditional Swift to TinyTalk

**Before:**

```swift
func processOrder(order: Order) throws -> Receipt {
    guard order.items.count > 0 else {
        throw OrderError.noItems
    }
    guard order.total > 0 else {
        throw OrderError.invalidTotal
    }
    guard order.total <= customer.balance else {
        throw OrderError.insufficientFunds
    }
    guard !customer.suspended else {
        throw OrderError.customerSuspended
    }
    // ... process order
}
```

**After:**

```swift
let orderCombos = combos {
    Combo<Order, Receipt>(
        "valid_order",
        when: [
            { $0.items.count > 0 },
            { $0.total > 0 },
            { ratio($0.total, $0.customer.balance) <= 1.0 },
            { !$0.customer.suspended }
        ]
    ) { order in
        Receipt(order: order)
    }
}

// Usage
switch orderCombos.execute(order) {
case .success(let receipt): // Done
case .failure(let finfr): // Cannot process
}
```

---

## Closing Note

TinyTalk is not just a library—it's a way of thinking about computation.

When you write traditional code, you enumerate invalid states. When you write TinyTalk, you declare valid combinations. This shift from permutations to combinations is the core insight.

The f/g ratio captures a fundamental truth: **you cannot attempt more than reality allows**. When your withdrawal exceeds your balance, when your payload exceeds your bandwidth, when your ambition exceeds your resources—the ratio tells the truth.

`1 == 1`. The constraint check IS the computation. Newton only accepts what works.

Now go build something verified.

---

**© 2026 Jared Lewis Conglomerate. All rights reserved.**

Newton · tinyTalk · Ada Computing Company · parcRI

---

```
when tinytalk_course:
    and has_philosophy_section
    and has_lexicon_section
    and has_architecture_section
    and has_swiftui_section
    and has_combo_pattern_section
    and has_examples_section
    and has_best_practices
    and has_appendices
fin course_complete

f/g ratio: 1.0
Fingerprint: TINYTALK_COURSE_V1
```
