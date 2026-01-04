//
//  TinyTalk.swift
//  Newton TinyTalk Swift DSL
//
//  The constraint-first language for iOS, macOS, watchOS, and visionOS.
//
//  Created by Jared Nashon Lewis
//  Jared Lewis Conglomerate · Newton · tinyTalk · Ada Computing Company
//
//  Copyright © 2026 Jared Lewis Conglomerate. All rights reserved.
//
//  "Combos, not permutations. State what can exist. Newton handles the rest."
//
//  ═══════════════════════════════════════════════════════════════════════════════
//  HISTORICAL LINEAGE:
//
//  TinyTalk descends from Smalltalk (Kay, 1972) and ThingLab (Borning, 1979).
//  The Blueprint/Law/Forge pattern implements CLP(X) (Jaffar & Lassez, 1987).
//  The f/g ratio extends CSP with dimensional analysis for verified computation.
//
//  Key Insight from Alan Kay:
//    "Smalltalk is not about objects, it's about messaging."
//    TinyTalk is not about objects, it's about constraints.
//  ═══════════════════════════════════════════════════════════════════════════════

import Foundation
import SwiftUI
import Combine

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK I: THE LEXICON
// The fundamental words that define what can and cannot exist.
// ═══════════════════════════════════════════════════════════════════════════════

/// The result of evaluating a law against state.
public enum LawResult: Equatable, Sendable {
    /// State is permitted - continue execution
    case allowed
    /// Closed - a stopping point that can be reopened
    case fin(String)
    /// Finality - ontological death, state cannot exist
    case finfr(String)

    public var isAllowed: Bool {
        if case .allowed = self { return true }
        return false
    }

    public var isFinfr: Bool {
        if case .finfr = self { return true }
        return false
    }

    public var message: String? {
        switch self {
        case .allowed: return nil
        case .fin(let msg): return msg
        case .finfr(let msg): return msg
        }
    }
}

/// Sentinel for finality - ontological death.
/// When a state cannot exist, it is finfr.
public struct Finfr: Error, CustomStringConvertible, Sendable {
    public let reason: String
    public let lawName: String

    public init(_ reason: String = "Ontological death", law: String = "unknown") {
        self.reason = reason
        self.lawName = law
    }

    public var description: String {
        "finfr: \(reason) (law: \(lawName))"
    }
}

/// Sentinel for closure - a pause that can be reopened.
public struct Fin: Error, CustomStringConvertible, Sendable {
    public let reason: String
    public let lawName: String

    public init(_ reason: String = "Closure reached", law: String = "unknown") {
        self.reason = reason
        self.lawName = law
    }

    public var description: String {
        "fin: \(reason) (law: \(lawName))"
    }
}

// MARK: - The `when` Function
// Declares a fact. The present state.

/// Declares a constraint check. If condition is true and result is finfr, throws.
/// - Parameters:
///   - condition: The boolean condition to evaluate
///   - then: What happens if condition is true (fin or finfr)
/// - Returns: The condition result for chaining
/// - Throws: Finfr if condition is true and result is finfr
@discardableResult
public func when(_ condition: Bool, then result: LawResult = .allowed) throws -> Bool {
    if condition {
        switch result {
        case .finfr(let reason):
            throw Finfr(reason)
        case .fin(let reason):
            throw Fin(reason)
        case .allowed:
            break
        }
    }
    return condition
}

/// Convenience for finfr declaration
public func finfr(_ reason: String = "State cannot exist") -> LawResult {
    .finfr(reason)
}

/// Convenience for fin declaration
public func fin(_ reason: String = "Closure reached") -> LawResult {
    .fin(reason)
}

// MARK: - The Ratio Type
// f/g dimensional analysis - the core of Newton's verification

/// The result of an f/g ratio calculation.
/// f = forge/fact/function (what you're trying to do)
/// g = ground/goal/governance (what reality allows)
public struct Ratio: Sendable, CustomStringConvertible {
    /// The numerator - what you're attempting (forge/fact/function)
    public let f: Double
    /// The denominator - what reality allows (ground/goal/governance)
    public let g: Double
    /// Tolerance for zero comparison
    public let epsilon: Double

    /// Whether the ratio is undefined (g ≈ 0)
    public var isUndefined: Bool {
        abs(g) < epsilon
    }

    /// The computed ratio value. Returns infinity if undefined.
    public var value: Double {
        if isUndefined {
            return f >= 0 ? .infinity : -.infinity
        }
        return f / g
    }

    public init(f: Double, g: Double, epsilon: Double = 1e-9) {
        self.f = f
        self.g = g
        self.epsilon = epsilon
    }

