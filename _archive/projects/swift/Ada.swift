//
//  Ada.swift
//  Newton Intent-to-Transform Compiler
//
//  Created by Jared Nashon Lewis
//  Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company
//
//  Copyright © 2026 Jared Lewis. All rights reserved.
//
//  Ada: The bridge between human intent and Newton's deterministic execution.
//
//  Architecture:
//    Human Intent → Ada (LLM-powered parser) → Newton Validator → Newton Executor
//    The LLM can hallucinate. Newton only accepts what works.
//
//  "The intent is the dream. The transform is the plan. Newton is the reality."
//

import Foundation

// MARK: - Core Data Structures

/// A Transform is a named operation with preconditions and effects.
/// Transforms are the atoms of Newton computation - discrete, verifiable state changes.
struct Transform: Codable, Equatable, Hashable {
    /// Unique identifier for this transform
    let id: UUID

    /// Human-readable name (e.g., "send_money", "approve_expense")
    let name: String

    /// Description of what this transform does
    let description: String

    /// State requirements that must be true before execution
    /// Key: state variable name, Value: required value or constraint
    let preconditions: [String: String]

    /// State changes that result from execution
    /// Key: state variable name, Value: new value
    let effects: [String: String]

    /// Domain this transform belongs to (financial, health, etc.)
    let domain: String

    /// Cost in Newton compute units (f/g ratio impact)
    let cost: Double

    init(name: String, description: String, preconditions: [String: String], effects: [String: String], domain: String = "general", cost: Double = 1.0) {
        self.id = UUID()
        self.name = name
        self.description = description
        self.preconditions = preconditions
        self.effects = effects
        self.domain = domain
        self.cost = cost
    }
}

/// A Goal represents a desired end state.
/// Goals are measured by distance from target - when distance = 0, goal is achieved.
struct Goal: Codable, Equatable {
    /// Human-readable description of the goal
    let description: String

    /// Target state to achieve
    /// Key: state variable name, Value: desired value
    let target: [String: String]

    /// Priority weight (higher = more important)
    let priority: Double

    /// Maximum transforms allowed to reach this goal
    let maxSteps: Int

    init(description: String, target: [String: String], priority: Double = 1.0, maxSteps: Int = 10) {
        self.description = description
        self.target = target
        self.priority = priority
        self.maxSteps = maxSteps
    }

    /// Calculate distance from current state to goal
    /// Returns 0 when goal is fully satisfied
    func distance(from state: [String: String]) -> Int {
        var mismatches = 0
        for (key, targetValue) in target {
            if state[key] != targetValue {
                mismatches += 1
            }
        }
        return mismatches
    }

    /// Check if goal is satisfied by current state
    func isSatisfied(by state: [String: String]) -> Bool {
        return distance(from: state) == 0
    }
}

/// An IntentProposal is what Ada generates from human language.
/// It's a hypothesis about what the user wants - Newton validates it.
struct IntentProposal: Codable {
    /// The parsed goal from user intent
    let goal: Goal

    /// Proposed sequence of transforms to achieve the goal
    let transforms: [Transform]

    /// Confidence score from Ada's parsing (0.0 - 1.0)
    let confidence: Double

    /// Original user intent string
    let originalIntent: String

    /// Timestamp of proposal
    let timestamp: Date

    /// Warnings or notes from parsing
    let warnings: [String]

    init(goal: Goal, transforms: [Transform], confidence: Double, originalIntent: String, warnings: [String] = []) {
        self.goal = goal
        self.transforms = transforms
        self.confidence = confidence
        self.originalIntent = originalIntent
        self.timestamp = Date()
        self.warnings = warnings
    }
}

// MARK: - Verification Results

/// Result of Newton validation
enum ValidationResult {
    case valid(signature: String, fgRatio: Double)
    case invalid(reason: String, constraint: String)
    case ambiguous(options: [IntentProposal])

    var isValid: Bool {
        if case .valid = self { return true }
        return false
    }
}

/// Result of transform execution
struct ExecutionResult: Codable {
    let success: Bool
    let newState: [String: String]
    let ledgerEntry: String
    let signature: String
    let executionTime: TimeInterval
    let fgRatio: Double

    /// When g approaches 0, we have ontological death (finfr)
    var isFinfr: Bool {
        return fgRatio.isInfinite || fgRatio > 1000000
    }
}

// MARK: - Newton Validator

/// The Gatekeeper: Validates transforms against Newton constraints.
/// No transform executes without passing through the validator.
class NewtonValidator {

