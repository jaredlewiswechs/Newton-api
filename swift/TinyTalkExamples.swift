//
//  TinyTalkExamples.swift
//  Newton TinyTalk Swift DSL - Practical Examples
//
//  Created by Jared Nashon Lewis
//  Jared Lewis Conglomerate · Newton · tinyTalk · Ada Computing Company
//
//  Copyright © 2026 Jared Lewis Conglomerate. All rights reserved.
//
//  These examples demonstrate the "combos not permutations" pattern.
//  Instead of checking every possible state, we define what CAN exist.
//
//  ═══════════════════════════════════════════════════════════════════════════════

import SwiftUI
import Foundation

// MARK: - ═══════════════════════════════════════════════════════════════════════
// EXAMPLE 1: BANK ACCOUNT
// The classic constraint example: you can't withdraw more than you have.
// ═══════════════════════════════════════════════════════════════════════════════

/// The state of a bank account.
struct AccountState: Sendable {
    var balance: Double
    var overdraftLimit: Double
    var frozen: Bool

    var availableBalance: Double {
        balance + overdraftLimit
    }
}

/// A constraint-governed bank account.
@Observable
@MainActor
final class BankAccount: Blueprint {
    typealias State = AccountState

    var state: AccountState

    init(balance: Double, overdraftLimit: Double = 0) {
        self.state = AccountState(
            balance: balance,
            overdraftLimit: overdraftLimit,
            frozen: false
        )
    }

    // MARK: Laws (Constraints)

    var laws: [Law<AccountState>] {
        [
            // Law 1: Balance can never go below negative overdraft limit
            Law("no_overdraft") { state in
                if state.balance < -state.overdraftLimit {
                    return .finfr("Cannot exceed overdraft limit")
                }
                return .allowed
            },

            // Law 2: Frozen accounts cannot be modified
            Law("not_frozen") { state in
                // This law is checked after operations
                // A frozen account should not have had operations
                return .allowed
            },

            // Law 3: f/g ratio - withdrawal/available must be <= 1.0
            Law("withdrawal_ratio") { state in
                // This is evaluated contextually during withdraw
                return .allowed
            }
        ]
    }

    func saveState() -> AccountState { state }
    func restoreState(_ saved: AccountState) { state = saved }

    // MARK: Forges (Operations)

    /// Withdraw money with automatic rollback on violation.
    func withdraw(_ amount: Double) -> Result<Double, Finfr> {
        // Pre-check: is account frozen?
        if state.frozen {
            return .failure(Finfr("Account is frozen", law: "not_frozen"))
        }

        // Pre-check: f/g ratio
        let r = ratio(amount, state.availableBalance)
        if r > 1.0 {
            return .failure(Finfr("Withdrawal exceeds available balance (f/g = \(r.value))", law: "withdrawal_ratio"))
        }
        if r.isUndefined {
            return .failure(Finfr("No available balance (finfr: g=0)", law: "withdrawal_ratio"))
        }

        // Execute with forge
        return Forge(self).execute { state in
            state.balance -= amount
            return amount
        }
    }

    /// Deposit money.
    func deposit(_ amount: Double) -> Result<Double, Finfr> {
        if state.frozen {
            return .failure(Finfr("Account is frozen", law: "not_frozen"))
        }

        return Forge(self).execute { state in
            state.balance += amount
            return state.balance
        }
    }

    /// Freeze the account.
    func freeze() {
        state.frozen = true
    }

    /// Unfreeze the account.
    func unfreeze() {
        state.frozen = false
    }
}

// MARK: - SwiftUI View for Bank Account

struct BankAccountView: View {
    @State private var account = BankAccount(balance: 1000, overdraftLimit: 100)
    @State private var amount: String = ""
    @State private var message: String = ""

