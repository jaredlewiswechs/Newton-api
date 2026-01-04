# TinyTalk Swift DSL

**Constraint-First Development for Apple Platforms**

*Jared Lewis Conglomerate · Newton · tinyTalk · Ada Computing Company*

---

## Overview

TinyTalk is a Swift DSL (Domain-Specific Language) for building verified applications on iOS, macOS, watchOS, and visionOS. Instead of checking every possible invalid state, you define what **can** exist—and let the system handle the rest.

```swift
// Traditional: check permutations of invalid states
if amount <= 0 { return .failure(...) }
if amount > balance { return .failure(...) }
if account.frozen { return .failure(...) }
// ... finally do the thing

// TinyTalk: define valid combinations
let withdrawalCombo = Combo("withdrawal", when: [
    { $0.amount > 0 },
    { ratio($0.amount, $0.balance) <= 1.0 },
    { !$0.frozen }
]) { request in
    Transaction(amount: request.amount)
}
```

## Quick Start

### 1. Add to Your Project

Copy `TinyTalk.swift` into your Xcode project.

### 2. Define a Blueprint

```swift
@Observable
final class BankAccount: Blueprint {
    typealias State = AccountState

    var state: AccountState

    var laws: [Law<AccountState>] {
        [
            Law("no_overdraft") { state in
                if state.balance < 0 {
                    return .finfr("Balance cannot be negative")
                }
                return .allowed
            }
        ]
    }

    func saveState() -> AccountState { state }
    func restoreState(_ saved: AccountState) { state = saved }

    // Forge: atomic mutation with rollback
    func withdraw(_ amount: Double) -> Result<Double, Finfr> {
        if ratio(amount, state.balance) > 1.0 {
            return .failure(Finfr("Exceeds balance"))
        }

        return Forge(self).execute { state in
            state.balance -= amount
            return amount
        }
    }
}
```

### 3. Use in SwiftUI

```swift
struct AccountView: View {
    @State private var account = BankAccount(balance: 1000)
    @State private var amount = ""

    var body: some View {
        VStack {
            Text("$\(account.state.balance, specifier: "%.2f")")

            if let amt = Double(amount) {
                RatioIndicator(f: amt, g: account.state.balance, threshold: 1.0)
            }

            TextField("Amount", text: $amount)

            Button("Withdraw") {
                if let amt = Double(amount) {
                    _ = account.withdraw(amt)
                }
            }

            NewtonBadge(verified: account.checkLaws().passed)
        }
    }
}
```

## The Lexicon

| Primitive | Meaning | Example |
|-----------|---------|---------|
| `fin` | Closure (can reopen) | `fin("Task done")` |
| `finfr` | Finality (ontological death) | `finfr("Cannot exist")` |
| `when` | State declaration | `try when(x > y, finfr(...))` |
| `ratio` | f/g dimensional analysis | `ratio(withdrawal, balance)` |

## Key Concepts

### The f/g Ratio

```
f/g = finfr

f = what you're attempting (forge/fact/function)
g = what reality allows (ground/goal/governance)
```

When `f/g > 1.0`, you're attempting more than possible.
When `g = 0`, the ratio is undefined (ontological death).

### Combos, Not Permutations

Instead of nested if-else checking all invalid states, define valid combinations:

```swift
let paymentCombos = combos {
    Combo("debit", when: [
        { $0.method == .debit },
        { ratio($0.amount, $0.balance) <= 1.0 }
    ]) { Payment(...) }

    Combo("credit", when: [
        { $0.method == .credit },
        { ratio($0.amount, $0.creditLimit) <= 1.0 }
    ]) { Payment(...) }
}

switch paymentCombos.execute(request) {
case .success(let payment): // Processed
case .failure(let finfr): // Cannot exist
}
```

## Files

| File | Description |
|------|-------------|
| `TinyTalk.swift` | Core DSL library |
| `TinyTalkExamples.swift` | Practical examples |
| `Ada.swift` | Intent-to-Transform compiler |

## Documentation

See `docs/TinyTalk_Swift_DSL_Course.md` for the complete course.

## License

© 2026 Jared Lewis Conglomerate. All rights reserved.

---

```
1 == 1
Ask Newton. Go.
```