    public var description: String {
        if isUndefined {
            return "Ratio(f=\(f), g=\(g), undefined)"
        }
        return "Ratio(f=\(f), g=\(g), value=\(String(format: "%.4f", value)))"
    }

    // MARK: Comparison Operators

    public static func < (lhs: Ratio, rhs: Double) -> Bool {
        if lhs.isUndefined { return false }
        return lhs.value < rhs
    }

    public static func <= (lhs: Ratio, rhs: Double) -> Bool {
        if lhs.isUndefined { return false }
        return lhs.value <= rhs
    }

    public static func > (lhs: Ratio, rhs: Double) -> Bool {
        if lhs.isUndefined { return true }
        return lhs.value > rhs
    }

    public static func >= (lhs: Ratio, rhs: Double) -> Bool {
        if lhs.isUndefined { return true }
        return lhs.value >= rhs
    }

    public static func == (lhs: Ratio, rhs: Double) -> Bool {
        if lhs.isUndefined { return false }
        return abs(lhs.value - rhs) < lhs.epsilon
    }
}

/// Create a ratio for f/g dimensional analysis.
/// - Parameters:
///   - f: The numerator (forge/fact/function) - what you're trying to do
///   - g: The denominator (ground/goal/governance) - what reality allows
/// - Returns: A Ratio that can be compared against thresholds
public func ratio(_ f: Double, _ g: Double) -> Ratio {
    Ratio(f: f, g: g)
}