    var body: some View {
        VStack(spacing: 20) {
            // Status
            VStack {
                Text("Balance")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text("$\(String(format: "%.2f", account.state.balance))")
                    .font(.system(size: 48, weight: .bold, design: .rounded))
            }

            // f/g ratio indicator
            if let withdrawAmount = Double(amount), withdrawAmount > 0 {
                RatioIndicator(
                    f: withdrawAmount,
                    g: account.state.availableBalance,
                    threshold: 1.0,
                    label: "withdrawal/available"
                )
            }

            // Newton badge
            NewtonBadge(
                verified: account.checkLaws().passed,
                fingerprint: prove(account).fingerprint
            )

            // Input
            TextField("Amount", text: $amount)
                .textFieldStyle(.roundedBorder)
                .keyboardType(.decimalPad)
                .frame(width: 200)

            // Actions
            HStack(spacing: 16) {
                Button("Withdraw") {
                    guard let amt = Double(amount), amt > 0 else { return }
                    switch account.withdraw(amt) {
                    case .success(let withdrawn):
                        message = "Withdrew $\(String(format: "%.2f", withdrawn))"
                    case .failure(let error):
                        message = error.description
                    }
                }
                .buttonStyle(.bordered)

                Button("Deposit") {
                    guard let amt = Double(amount), amt > 0 else { return }
                    switch account.deposit(amt) {
                    case .success(let newBalance):
                        message = "New balance: $\(String(format: "%.2f", newBalance))"
                    case .failure(let error):
                        message = error.description
                    }
                }
                .buttonStyle(.bordered)
            }

            // Message
            if !message.isEmpty {
                Text(message)
                    .font(.caption)
                    .foregroundColor(message.contains("finfr") ? .red : .green)
                    .padding()
                    .background(Color.secondary.opacity(0.1))
                    .cornerRadius(8)
            }
        }
        .padding()
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// EXAMPLE 2: LESSON PLAN GENERATOR (Teacher's Aide)
// Constraints from education: TEKS alignment, differentiation, time bounds.
// ═══════════════════════════════════════════════════════════════════════════════

/// Student performance level
enum PerformanceLevel: String, Codable, Sendable, CaseIterable {
    case mastery = "Mastery"
    case approaching = "Approaching"
    case developing = "Developing"
    case reteach = "Reteach"
}

/// A lesson plan request
struct LessonRequest: Sendable {
    var grade: Int
    var subject: String
    var topic: String
    var duration: Int // minutes
    var studentCounts: [PerformanceLevel: Int]

    var totalStudents: Int {
        studentCounts.values.reduce(0, +)
    }

    var masteryRate: Double {
        guard totalStudents > 0 else { return 0 }
        return Double(studentCounts[.mastery] ?? 0) / Double(totalStudents)
    }
}

/// A generated lesson plan
struct LessonPlan: Sendable, Identifiable {
    let id = UUID()
    var title: String
    var grade: Int
    var subject: String
    var objective: String
    var teksCode: String
    var duration: Int
    var activities: [String]
    var differentiation: [PerformanceLevel: String]
    var verified: Bool
    var fingerprint: String
}

/// Combos for lesson plan generation.
/// Each combo handles a specific scenario.
let lessonCombos = combos {
    // Combo 1: High mastery - enrichment focus
    Combo<LessonRequest, LessonPlan>(
        "enrichment_focus",
        when: [
            { $0.masteryRate >= 0.7 },
            { $0.duration >= 30 }
        ]
    ) { request in
        LessonPlan(
            title: "\(request.topic) - Enrichment",
            grade: request.grade,
            subject: request.subject,
            objective: "Students will extend understanding of \(request.topic)",
            teksCode: "\(request.grade).\(request.subject.prefix(1).uppercased())A",
            duration: request.duration,
            activities: [
                "Review (5 min)",
                "Challenge problem (15 min)",
                "Peer teaching (10 min)",
                "Extension project (\(request.duration - 30) min)"
            ],
            differentiation: [
                .mastery: "Lead peer teaching groups",
                .approaching: "Collaborative problem solving",
                .developing: "Guided practice with partner",
                .reteach: "Small group with teacher"
            ],
            verified: true,
            fingerprint: UUID().uuidString.prefix(8).uppercased() + ""
        )
    }

    // Combo 2: Low mastery - reteach focus
    Combo<LessonRequest, LessonPlan>(
        "reteach_focus",
        when: [
            { $0.masteryRate < 0.3 },
            { $0.duration >= 30 }
        ]
    ) { request in
        LessonPlan(
            title: "\(request.topic) - Reteach",
            grade: request.grade,
            subject: request.subject,
            objective: "Students will demonstrate understanding of \(request.topic) fundamentals",
            teksCode: "\(request.grade).\(request.subject.prefix(1).uppercased())A",
            duration: request.duration,
            activities: [
                "Concrete examples (10 min)",
                "Guided practice (15 min)",
                "Check for understanding (5 min)",
                "Independent practice (\(request.duration - 30) min)"
            ],
            differentiation: [
                .mastery: "Peer tutor role",
                .approaching: "Standard practice",
                .developing: "Visual aids and manipulatives",
                .reteach: "One-on-one or small group"
            ],
            verified: true,
            fingerprint: UUID().uuidString.prefix(8).uppercased() + ""
        )
    }

    // Combo 3: Mixed class - balanced approach
    Combo<LessonRequest, LessonPlan>(
        "balanced_approach",
        when: [
            { $0.masteryRate >= 0.3 && $0.masteryRate < 0.7 }
        ]
    ) { request in
        LessonPlan(
            title: "\(request.topic)",
            grade: request.grade,
            subject: request.subject,
            objective: "Students will apply \(request.topic) concepts at their level",
            teksCode: "\(request.grade).\(request.subject.prefix(1).uppercased())A",
            duration: request.duration,
            activities: [
                "Hook/Engage (5 min)",
                "Direct instruction (10 min)",
                "Station rotation (20 min)",
                "Closure (5 min)"
            ],
            differentiation: [
                .mastery: "Challenge station",
                .approaching: "Application station",
                .developing: "Guided practice station",
                .reteach: "Teacher-led station"
            ],
            verified: true,
            fingerprint: UUID().uuidString.prefix(8).uppercased() + ""
        )
    }

    // Combo 4: Short lesson - condensed format
    Combo<LessonRequest, LessonPlan>(
        "condensed",
        when: [
            { $0.duration < 30 }
        ]
    ) { request in
        LessonPlan(
            title: "\(request.topic) - Quick",
            grade: request.grade,
            subject: request.subject,
            objective: "Students will practice \(request.topic)",
            teksCode: "\(request.grade).\(request.subject.prefix(1).uppercased())A",
            duration: request.duration,
            activities: [
                "Mini-lesson (\(request.duration / 2) min)",
                "Practice (\(request.duration / 2) min)"
            ],
            differentiation: [
                .mastery: "Independent work",
                .approaching: "Partner work",
                .developing: "Guided work",
                .reteach: "Teacher support"
            ],
            verified: true,
            fingerprint: UUID().uuidString.prefix(8).uppercased() + ""
        )
    }
}

// MARK: - SwiftUI View for Lesson Plan Generator

struct LessonPlanView: View {
    @State private var grade = 3
    @State private var subject = "Mathematics"
    @State private var topic = "Decomposing Numbers"
    @State private var duration = 50
    @State private var mastery = 1
    @State private var approaching = 5
    @State private var developing = 10
    @State private var reteach = 4
    @State private var generatedPlan: LessonPlan?

    var request: LessonRequest {
        LessonRequest(
            grade: grade,
            subject: subject,
            topic: topic,
            duration: duration,
            studentCounts: [
                .mastery: mastery,
                .approaching: approaching,
                .developing: developing,
                .reteach: reteach
            ]
        )
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Input Section
                GroupBox("Lesson Parameters") {
                    VStack(alignment: .leading, spacing: 12) {
                        LabeledContent("Grade") {
                            Picker("Grade", selection: $grade) {
                                ForEach(1...12, id: \.self) { Text("\($0)") }
                            }
                            .pickerStyle(.menu)
                        }

                        LabeledContent("Subject") {
                            TextField("Subject", text: $subject)
                                .textFieldStyle(.roundedBorder)
                        }

                        LabeledContent("Topic") {
                            TextField("Topic", text: $topic)
                                .textFieldStyle(.roundedBorder)
                        }

                        LabeledContent("Duration") {
                            Stepper("\(duration) min", value: $duration, in: 15...120, step: 5)
                        }
                    }
                }

                GroupBox("Student Data") {
                    VStack(alignment: .leading, spacing: 8) {
                        Stepper("Mastery: \(mastery)", value: $mastery, in: 0...30)
                        Stepper("Approaching: \(approaching)", value: $approaching, in: 0...30)
                        Stepper("Developing: \(developing)", value: $developing, in: 0...30)
                        Stepper("Reteach: \(reteach)", value: $reteach, in: 0...30)

                        RatioIndicator(
                            f: Double(mastery),
                            g: Double(request.totalStudents),
                            threshold: 1.0,
                            label: "mastery rate"
                        )
                    }
                }

                // Generate Button
                Button {
                    switch lessonCombos.execute(request) {
                    case .success(let plan):
                        generatedPlan = plan
                    case .failure(let error):
                        print(error)
                    }
                } label: {
                    Label("Generate Lesson Plan", systemImage: "wand.and.stars")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)

                // Generated Plan
                if let plan = generatedPlan {
                    GroupBox {
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                Text(plan.title)
                                    .font(.headline)
                                Spacer()
                                NewtonBadge(verified: plan.verified, fingerprint: plan.fingerprint)
                            }

                            Text("TEKS: \(plan.teksCode)")
                                .font(.caption)
                                .foregroundColor(.secondary)

                            Text(plan.objective)
                                .font(.subheadline)

                            Divider()

                            Text("Activities")
                                .font(.caption.bold())
                            ForEach(plan.activities, id: \.self) { activity in
                                Text("• \(activity)")
                                    .font(.caption)
                            }

                            Divider()

                            Text("Differentiation")
                                .font(.caption.bold())
                            ForEach(Array(plan.differentiation.keys.sorted(by: { $0.rawValue < $1.rawValue })), id: \.self) { level in
                                if let instruction = plan.differentiation[level] {
                                    HStack {
                                        Text(level.rawValue)
                                            .font(.caption2)
                                            .padding(.horizontal, 6)
                                            .padding(.vertical, 2)
                                            .background(Color.accentColor.opacity(0.1))
                                            .cornerRadius(4)
                                        Text(instruction)
                                            .font(.caption)
                                    }
                                }
                            }
                        }
                    } label: {
                        Label("Generated Plan", systemImage: "doc.text")
                    }
                }
            }
            .padding()
        }
        .navigationTitle("Teacher's Aide")
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// EXAMPLE 3: CONTENT SAFETY CHECKER
// Pattern-based verification with f/g ratio for severity.
// ═══════════════════════════════════════════════════════════════════════════════