    /// Registered constraints by domain
    private var constraints: [String: [[String: Any]]] = [:]

    /// Locked baseline statistics for robust verification
    private var lockedBaselines: [String: (median: Double, mad: Double)] = [:]

    /// Newton API endpoint
    private let apiEndpoint: URL

    init(apiEndpoint: URL = URL(string: "http://localhost:8000")!) {
        self.apiEndpoint = apiEndpoint
        loadDefaultConstraints()
    }

    /// Load default constraints from Newton
    private func loadDefaultConstraints() {
        // Financial constraints
        constraints["financial"] = [
            ["field": "amount", "operator": "lt", "value": 10000, "reason": "Amount exceeds single-transaction limit"],
            ["field": "currency", "operator": "in", "value": ["USD", "EUR", "GBP", "JPY", "CAD"], "reason": "Unsupported currency"],
            ["field": "fraud_score", "operator": "lt", "value": 0.7, "reason": "High fraud risk detected"]
        ]

        // Health constraints
        constraints["health"] = [
            ["field": "phi_exposed", "operator": "eq", "value": false, "reason": "PHI must not be exposed"],
            ["field": "hipaa_compliant", "operator": "eq", "value": true, "reason": "HIPAA compliance required"]
        ]

        // General constraints
        constraints["general"] = [
            ["field": "harm_intent", "operator": "eq", "value": false, "reason": "Harmful intent detected"],
            ["field": "verified_identity", "operator": "eq", "value": true, "reason": "Identity verification required"]
        ]
    }

    /// Validate a transform against Newton constraints
    /// Returns: ValidationResult indicating if transform is safe to execute
    func validate(_ transform: Transform, currentState: [String: String]) -> ValidationResult {

        // Check preconditions are satisfied
        for (key, required) in transform.preconditions {
            guard let actual = currentState[key] else {
                return .invalid(
                    reason: "Missing precondition: \(key)",
                    constraint: "precondition_check"
                )
            }
            if actual != required {
                return .invalid(
                    reason: "Precondition failed: \(key) is '\(actual)', requires '\(required)'",
                    constraint: "precondition_check"
                )
            }
        }

        // Check domain-specific constraints
        if let domainConstraints = constraints[transform.domain] {
            for constraint in domainConstraints {
                if let field = constraint["field"] as? String,
                   let op = constraint["operator"] as? String,
                   let reason = constraint["reason"] as? String {

                    // Check if this constraint applies to any effect
                    if let effectValue = transform.effects[field] {
                        let passes = evaluateConstraint(
                            value: effectValue,
                            operator: op,
                            target: constraint["value"]
                        )
                        if !passes {
                            return .invalid(reason: reason, constraint: field)
                        }
                    }
                }
            }
        }

        // Calculate f/g ratio
        let forge = calculateForge(transform)
        let ground = calculateGround(transform, state: currentState)

        // Guard against division by zero (ontological death)
        guard ground > 0 else {
            return .invalid(
                reason: "Ground is zero - ontological death (finfr)",
                constraint: "fg_ratio"
            )
        }

        let fgRatio = forge / ground

        // Generate cryptographic signature
        let signature = generateSignature(transform: transform, fgRatio: fgRatio)

        return .valid(signature: signature, fgRatio: fgRatio)
    }

    /// Validate an entire intent proposal
    func validate(_ proposal: IntentProposal, currentState: [String: String]) -> ValidationResult {
        var state = currentState

        for transform in proposal.transforms {
            let result = validate(transform, currentState: state)

            switch result {
            case .invalid:
                return result
            case .ambiguous:
                return result
            case .valid:
                // Apply effects to state for next transform
                for (key, value) in transform.effects {
                    state[key] = value
                }
            }
        }

        // Verify goal is achievable
        if !proposal.goal.isSatisfied(by: state) {
            return .invalid(
                reason: "Transforms do not achieve goal. Distance: \(proposal.goal.distance(from: state))",
                constraint: "goal_satisfaction"
            )
        }

        // Calculate overall f/g ratio
        let totalForge = proposal.transforms.reduce(0.0) { $0 + calculateForge($1) }
        let totalGround = proposal.transforms.reduce(0.0) { $0 + calculateGround($1, state: currentState) }

        guard totalGround > 0 else {
            return .invalid(reason: "Total ground is zero", constraint: "fg_ratio")
        }

        let signature = generateSignature(proposal: proposal)
        return .valid(signature: signature, fgRatio: totalForge / totalGround)
    }

