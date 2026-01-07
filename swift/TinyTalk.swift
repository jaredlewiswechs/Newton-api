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

import Foundation
import SwiftUI
import Combine
import CryptoKit

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK I: THE LEXICON
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

/// Declares a constraint check. If condition is true and result is fin/finfr, throws.
/// - Parameters:
///   - condition: The boolean condition to evaluate
///   - then: What happens if condition is true (fin or finfr)
/// - Returns: The condition result for chaining
@discardableResult
public func when(_ condition: Bool, then result: LawResult = .allowed) throws -> Bool {
    guard condition else { return false }

    switch result {
    case .finfr(let reason):
        throw Finfr(reason)
    case .fin(let reason):
        throw Fin(reason)
    case .allowed:
        return true
    }
}

/// Convenience for finfr declaration
public func finfr(_ reason: String = "State cannot exist") -> LawResult { .finfr(reason) }

/// Convenience for fin declaration
public func fin(_ reason: String = "Closure reached") -> LawResult { .fin(reason) }

// MARK: - The Ratio Type (f/g)

public struct Ratio: Sendable, CustomStringConvertible {
    public let f: Double
    public let g: Double
    public let epsilon: Double

    public var isUndefined: Bool { abs(g) < epsilon }

    public var value: Double {
        guard !isUndefined else { return f >= 0 ? .infinity : -.infinity }
        return f / g
    }

    public init(f: Double, g: Double, epsilon: Double = 1e-9) {
        self.f = f
        self.g = g
        self.epsilon = epsilon
    }

    public var description: String {
        if isUndefined { return "Ratio(f=\(f), g=\(g), undefined)" }
        return "Ratio(f=\(f), g=\(g), value=\(String(format: "%.4f", value)))"
    }

    // Comparisons against thresholds (Double)
    public static func < (lhs: Ratio, rhs: Double) -> Bool {
        guard !lhs.isUndefined else { return false }
        return lhs.value < rhs
    }

    public static func <= (lhs: Ratio, rhs: Double) -> Bool {
        guard !lhs.isUndefined else { return false }
        return lhs.value <= rhs
    }

    public static func > (lhs: Ratio, rhs: Double) -> Bool {
        // Undefined ratio is treated as "fails safe" (too large)
        if lhs.isUndefined { return true }
        return lhs.value > rhs
    }

    public static func >= (lhs: Ratio, rhs: Double) -> Bool {
        if lhs.isUndefined { return true }
        return lhs.value >= rhs
    }

    public static func == (lhs: Ratio, rhs: Double) -> Bool {
        guard !lhs.isUndefined else { return false }
        return abs(lhs.value - rhs) < lhs.epsilon
    }
}

public func ratio(_ f: Double, _ g: Double) -> Ratio { Ratio(f: f, g: g) }