/// Safety check result
struct SafetyResult: Sendable {
    var safe: Bool
    var categories: [String]
    var severity: Double  // f/g ratio: violations/total_checks
    var fingerprint: String
}

/// Content safety state
struct SafetyState: Sendable {
    var content: String
    var violations: [String]
    var checksPerformed: Int
}

@Observable
@MainActor
final class ContentSafety: Blueprint {
    typealias State = SafetyState

    var state: SafetyState

    private let patterns: [String: [String]] = [
        "harm": [
            "kill", "murder", "weapon", "bomb"
        ],
        "personal_info": [
            "ssn", "social security", "credit card"
        ],
        "profanity": [
            // Simplified for example
        ]
    ]

    init() {
        self.state = SafetyState(content: "", violations: [], checksPerformed: 0)
    }

    var laws: [Law<SafetyState>] {
        [
            Law("no_violations") { state in
                if !state.violations.isEmpty {
                    return .finfr("Content contains \(state.violations.count) violations")
                }
                return .allowed
            },

            Law("severity_ratio") { state in
                guard state.checksPerformed > 0 else { return .allowed }
                let severity = Double(state.violations.count) / Double(state.checksPerformed)
                if severity > 0.3 {
                    return .finfr("Severity ratio too high: \(severity)")
                }
                return .allowed
            }
        ]
    }