    // MARK: - Private Helpers

    private func evaluateConstraint(value: String, operator op: String, target: Any?) -> Bool {
        switch op {
        case "eq":
            if let targetStr = target as? String {
                return value == targetStr
            } else if let targetBool = target as? Bool {
                return (value == "true") == targetBool
            }
        case "neq":
            if let targetStr = target as? String {
                return value != targetStr
            }
        case "lt":
            if let targetNum = target as? Double, let valueNum = Double(value) {
                return valueNum < targetNum
            }
        case "lte":
            if let targetNum = target as? Double, let valueNum = Double(value) {
                return valueNum <= targetNum
            }
        case "gt":
            if let targetNum = target as? Double, let valueNum = Double(value) {
                return valueNum > targetNum
            }
        case "gte":
            if let targetNum = target as? Double, let valueNum = Double(value) {
                return valueNum >= targetNum
            }
        case "in":
            if let targetArray = target as? [String] {
                return targetArray.contains(value)
            }
        case "contains":
            if let targetStr = target as? String {
                return value.contains(targetStr)
            }
        case "matches":
            if let pattern = target as? String {
                return value.range(of: pattern, options: .regularExpression) != nil
            }
        default:
            break
        }
        return true // Unknown operator passes by default
    }

    /// Calculate forge (what you want) from transform
    private func calculateForge(_ transform: Transform) -> Double {
        // Forge is based on the complexity and impact of effects
        let effectComplexity = Double(transform.effects.count)
        return effectComplexity * transform.cost
    }

    /// Calculate ground (what reality allows) from transform and state
    private func calculateGround(_ transform: Transform, state: [String: String]) -> Double {
        // Ground is based on satisfied preconditions and resource availability
        var ground = 1.0

        for (key, required) in transform.preconditions {
            if state[key] == required {
                ground += 1.0
            }
        }

        // Domain-specific grounding
        if transform.domain == "financial" {
            if let balance = state["balance"], let balanceNum = Double(balance) {
                ground += min(balanceNum / 1000.0, 10.0) // Cap contribution
            }
        }

        return ground
    }

    /// Generate cryptographic signature for verified transform
    private func generateSignature(transform: Transform, fgRatio: Double) -> String {
        let data = "\(transform.id):\(transform.name):\(fgRatio):\(Date().timeIntervalSince1970)"
        return data.data(using: .utf8)!
            .base64EncodedString()
            .prefix(16)
            .uppercased()
    }

    private func generateSignature(proposal: IntentProposal) -> String {
        let data = "\(proposal.originalIntent):\(proposal.confidence):\(proposal.timestamp.timeIntervalSince1970)"
        return data.data(using: .utf8)!
            .base64EncodedString()
            .prefix(16)
            .uppercased()
    }
}

// MARK: - Newton Executor

/// Executes validated transforms and writes to the ledger.
/// Only accepts transforms that have passed NewtonValidator.
class NewtonExecutor {

    /// The immutable ledger of all executions
    private var ledger: [LedgerEntry] = []

    /// Current world state
    private(set) var state: [String: String] = [:]

    /// Validator reference
    private let validator: NewtonValidator

    struct LedgerEntry: Codable {
        let id: UUID
        let timestamp: Date
        let transformName: String
        let signature: String
        let previousStateHash: String
        let newStateHash: String
        let fgRatio: Double
    }

    init(validator: NewtonValidator, initialState: [String: String] = [:]) {
        self.validator = validator
        self.state = initialState
    }

    /// Execute a validated transform
    /// Precondition: Transform must have passed validation
    func execute(_ transform: Transform, validationSignature: String, fgRatio: Double) -> ExecutionResult {
        let startTime = Date()

        // Double-check validation (defense in depth)
        let revalidation = validator.validate(transform, currentState: state)
        guard case .valid = revalidation else {
            return ExecutionResult(
                success: false,
                newState: state,
                ledgerEntry: "",
                signature: "",
                executionTime: Date().timeIntervalSince(startTime),
                fgRatio: fgRatio
            )
        }

        // Capture previous state hash
        let previousHash = hashState(state)

        // Apply effects
        for (key, value) in transform.effects {
            state[key] = value
        }

        // Create ledger entry
        let entry = LedgerEntry(
            id: UUID(),
            timestamp: Date(),
            transformName: transform.name,
            signature: validationSignature,
            previousStateHash: previousHash,
            newStateHash: hashState(state),
            fgRatio: fgRatio
        )

        // Append to immutable ledger
        ledger.append(entry)

        return ExecutionResult(
            success: true,
            newState: state,
            ledgerEntry: entry.id.uuidString,
            signature: validationSignature,
            executionTime: Date().timeIntervalSince(startTime),
            fgRatio: fgRatio
        )
    }