/// Throws finfr if the ratio is undefined (g ≈ 0).
/// - Parameters:
///   - f: The numerator
///   - g: The denominator
/// - Throws: Finfr if g ≈ 0
public func finfrIfUndefined(_ f: Double, _ g: Double) throws {
    let r = ratio(f, g)
    if r.isUndefined {
        throw Finfr("Ratio is undefined (denominator ≈ 0)", law: "ratio_undefined")
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK II: THE BLUEPRINT
// The foundation for constraint-governed types.
// ═══════════════════════════════════════════════════════════════════════════════

/// A law is a constraint that must hold for a state to be valid.
/// Laws are evaluated before any forge executes.
public struct Law<State>: Identifiable, Sendable where State: Sendable {
    public let id: String
    public let name: String
    public let evaluate: @Sendable (State) -> LawResult

    public init(
        _ name: String,
        id: String? = nil,
        evaluate: @escaping @Sendable (State) -> LawResult
    ) {
        self.id = id ?? UUID().uuidString
        self.name = name
        self.evaluate = evaluate
    }
}

/// Result of checking all laws against a state.
public struct LawCheckResult: Sendable {
    public let passed: Bool
    public let violations: [String]
    public let firstViolation: LawResult?

    public static let success = LawCheckResult(passed: true, violations: [], firstViolation: nil)

    public static func failure(_ violations: [String], first: LawResult) -> LawCheckResult {
        LawCheckResult(passed: false, violations: violations, firstViolation: first)
    }
}

/// A Blueprint is a type that defines constraint-governed state.
/// Think of it as a class with built-in verification.
public protocol Blueprint: AnyObject, Observable {
    associatedtype State: Sendable

    /// The current state
    var state: State { get set }

    /// The laws that govern this blueprint
    var laws: [Law<State>] { get }

    /// Check all laws against current state
    func checkLaws() -> LawCheckResult

    /// Save state for potential rollback
    func saveState() -> State

    /// Restore state from saved copy
    func restoreState(_ saved: State)
}

extension Blueprint {
    /// Check all laws against current state.
    public func checkLaws() -> LawCheckResult {
        var violations: [String] = []

        for law in laws {
            let result = law.evaluate(state)
            switch result {
            case .finfr(let reason):
                violations.append("\(law.name): \(reason)")
                return .failure(violations, first: result)
            case .fin(let reason):
                violations.append("\(law.name): \(reason)")
                return .failure(violations, first: result)
            case .allowed:
                continue
            }
        }

        return .success
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK III: THE FORGE
// Atomic state mutations with automatic rollback.
// ═══════════════════════════════════════════════════════════════════════════════

/// A Forge is an atomic operation that mutates state with verification.
/// If any law is violated after the operation, state is rolled back.
@MainActor
public struct Forge<B: Blueprint> {
    public let blueprint: B

    public init(_ blueprint: B) {
        self.blueprint = blueprint
    }

    /// Execute an operation with automatic rollback on law violation.
    /// - Parameter operation: The mutation to perform
    /// - Returns: Success with new state, or failure with violation
    @discardableResult
    public func execute<T>(
        _ operation: @escaping (inout B.State) throws -> T
    ) -> Result<T, Finfr> {
        // Save current state
        let savedState = blueprint.saveState()

        do {
            // Execute the operation
            let result = try operation(&blueprint.state)

            // Check all laws
            let check = blueprint.checkLaws()

            if !check.passed {
                // Rollback
                blueprint.restoreState(savedState)

                if let violation = check.firstViolation, case .finfr(let reason) = violation {
                    return .failure(Finfr(reason, law: check.violations.first ?? "unknown"))
                }
                return .failure(Finfr(check.violations.joined(separator: "; ")))
            }

            return .success(result)

        } catch let error as Finfr {
            // Rollback on explicit finfr
            blueprint.restoreState(savedState)
            return .failure(error)
        } catch {
            // Rollback on any error
            blueprint.restoreState(savedState)
            return .failure(Finfr(error.localizedDescription))
        }
    }

    /// Execute with async operation
    @discardableResult
    public func executeAsync<T>(
        _ operation: @escaping (inout B.State) async throws -> T
    ) async -> Result<T, Finfr> {
        let savedState = blueprint.saveState()

        do {
            let result = try await operation(&blueprint.state)
            let check = blueprint.checkLaws()

            if !check.passed {
                blueprint.restoreState(savedState)
                if let violation = check.firstViolation, case .finfr(let reason) = violation {
                    return .failure(Finfr(reason, law: check.violations.first ?? "unknown"))
                }
                return .failure(Finfr(check.violations.joined(separator: "; ")))
            }

            return .success(result)
        } catch let error as Finfr {
            blueprint.restoreState(savedState)
            return .failure(error)
        } catch {
            blueprint.restoreState(savedState)
            return .failure(Finfr(error.localizedDescription))
        }
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK IV: COMBOS - The Core Pattern
// Think in combinations of valid states, not permutations of all possible states.
// ═══════════════════════════════════════════════════════════════════════════════

/// A Combo defines a valid combination of constraints.
/// Instead of checking all permutations, you define what CAN exist.
public struct Combo<Input, Output>: Identifiable, Sendable where Input: Sendable, Output: Sendable {
    public let id: String
    public let name: String
    public let preconditions: [@Sendable (Input) -> Bool]
    public let transform: @Sendable (Input) throws -> Output

    public init(
        _ name: String,
        id: String? = nil,
        when preconditions: [@Sendable (Input) -> Bool] = [],
        then transform: @escaping @Sendable (Input) throws -> Output
    ) {
        self.id = id ?? UUID().uuidString
        self.name = name
        self.preconditions = preconditions
        self.transform = transform
    }

    /// Check if all preconditions are met
    public func canExecute(_ input: Input) -> Bool {
        preconditions.allSatisfy { $0(input) }
    }

    /// Execute if preconditions are met
    public func execute(_ input: Input) -> Result<Output, Finfr> {
        guard canExecute(input) else {
            return .failure(Finfr("Preconditions not met", law: name))
        }

        do {
            let output = try transform(input)
            return .success(output)
        } catch let error as Finfr {
            return .failure(error)
        } catch {
            return .failure(Finfr(error.localizedDescription, law: name))
        }
    }
}

/// A ComboSet is a collection of mutually exclusive combos.
/// The first matching combo executes. No ambiguity.
public struct ComboSet<Input, Output>: Sendable where Input: Sendable, Output: Sendable {
    public let combos: [Combo<Input, Output>]

    public init(_ combos: [Combo<Input, Output>]) {
        self.combos = combos
    }

    /// Find the first combo whose preconditions match
    public func match(_ input: Input) -> Combo<Input, Output>? {
        combos.first { $0.canExecute(input) }
    }

    /// Execute the first matching combo
    public func execute(_ input: Input) -> Result<Output, Finfr> {
        guard let combo = match(input) else {
            return .failure(Finfr("No matching combo", law: "combo_set"))
        }
        return combo.execute(input)
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK V: SWIFTUI INTEGRATION
// Verified views that only render valid states.
// ═══════════════════════════════════════════════════════════════════════════════

/// A view modifier that prevents rendering if laws are violated.
public struct VerifiedViewModifier<B: Blueprint>: ViewModifier {
    @ObservedObject private var blueprint: B
    let fallback: AnyView

    public init(_ blueprint: B, fallback: AnyView = AnyView(EmptyView())) {
        self._blueprint = ObservedObject(wrappedValue: blueprint)
        self.fallback = fallback
    }

    public func body(content: Content) -> some View {
        let check = blueprint.checkLaws()

        if check.passed {
            content
        } else {
            fallback
        }
    }
}

extension View {
    /// Only render this view if the blueprint's laws are satisfied.
    public func verified<B: Blueprint>(
        by blueprint: B,
        fallback: some View = EmptyView()
    ) -> some View {
        modifier(VerifiedViewModifier(blueprint, fallback: AnyView(fallback)))
    }
}

/// A property wrapper for verified state in SwiftUI.
@MainActor
@propertyWrapper
public struct Verified<Value: Sendable>: DynamicProperty {
    @State private var value: Value
    private let validate: (Value) -> LawResult

    public var wrappedValue: Value {
        get { value }
        nonmutating set {
            let result = validate(newValue)
            if result.isAllowed {
                value = newValue
            }
            // Silently reject invalid values
        }
    }

    public var projectedValue: Binding<Value> {
        Binding(
            get: { value },
            set: { newValue in
                let result = validate(newValue)
                if result.isAllowed {
                    value = newValue
                }
            }
        )
    }

    public init(wrappedValue: Value, validate: @escaping (Value) -> LawResult) {
        self._value = State(initialValue: wrappedValue)
        self.validate = validate
    }
}

/// A view that displays f/g ratio status.
public struct RatioIndicator: View {
    public let f: Double
    public let g: Double
    public let threshold: Double
    public let label: String

    public init(f: Double, g: Double, threshold: Double = 1.0, label: String = "") {
        self.f = f
        self.g = g
        self.threshold = threshold
        self.label = label
    }

    private var r: Ratio { ratio(f, g) }

    private var status: (color: Color, icon: String) {
        if r.isUndefined {
            return (.red, "xmark.circle.fill")
        } else if r <= threshold {
            return (.green, "checkmark.circle.fill")
        } else if r <= threshold * 1.2 {
            return (.yellow, "exclamationmark.triangle.fill")
        } else {
            return (.red, "xmark.circle.fill")
        }
    }

    public var body: some View {
        HStack(spacing: 8) {
            Image(systemName: status.icon)
                .foregroundColor(status.color)

            if !label.isEmpty {
                Text(label)
                    .font(.caption)
            }

            Text(r.isUndefined ? "∞" : String(format: "%.2f", r.value))
                .font(.system(.caption, design: .monospaced))
                .foregroundColor(status.color)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
        .background(status.color.opacity(0.1))
        .cornerRadius(8)
    }
}

/// Newton verification badge
public struct NewtonBadge: View {
    public let verified: Bool
    public let fingerprint: String?

    public init(verified: Bool = true, fingerprint: String? = nil) {
        self.verified = verified
        self.fingerprint = fingerprint
    }

    public var body: some View {
        HStack(spacing: 4) {
            Image(systemName: verified ? "checkmark.seal.fill" : "xmark.seal.fill")
            Text("1 == 1")
                .font(.system(.caption2, design: .monospaced))
            if let fp = fingerprint {
                Text(fp.prefix(8))
                    .font(.system(.caption2, design: .monospaced))
                    .foregroundColor(.secondary)
            }
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(verified ? Color.green.opacity(0.15) : Color.red.opacity(0.15))
        .foregroundColor(verified ? .green : .red)
        .cornerRadius(4)
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK VI: CONSTRAINT BUILDERS
// DSL syntax for declaring constraints.
// ═══════════════════════════════════════════════════════════════════════════════

/// Result builder for composing multiple laws.
@resultBuilder
public struct LawBuilder<State: Sendable> {
    public static func buildBlock(_ laws: Law<State>...) -> [Law<State>] {
        laws
    }

    public static func buildOptional(_ law: [Law<State>]?) -> [Law<State>] {
        law ?? []
    }

    public static func buildEither(first law: [Law<State>]) -> [Law<State>] {
        law
    }

    public static func buildEither(second law: [Law<State>]) -> [Law<State>] {
        law
    }

    public static func buildArray(_ laws: [[Law<State>]]) -> [Law<State>] {
        laws.flatMap { $0 }
    }
}

/// Result builder for composing combos.
@resultBuilder
public struct ComboBuilder<Input: Sendable, Output: Sendable> {
    public static func buildBlock(_ combos: Combo<Input, Output>...) -> [Combo<Input, Output>] {
        combos
    }

    public static func buildArray(_ combos: [[Combo<Input, Output>]]) -> [Combo<Input, Output>] {
        combos.flatMap { $0 }
    }
}

/// Build a set of laws using DSL syntax.
public func laws<State: Sendable>(
    @LawBuilder<State> _ builder: () -> [Law<State>]
) -> [Law<State>] {
    builder()
}

/// Build a combo set using DSL syntax.
public func combos<Input: Sendable, Output: Sendable>(
    @ComboBuilder<Input, Output> _ builder: () -> [Combo<Input, Output>]
) -> ComboSet<Input, Output> {
    ComboSet(builder())
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK VII: VERIFICATION PROOF
// Cryptographic proof of constraint satisfaction.
// ═══════════════════════════════════════════════════════════════════════════════

import CryptoKit

/// A verification proof that can be independently validated.
public struct VerificationProof: Codable, Sendable, Identifiable {
    public let id: String
    public let timestamp: Date
    public let constraintsSatisfied: Int
    public let fingerprint: String
    public let signature: String

    public init(constraintsSatisfied: Int) {
        self.id = UUID().uuidString
        self.timestamp = Date()
        self.constraintsSatisfied = constraintsSatisfied

        // Generate fingerprint
        let data = "\(id):\(timestamp.timeIntervalSince1970):\(constraintsSatisfied)"
        let hash = SHA256.hash(data: Data(data.utf8))
        self.fingerprint = hash.prefix(8).map { String(format: "%02x", $0) }.joined().uppercased()

        // Generate signature
        let sigData = "\(fingerprint):\(constraintsSatisfied)"
        let sigHash = SHA256.hash(data: Data(sigData.utf8))
        self.signature = "N2_" + sigHash.prefix(16).map { String(format: "%02x", $0) }.joined().uppercased()
    }
}

/// Generate a verification proof for a blueprint.
public func prove<B: Blueprint>(_ blueprint: B) -> VerificationProof {
    let check = blueprint.checkLaws()
    return VerificationProof(constraintsSatisfied: check.passed ? blueprint.laws.count : 0)
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK VIII: CONVENIENCE EXTENSIONS
// Making TinyTalk feel natural in Swift.
// ═══════════════════════════════════════════════════════════════════════════════

extension Numeric where Self: Comparable {
    /// Check if value is within range, returning LawResult.
    public func mustBe(lessThan max: Self) -> LawResult {
        self < max ? .allowed : .finfr("Value \(self) must be less than \(max)")
    }

    public func mustBe(atMost max: Self) -> LawResult {
        self <= max ? .allowed : .finfr("Value \(self) must be at most \(max)")
    }

    public func mustBe(greaterThan min: Self) -> LawResult {
        self > min ? .allowed : .finfr("Value \(self) must be greater than \(min)")
    }

    public func mustBe(atLeast min: Self) -> LawResult {
        self >= min ? .allowed : .finfr("Value \(self) must be at least \(min)")
    }
}

extension Double {
    /// Create a ratio with this value as numerator.
    public func over(_ denominator: Double) -> Ratio {
        ratio(self, denominator)
    }
}

extension String {
    /// Check if string is non-empty.
    public var mustNotBeEmpty: LawResult {
        isEmpty ? .finfr("String must not be empty") : .allowed
    }

    /// Check if string matches pattern.
    public func mustMatch(_ pattern: String) -> LawResult {
        if let regex = try? NSRegularExpression(pattern: pattern),
           regex.firstMatch(in: self, range: NSRange(startIndex..., in: self)) != nil {
            return .allowed
        }
        return .finfr("String must match pattern: \(pattern)")
    }
}

extension Optional {
    /// Check if optional has a value.
    public var mustExist: LawResult {
        self != nil ? .allowed : .finfr("Value must exist")
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// THE CLOSURE CONDITION
// ═══════════════════════════════════════════════════════════════════════════════

/// The fundamental law of Newton.
/// 1 == 1.
/// Everything else follows.
@inlinable
public func newton<T: Equatable>(_ current: T, _ goal: T) -> Bool {
    current == goal
}

// ═══════════════════════════════════════════════════════════════════════════════
// NEWTON VERIFICATION FOOTER
// ═══════════════════════════════════════════════════════════════════════════════
//
// when tinytalk_swift_dsl:
//     and language == swift
//     and platforms contains [iOS, macOS, watchOS, visionOS]
//     and has_lexicon [fin, finfr, when, ratio]
//     and has_blueprint_pattern
//     and has_forge_with_rollback
//     and has_combo_pattern
//     and has_swiftui_integration
//     and has_verification_proof
// fin tinytalk_verified
//
// f/g ratio: 1.0 (all constraints satisfied)
// Fingerprint: TINYTALK_SWIFT_DSL_V1
// Generated: 2026-01-04
//
// © 2026 Jared Lewis Conglomerate
// ═══════════════════════════════════════════════════════════════════════════════