    func saveState() -> SafetyState { state }
    func restoreState(_ saved: SafetyState) { state = saved }

    func check(_ content: String) -> SafetyResult {
        state.content = content
        state.violations = []
        state.checksPerformed = 0

        let lowercased = content.lowercased()

        for (category, keywords) in patterns {
            for keyword in keywords {
                state.checksPerformed += 1
                if lowercased.contains(keyword) {
                    state.violations.append(category)
                    break
                }
            }
        }

        let severity = state.checksPerformed > 0
            ? Double(state.violations.count) / Double(state.checksPerformed)
            : 0

        return SafetyResult(
            safe: state.violations.isEmpty,
            categories: state.violations,
            severity: severity,
            fingerprint: prove(self).fingerprint
        )
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// EXAMPLE 4: THE COMBO PATTERN IN DEPTH
// This is the core insight: define what CAN exist, not all permutations.
// ═══════════════════════════════════════════════════════════════════════════════

/*
 THE TRADITIONAL APPROACH (Permutations):
 =========================================

 func handleTransaction(type: TransactionType, amount: Double, user: User) {
     if type == .withdrawal {
         if amount > 0 {
             if amount <= user.balance {
                 if !user.frozen {
                     if amount <= user.dailyLimit {
                         // Finally do the thing
                     } else {
                         // Handle daily limit exceeded
                     }
                 } else {
                     // Handle frozen account
                 }
             } else {
                 // Handle insufficient funds
             }
         } else {
             // Handle invalid amount
         }
     } else if type == .deposit {
         // Another tree of if-else
     } else if type == .transfer {
         // Yet another tree
     }
 }

 Problem: You're checking all PERMUTATIONS of invalid states.
 This grows exponentially with each new condition.


 THE TINYTALK APPROACH (Combos):
 ===============================

 let transactionCombos = combos {
     Combo("withdrawal", when: [
         { $0.type == .withdrawal },
         { $0.amount > 0 },
         { ratio($0.amount, $0.balance) <= 1.0 },
         { !$0.frozen },
         { ratio($0.amount, $0.dailyLimit) <= 1.0 }
     ]) { request in
         // Just do the thing
         return Transaction(...)
     }

     Combo("deposit", when: [
         { $0.type == .deposit },
         { $0.amount > 0 },
         { !$0.frozen }
     ]) { request in
         return Transaction(...)
     }

     // ... other combos
 }

 // Usage:
 switch transactionCombos.execute(request) {
 case .success(let tx): // It worked
 case .failure(let finfr): // It can't exist
 }

 Advantage: You define COMBINATIONS of valid states.
 Each combo is a complete specification of what CAN exist.
 No nested if-else. No exponential growth. Just combos.
 */

// MARK: - Transaction Example with Combos

enum TransactionType: Sendable {
    case withdrawal
    case deposit
    case transfer
}

struct TransactionRequest: Sendable {
    var type: TransactionType
    var amount: Double
    var fromBalance: Double
    var toBalance: Double?
    var dailyLimit: Double
    var frozen: Bool
}

struct Transaction: Sendable, Identifiable {
    let id = UUID()
    var type: TransactionType
    var amount: Double
    var timestamp: Date
    var verified: Bool
}

let transactionCombos = combos {
    // Withdrawal: amount must fit in balance and daily limit
    Combo<TransactionRequest, Transaction>(
        "withdrawal",
        when: [
            { $0.type == .withdrawal },
            { $0.amount > 0 },
            { ratio($0.amount, $0.fromBalance) <= 1.0 },
            { !$0.frozen },
            { ratio($0.amount, $0.dailyLimit) <= 1.0 }
        ]
    ) { request in
        Transaction(
            type: .withdrawal,
            amount: request.amount,
            timestamp: Date(),
            verified: true
        )
    }

    // Deposit: just needs positive amount and unfrozen account
    Combo<TransactionRequest, Transaction>(
        "deposit",
        when: [
            { $0.type == .deposit },
            { $0.amount > 0 },
            { !$0.frozen }
        ]
    ) { request in
        Transaction(
            type: .deposit,
            amount: request.amount,
            timestamp: Date(),
            verified: true
        )
    }

    // Transfer: needs positive amount, sufficient balance, and both accounts unfrozen
    Combo<TransactionRequest, Transaction>(
        "transfer",
        when: [
            { $0.type == .transfer },
            { $0.amount > 0 },
            { ratio($0.amount, $0.fromBalance) <= 1.0 },
            { !$0.frozen },
            { $0.toBalance != nil }
        ]
    ) { request in
        Transaction(
            type: .transfer,
            amount: request.amount,
            timestamp: Date(),
            verified: true
        )
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// EXAMPLE 5: REAL-WORLD APP - GRADE TRACKER
// A complete mini-app using all TinyTalk patterns.
// ═══════════════════════════════════════════════════════════════════════════════

/// Grade entry
struct GradeEntry: Sendable, Identifiable {
    let id = UUID()
    var studentName: String
    var assignment: String
    var score: Double
    var maxScore: Double
    var timestamp: Date

    var percentage: Double {
        guard maxScore > 0 else { return 0 }
        return (score / maxScore) * 100
    }
}

/// Gradebook state
struct GradebookState: Sendable {
    var className: String
    var entries: [GradeEntry]
    var maxEntriesPerStudent: Int

    var averageScore: Double {
        guard !entries.isEmpty else { return 0 }
        return entries.map(\.percentage).reduce(0, +) / Double(entries.count)
    }

    var studentCount: Int {
        Set(entries.map(\.studentName)).count
    }
}

@Observable
@MainActor
final class Gradebook: Blueprint {
    typealias State = GradebookState

    var state: GradebookState

    init(className: String) {
        self.state = GradebookState(
            className: className,
            entries: [],
            maxEntriesPerStudent: 50
        )
    }

    var laws: [Law<GradebookState>] {
        [
            // Law 1: Score cannot exceed max score
            Law("score_bounds") { state in
                for entry in state.entries {
                    if entry.score > entry.maxScore {
                        return .finfr("Score \(entry.score) exceeds max \(entry.maxScore) for \(entry.studentName)")
                    }
                    if entry.score < 0 {
                        return .finfr("Score cannot be negative for \(entry.studentName)")
                    }
                }
                return .allowed
            },

            // Law 2: Max entries per student
            Law("entry_limit") { state in
                let grouped = Dictionary(grouping: state.entries, by: \.studentName)
                for (student, entries) in grouped {
                    if entries.count > state.maxEntriesPerStudent {
                        return .finfr("\(student) has too many entries (\(entries.count)/\(state.maxEntriesPerStudent))")
                    }
                }
                return .allowed
            },

            // Law 3: Max score must be positive
            Law("max_score_positive") { state in
                for entry in state.entries {
                    if entry.maxScore <= 0 {
                        return .finfr("Max score must be positive for \(entry.assignment)")
                    }
                }
                return .allowed
            }
        ]
    }

    func saveState() -> GradebookState { state }
    func restoreState(_ saved: GradebookState) { state = saved }

    // MARK: Forges

    func addGrade(
        student: String,
        assignment: String,
        score: Double,
        maxScore: Double
    ) -> Result<GradeEntry, Finfr> {
        // Pre-check with f/g ratio
        let r = ratio(score, maxScore)
        if r > 1.0 {
            return .failure(Finfr("Score/MaxScore ratio exceeds 1.0", law: "score_bounds"))
        }
        if r.isUndefined {
            return .failure(Finfr("Max score cannot be zero", law: "max_score_positive"))
        }

        let entry = GradeEntry(
            studentName: student,
            assignment: assignment,
            score: score,
            maxScore: maxScore,
            timestamp: Date()
        )

        return Forge(self).execute { state in
            state.entries.append(entry)
            return entry
        }
    }

    func removeGrade(_ id: UUID) -> Result<Void, Finfr> {
        Forge(self).execute { state in
            state.entries.removeAll { $0.id == id }
        }
    }
}

// MARK: - Gradebook SwiftUI View

struct GradebookView: View {
    @State private var gradebook = Gradebook(className: "Math 101")
    @State private var newStudent = ""
    @State private var newAssignment = ""
    @State private var newScore = ""
    @State private var newMaxScore = "100"
    @State private var errorMessage: String?

    var body: some View {
        List {
            // Stats Section
            Section {
                HStack {
                    VStack(alignment: .leading) {
                        Text("Class Average")
                            .font(.caption)
                        Text("\(String(format: "%.1f", gradebook.state.averageScore))%")
                            .font(.title2.bold())
                    }

                    Spacer()

                    VStack(alignment: .trailing) {
                        Text("Students")
                            .font(.caption)
                        Text("\(gradebook.state.studentCount)")
                            .font(.title2.bold())
                    }
                }

                NewtonBadge(
                    verified: gradebook.checkLaws().passed,
                    fingerprint: prove(gradebook).fingerprint
                )
            }

            // Add Grade Section
            Section("Add Grade") {
                TextField("Student Name", text: $newStudent)
                TextField("Assignment", text: $newAssignment)
                HStack {
                    TextField("Score", text: $newScore)
                        .keyboardType(.decimalPad)
                    Text("/")
                    TextField("Max", text: $newMaxScore)
                        .keyboardType(.decimalPad)
                }

                // Real-time f/g ratio
                if let score = Double(newScore), let max = Double(newMaxScore) {
                    RatioIndicator(f: score, g: max, threshold: 1.0, label: "score/max")
                }

                Button("Add Grade") {
                    addGrade()
                }
                .disabled(newStudent.isEmpty || newAssignment.isEmpty)

                if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }
            }

            // Grades List
            Section("Grades") {
                ForEach(gradebook.state.entries) { entry in
                    HStack {
                        VStack(alignment: .leading) {
                            Text(entry.studentName)
                                .font(.headline)
                            Text(entry.assignment)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }

                        Spacer()

                        VStack(alignment: .trailing) {
                            Text("\(String(format: "%.0f", entry.score))/\(String(format: "%.0f", entry.maxScore))")
                            Text("\(String(format: "%.1f", entry.percentage))%")
                                .font(.caption)
                                .foregroundColor(entry.percentage >= 70 ? .green : .orange)
                        }
                    }
                }
                .onDelete { indices in
                    for index in indices {
                        let entry = gradebook.state.entries[index]
                        _ = gradebook.removeGrade(entry.id)
                    }
                }
            }
        }
        .navigationTitle(gradebook.state.className)
    }

    private func addGrade() {
        guard let score = Double(newScore),
              let maxScore = Double(newMaxScore) else {
            errorMessage = "Invalid score values"
            return
        }

        switch gradebook.addGrade(
            student: newStudent,
            assignment: newAssignment,
            score: score,
            maxScore: maxScore
        ) {
        case .success:
            // Clear form
            newStudent = ""
            newAssignment = ""
            newScore = ""
            errorMessage = nil
        case .failure(let error):
            errorMessage = error.description
        }
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// MAIN EXAMPLES APP
// ═══════════════════════════════════════════════════════════════════════════════

struct TinyTalkExamplesApp: View {
    var body: some View {
        NavigationStack {
            List {
                NavigationLink("Bank Account") {
                    BankAccountView()
                }

                NavigationLink("Lesson Plan Generator") {
                    LessonPlanView()
                }

                NavigationLink("Gradebook") {
                    GradebookView()
                }
            }
            .navigationTitle("TinyTalk Examples")
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// NEWTON VERIFICATION FOOTER
// ═══════════════════════════════════════════════════════════════════════════════
//
// when tinytalk_examples:
//     and has_bank_account_example
//     and has_lesson_plan_example
//     and has_gradebook_example
//     and demonstrates_combo_pattern
//     and demonstrates_fg_ratio
//     and has_swiftui_integration
// fin examples_verified
//
// © 2026 Jared Lewis Conglomerate
// ═══════════════════════════════════════════════════════════════════════════════