    /// Execute an entire proposal
    func execute(_ proposal: IntentProposal) -> [ExecutionResult] {
        var results: [ExecutionResult] = []

        // Validate entire proposal first
        let validation = validator.validate(proposal, currentState: state)
        guard case .valid(let signature, let fgRatio) = validation else {
            return []
        }

        // Execute each transform
        for transform in proposal.transforms {
            let result = execute(transform, validationSignature: signature, fgRatio: fgRatio)
            results.append(result)

            if !result.success {
                break // Stop on first failure
            }
        }

        return results
    }

    /// Get ledger entries (read-only)
    func getLedger() -> [LedgerEntry] {
        return ledger
    }

    /// Hash state for ledger integrity
    private func hashState(_ state: [String: String]) -> String {
        let sorted = state.sorted { $0.key < $1.key }
        let data = sorted.map { "\($0.key)=\($0.value)" }.joined(separator: ";")
        return data.data(using: .utf8)!
            .base64EncodedString()
            .prefix(12)
            .uppercased()
    }
}

// MARK: - Ada Intent Parser

/// Rule-based fallback parser for when LLM is unavailable.
/// Handles common intent patterns without external API.
class AdaIntentParser {

    /// Known transform templates
    private var templates: [String: Transform] = [:]

    init() {
        loadTemplates()
    }

    private func loadTemplates() {
        // Financial transforms
        templates["send_money"] = Transform(
            name: "send_money",
            description: "Transfer funds from one account to another",
            preconditions: ["authenticated": "true", "has_balance": "true"],
            effects: ["transfer_initiated": "true"],
            domain: "financial"
        )

        templates["approve_expense"] = Transform(
            name: "approve_expense",
            description: "Approve an expense report",
            preconditions: ["is_manager": "true", "expense_submitted": "true"],
            effects: ["expense_approved": "true"],
            domain: "financial"
        )

        // General transforms
        templates["create_document"] = Transform(
            name: "create_document",
            description: "Create a new document",
            preconditions: ["authenticated": "true"],
            effects: ["document_created": "true"],
            domain: "general"
        )

        templates["share_access"] = Transform(
            name: "share_access",
            description: "Share access to a resource",
            preconditions: ["is_owner": "true"],
            effects: ["access_shared": "true"],
            domain: "general"
        )
    }

    /// Parse intent using rule-based matching
    func parse(_ intent: String) -> IntentProposal? {
        let lowercased = intent.lowercased()

        // Pattern matching for common intents
        if lowercased.contains("send") && lowercased.contains("money") {
            return createProposal(template: "send_money", intent: intent)
        }

        if lowercased.contains("approve") && lowercased.contains("expense") {
            return createProposal(template: "approve_expense", intent: intent)
        }

        if lowercased.contains("create") && lowercased.contains("document") {
            return createProposal(template: "create_document", intent: intent)
        }

        if lowercased.contains("share") {
            return createProposal(template: "share_access", intent: intent)
        }

        // No match found
        return nil
    }

    private func createProposal(template: String, intent: String) -> IntentProposal? {
        guard let transform = templates[template] else { return nil }

        let goal = Goal(
            description: "Complete: \(transform.description)",
            target: transform.effects
        )

        return IntentProposal(
            goal: goal,
            transforms: [transform],
            confidence: 0.7, // Lower confidence for rule-based
            originalIntent: intent,
            warnings: ["Parsed using rule-based fallback"]
        )
    }
}

// MARK: - Ada LLM Bridge

/// Connects to Claude API for intent understanding.
/// The LLM provides the flexibility; Newton provides the safety.
class AdaLLMBridge {

    private let apiKey: String
    private let model: String
    private let session: URLSession

    init(apiKey: String, model: String = "claude-sonnet-4-20250514") {
        self.apiKey = apiKey
        self.model = model
        self.session = URLSession.shared
    }