public func finfrIfUndefined(_ f: Double, _ g: Double) throws {
    let r = ratio(f, g)
    if r.isUndefined {
        throw Finfr("Ratio is undefined (denominator ≈ 0)", law: "ratio_undefined")
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK II: THE BLUEPRINT
// ═══════════════════════════════════════════════════════════════════════════════

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

/// Result of checking laws against a state.
public struct LawCheckResult: Sendable {
    public let passed: Bool
    public let violations: [String]
    public let firstViolation: LawResult?
    public let firstLawName: String?

    public static let success = LawCheckResult(
        passed: true,
        violations: [],
        firstViolation: nil,
        firstLawName: nil
    )

    public static func failure(
        violations: [String],
        first: LawResult,
        firstLawName: String
    ) -> LawCheckResult {
        LawCheckResult(
            passed: false,
            violations: violations,
            firstViolation: first,
            firstLawName: firstLawName
        )
    }
}

/// A Blueprint defines constraint-governed state.
/// NOTE: Use ObservableObject for SwiftUI integration.
public protocol Blueprint: AnyObject, ObservableObject {
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
    /// Default save/restore for value-type state (structs).
    public func saveState() -> State { state }
    public func restoreState(_ saved: State) { state = saved }

    /// Check all laws against current state.
    public func checkLaws() -> LawCheckResult {
        var violations: [String] = []

        for law in laws {
            let result = law.evaluate(state)
            switch result {
            case .allowed:
                continue
            case .fin(let reason):
                violations.append("\(law.name): \(reason)")
                return .failure(violations: violations, first: result, firstLawName: law.name)
            case .finfr(let reason):
                violations.append("\(law.name): \(reason)")
                return .failure(violations: violations, first: result, firstLawName: law.name)
            }
        }

        return .success
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK III: THE FORGE
// ═══════════════════════════════════════════════════════════════════════════════

/// A Forge is an atomic operation that mutates state with verification.
/// If any law is violated after the operation, state is rolled back.
@MainActor
public struct Forge<B: Blueprint> {
    public let blueprint: B

    public init(_ blueprint: B) { self.blueprint = blueprint }

    /// Execute an operation with automatic rollback on law violation.
    @discardableResult
    public func execute<T>(
        _ operation: @escaping (inout B.State) throws -> T
    ) -> Result<T, Finfr> {
        let savedState = blueprint.saveState()

        do {
            // Mutate locally (avoids inout-to-protocol-property pitfalls)
            var next = blueprint.state
            let result = try operation(&next)
            blueprint.state = next

            // Verify
            let check = blueprint.checkLaws()
            if !check.passed {
                blueprint.restoreState(savedState)

                let lawName = check.firstLawName ?? "unknown"
                let reason = check.violations.joined(separator: "; ")

                if let v = check.firstViolation {
                    switch v {
                    case .finfr(let msg):
                        return .failure(Finfr(msg, law: lawName))
                    case .fin(let msg):
                        return .failure(Finfr("fin: \(msg)", law: lawName))
                    case .allowed:
                        break
                    }
                }
                return .failure(Finfr(reason, law: lawName))
            }

            return .success(result)

        } catch let error as Finfr {
            blueprint.restoreState(savedState)
            return .failure(error)
        } catch let error as Fin {
            blueprint.restoreState(savedState)
            return .failure(Finfr("fin: \(error.reason)", law: error.lawName))
        } catch {
            blueprint.restoreState(savedState)
            return .failure(Finfr(error.localizedDescription, law: "unknown"))
        }
    }

    /// Execute with async operation
    @discardableResult
    public func executeAsync<T>(
        _ operation: @escaping (inout B.State) async throws -> T
    ) async -> Result<T, Finfr> {
        let savedState = blueprint.saveState()

        do {
            var next = blueprint.state
            let result = try await operation(&next)
            blueprint.state = next

            let check = blueprint.checkLaws()
            if !check.passed {
                blueprint.restoreState(savedState)

                let lawName = check.firstLawName ?? "unknown"
                let reason = check.violations.joined(separator: "; ")

                if let v = check.firstViolation {
                    switch v {
                    case .finfr(let msg):
                        return .failure(Finfr(msg, law: lawName))
                    case .fin(let msg):
                        return .failure(Finfr("fin: \(msg)", law: lawName))
                    case .allowed:
                        break
                    }
                }
                return .failure(Finfr(reason, law: lawName))
            }

            return .success(result)

        } catch let error as Finfr {
            blueprint.restoreState(savedState)
            return .failure(error)
        } catch let error as Fin {
            blueprint.restoreState(savedState)
            return .failure(Finfr("fin: \(error.reason)", law: error.lawName))
        } catch {
            blueprint.restoreState(savedState)
            return .failure(Finfr(error.localizedDescription, law: "unknown"))
        }
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK IV: COMBOS
// ═══════════════════════════════════════════════════════════════════════════════

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

    public func canExecute(_ input: Input) -> Bool {
        preconditions.allSatisfy { $0(input) }
    }

    public func execute(_ input: Input) -> Result<Output, Finfr> {
        guard canExecute(input) else {
            return .failure(Finfr("Preconditions not met", law: name))
        }

        do {
            let output = try transform(input)
            return .success(output)
        } catch let error as Finfr {
            return .failure(error)
        } catch let error as Fin {
            return .failure(Finfr("fin: \(error.reason)", law: error.lawName))
        } catch {
            return .failure(Finfr(error.localizedDescription, law: name))
        }
    }
}

public struct ComboSet<Input, Output>: Sendable where Input: Sendable, Output: Sendable {
    public let combos: [Combo<Input, Output>]

    public init(_ combos: [Combo<Input, Output>]) {
        self.combos = combos
    }

    public func match(_ input: Input) -> Combo<Input, Output>? {
        combos.first { $0.canExecute(input) }
    }

    public func execute(_ input: Input) -> Result<Output, Finfr> {
        guard let combo = match(input) else {
            return .failure(Finfr("No matching combo", law: "combo_set"))
        }
        return combo.execute(input)
    }
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK V: SWIFTUI INTEGRATION
// ═══════════════════════════════════════════════════════════════════════════════

public struct VerifiedViewModifier<B: Blueprint>: ViewModifier {
    @ObservedObject private var blueprint: B
    let fallback: AnyView

    public init(_ blueprint: B, fallback: AnyView = AnyView(EmptyView())) {
        self._blueprint = ObservedObject(wrappedValue: blueprint)
        self.fallback = fallback
    }

    public func body(content: Content) -> some View {
        let check = blueprint.checkLaws()
        return Group {
            if check.passed { content }
            else { fallback }
        }
    }
}

extension View {
    public func verified<B: Blueprint>(
        by blueprint: B,
        fallback: some View = EmptyView()
    ) -> some View {
        modifier(VerifiedViewModifier(blueprint, fallback: AnyView(fallback)))
    }
}

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
// ═══════════════════════════════════════════════════════════════════════════════

@resultBuilder
public struct LawBuilder<State: Sendable> {
    public static func buildBlock(_ laws: Law<State>...) -> [Law<State>] { laws }
    public static func buildOptional(_ law: [Law<State>]?) -> [Law<State>] { law ?? [] }
    public static func buildEither(first law: [Law<State>]) -> [Law<State>] { law }
    public static func buildEither(second law: [Law<State>]) -> [Law<State>] { law }
    public static func buildArray(_ laws: [[Law<State>]]) -> [Law<State>] { laws.flatMap { $0 } }
}

@resultBuilder
public struct ComboBuilder<Input: Sendable, Output: Sendable> {
    public static func buildBlock(_ combos: Combo<Input, Output>...) -> [Combo<Input, Output>] { combos }
    public static func buildArray(_ combos: [[Combo<Input, Output>]]) -> [Combo<Input, Output>] { combos.flatMap { $0 } }
}

public func laws<State: Sendable>(@LawBuilder<State> _ builder: () -> [Law<State>]) -> [Law<State>] {
    builder()
}

public func combos<Input: Sendable, Output: Sendable>(
    @ComboBuilder<Input, Output> _ builder: () -> [Combo<Input, Output>]
) -> ComboSet<Input, Output> {
    ComboSet(builder())
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK VII: VERIFICATION PROOF
// ═══════════════════════════════════════════════════════════════════════════════

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

        let data = "\(id):\(timestamp.timeIntervalSince1970):\(constraintsSatisfied)"
        let hash = SHA256.hash(data: Data(data.utf8))
        self.fingerprint = hash.prefix(8).map { String(format: "%02x", $0) }.joined().uppercased()

        let sigData = "\(fingerprint):\(constraintsSatisfied)"
        let sigHash = SHA256.hash(data: Data(sigData.utf8))
        self.signature = "N2_" + sigHash.prefix(16).map { String(format: "%02x", $0) }.joined().uppercased()
    }
}

public func prove<B: Blueprint>(_ blueprint: B) -> VerificationProof {
    let check = blueprint.checkLaws()
    return VerificationProof(constraintsSatisfied: check.passed ? blueprint.laws.count : 0)
}

// MARK: - ═══════════════════════════════════════════════════════════════════════
// BOOK VIII: CONVENIENCE EXTENSIONS
// ═══════════════════════════════════════════════════════════════════════════════

extension Numeric where Self: Comparable {
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
    public func over(_ denominator: Double) -> Ratio { ratio(self, denominator) }
}

extension String {
    public var mustNotBeEmpty: LawResult {
        isEmpty ? .finfr("String must not be empty") : .allowed
    }

    public func mustMatch(_ pattern: String) -> LawResult {
        if let regex = try? NSRegularExpression(pattern: pattern),
           regex.firstMatch(in: self, range: NSRange(startIndex..., in: self)) != nil {
            return .allowed
        }
        return .finfr("String must match pattern: \(pattern)")
    }
}

extension Optional {
    public var mustExist: LawResult {
        self != nil ? .allowed : .finfr("Value must exist")
    }
}

// MARK: - THE CLOSURE CONDITION

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
// Fingerprint: TINYTALK_SWIFT_DSL_V2
// Generated: 2026-01-07
//
// FIXES IN V2 (2026):
// - Observable → ObservableObject (no Observable protocol exists)
// - import CryptoKit moved to top
// - Forge.execute uses local var copy to avoid exclusivity issues
// - LawCheckResult tracks firstLawName separately
//
// © 2026 Jared Lewis Conglomerate
// ═══════════════════════════════════════════════════════════════════════════════