    /// Parse intent using Claude
    func parse(_ intent: String, context: [String: String] = [:]) async throws -> IntentProposal {
        let systemPrompt = """
        You are Ada, the intent parser for Newton - a verified computation system.

        Your job is to convert human intent into structured transforms that Newton can verify and execute.

        CRITICAL: You are NOT executing anything. You are proposing transforms for Newton to validate.
        Newton will reject any proposal that violates constraints. You cannot override Newton.

        Output format (JSON):
        {
            "goal": {
                "description": "Human-readable goal",
                "target": {"state_var": "desired_value"}
            },
            "transforms": [
                {
                    "name": "transform_name",
                    "description": "What this does",
                    "preconditions": {"var": "required_value"},
                    "effects": {"var": "new_value"},
                    "domain": "financial|health|general",
                    "cost": 1.0
                }
            ],
            "confidence": 0.0-1.0,
            "warnings": ["any concerns"]
        }

        Current context:
        \(context.map { "\($0.key): \($0.value)" }.joined(separator: "\n"))
        """

        let url = URL(string: "https://api.anthropic.com/v1/messages")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "x-api-key")
        request.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")

        let body: [String: Any] = [
            "model": model,
            "max_tokens": 1024,
            "system": systemPrompt,
            "messages": [
                ["role": "user", "content": intent]
            ]
        ]

        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw AdaError.apiError("Failed to get response from Claude")
        }

        // Parse Claude's response
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let content = json["content"] as? [[String: Any]],
              let text = content.first?["text"] as? String else {
            throw AdaError.parseError("Invalid response format")
        }

        // Extract JSON from response
        return try parseProposalJSON(text, originalIntent: intent)
    }

    private func parseProposalJSON(_ text: String, originalIntent: String) throws -> IntentProposal {
        // Find JSON in response
        guard let jsonStart = text.firstIndex(of: "{"),
              let jsonEnd = text.lastIndex(of: "}") else {
            throw AdaError.parseError("No JSON found in response")
        }

        let jsonString = String(text[jsonStart...jsonEnd])
        guard let data = jsonString.data(using: .utf8),
              let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            throw AdaError.parseError("Invalid JSON in response")
        }

        // Parse goal
        guard let goalData = json["goal"] as? [String: Any],
              let goalDesc = goalData["description"] as? String,
              let goalTarget = goalData["target"] as? [String: String] else {
            throw AdaError.parseError("Invalid goal format")
        }

        let goal = Goal(description: goalDesc, target: goalTarget)

        // Parse transforms
        guard let transformsData = json["transforms"] as? [[String: Any]] else {
            throw AdaError.parseError("Invalid transforms format")
        }

        var transforms: [Transform] = []
        for t in transformsData {
            guard let name = t["name"] as? String,
                  let desc = t["description"] as? String else {
                continue
            }

            let transform = Transform(
                name: name,
                description: desc,
                preconditions: t["preconditions"] as? [String: String] ?? [:],
                effects: t["effects"] as? [String: String] ?? [:],
                domain: t["domain"] as? String ?? "general",
                cost: t["cost"] as? Double ?? 1.0
            )
            transforms.append(transform)
        }

        let confidence = json["confidence"] as? Double ?? 0.5
        let warnings = json["warnings"] as? [String] ?? []

        return IntentProposal(
            goal: goal,
            transforms: transforms,
            confidence: confidence,
            originalIntent: originalIntent,
            warnings: warnings
        )
    }
}

enum AdaError: Error {
    case apiError(String)
    case parseError(String)
    case validationFailed(String)
    case executionFailed(String)
}

// MARK: - Ada: The Complete System

/// Ada: Intent-to-Transform Compiler for Newton
///
/// The bridge between human dreams and Newton's deterministic reality.
/// Ada understands what you want. Newton ensures it's safe.
///
/// "The intent is the dream. The transform is the plan. Newton is the reality."
///
class Ada {

    /// LLM bridge for intent understanding
    private let llmBridge: AdaLLMBridge?

    /// Rule-based fallback parser
    private let ruleParser: AdaIntentParser

    /// Newton validator (the gatekeeper)
    private let validator: NewtonValidator

    /// Newton executor (writes to ledger)
    private let executor: NewtonExecutor

    /// Current context for intent parsing
    private var context: [String: String] = [:]

    /// Whether to use LLM or fallback to rules
    private var useLLM: Bool

    init(apiKey: String? = nil, initialState: [String: String] = [:]) {
        self.validator = NewtonValidator()
        self.executor = NewtonExecutor(validator: validator, initialState: initialState)
        self.ruleParser = AdaIntentParser()

        if let key = apiKey {
            self.llmBridge = AdaLLMBridge(apiKey: key)
            self.useLLM = true
        } else {
            self.llmBridge = nil
            self.useLLM = false
        }
    }

    /// Process a human intent through the full pipeline
    /// Intent → Parse → Validate → Execute → Result
    func process(_ intent: String) async throws -> AdaResult {

        // Step 1: Parse intent into proposal
        let proposal: IntentProposal

        if useLLM, let bridge = llmBridge {
            do {
                proposal = try await bridge.parse(intent, context: context)
            } catch {
                // Fallback to rule-based
                guard let fallback = ruleParser.parse(intent) else {
                    throw AdaError.parseError("Could not understand intent: \(intent)")
                }
                proposal = fallback
            }
        } else {
            guard let parsed = ruleParser.parse(intent) else {
                throw AdaError.parseError("Could not understand intent: \(intent)")
            }
            proposal = parsed
        }

        // Step 2: Validate with Newton
        let validation = validator.validate(proposal, currentState: executor.state)

        switch validation {
        case .invalid(let reason, let constraint):
            return AdaResult(
                success: false,
                proposal: proposal,
                validation: validation,
                executions: [],
                message: "Newton rejected: \(reason) (constraint: \(constraint))"
            )

        case .ambiguous(let options):
            return AdaResult(
                success: false,
                proposal: proposal,
                validation: validation,
                executions: [],
                message: "Ambiguous intent. \(options.count) possible interpretations."
            )

        case .valid(let signature, let fgRatio):
            // Step 3: Execute
            let results = executor.execute(proposal)

            let allSucceeded = results.allSatisfy { $0.success }

            return AdaResult(
                success: allSucceeded,
                proposal: proposal,
                validation: validation,
                executions: results,
                message: allSucceeded
                    ? "Executed successfully. Signature: \(signature), f/g: \(String(format: "%.2f", fgRatio))"
                    : "Execution failed after validation"
            )
        }
    }

    /// Set context for future intent parsing
    func setContext(_ key: String, _ value: String) {
        context[key] = value
    }

    /// Get current state
    var currentState: [String: String] {
        return executor.state
    }

    /// Get ledger entries
    var ledger: [NewtonExecutor.LedgerEntry] {
        return executor.getLedger()
    }

    /// Enable/disable LLM usage
    func setUseLLM(_ enabled: Bool) {
        useLLM = enabled && llmBridge != nil
    }
}

/// Result of Ada processing
struct AdaResult {
    let success: Bool
    let proposal: IntentProposal
    let validation: ValidationResult
    let executions: [ExecutionResult]
    let message: String

    /// Check if we hit finfr (ontological death)
    var isFinfr: Bool {
        return executions.contains { $0.isFinfr }
    }
}

// MARK: - Convenience Extensions

extension Ada {

    /// Quick validation without execution
    func validate(_ intent: String) async throws -> ValidationResult {
        let proposal: IntentProposal

        if useLLM, let bridge = llmBridge {
            proposal = try await bridge.parse(intent, context: context)
        } else {
            guard let parsed = ruleParser.parse(intent) else {
                throw AdaError.parseError("Could not understand intent")
            }
            proposal = parsed
        }

        return validator.validate(proposal, currentState: executor.state)
    }

    /// Check if intent would succeed without executing
    func wouldSucceed(_ intent: String) async -> Bool {
        do {
            let validation = try await validate(intent)
            return validation.isValid
        } catch {
            return false
        }
    }
}

// MARK: - Example Usage

/*

 // Initialize Ada with Claude API key
 let ada = Ada(
     apiKey: "your-api-key",
     initialState: [
         "authenticated": "true",
         "has_balance": "true",
         "balance": "5000"
     ]
 )

 // Process an intent
 Task {
     do {
         let result = try await ada.process("Send $100 to Alice")

         if result.success {
             print("✓ Executed: \(result.message)")
             print("New state: \(ada.currentState)")
         } else {
             print("✗ Rejected: \(result.message)")
         }
     } catch {
         print("Error: \(error)")
     }
 }

 // Or use rule-based parsing (no API key needed)
 let adaOffline = Ada(initialState: ["authenticated": "true"])

 Task {
     let result = try await adaOffline.process("approve expense report")
     print(result.message)
 }

 */

// MARK: - Philosophy
//
// "The LLM can hallucinate. Newton only accepts what works."
//
// Ada is the dreamer. Newton is the reality check.
// Together they bridge human intent and verified execution.
//
// 1 == 1. Ask Newton. Go.
//
// © 2026 Jared Lewis · Ada Computing Company · Houston, Texas
