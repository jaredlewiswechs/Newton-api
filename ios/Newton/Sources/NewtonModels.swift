//
//  NewtonModels.swift
//  Newton
//
//  API response models for Newton Supercomputer.
//

import Foundation

// MARK: - Health Response

struct HealthResponse: Codable {
    let status: String
    let version: String
    let uptime: Double
    let timestamp: Int

    var isHealthy: Bool { status == "operational" }
    var formattedUptime: String {
        let hours = Int(uptime) / 3600
        let minutes = (Int(uptime) % 3600) / 60
        return "\(hours)h \(minutes)m"
    }
}

// MARK: - Verify Request/Response

struct VerifyRequest: Codable {
    let input: String
    let constraints: [String]?

    init(input: String, constraints: [String]? = nil) {
        self.input = input
        self.constraints = constraints
    }
}

struct VerifyResponse: Codable {
    let verified: Bool
    let result: VerifyResult?
    let code: Int
    let elapsedUs: Int
    let fingerprint: String
    let ledgerEntry: Int?

    enum CodingKeys: String, CodingKey {
        case verified, result, code, fingerprint
        case elapsedUs = "elapsed_us"
        case ledgerEntry = "ledger_entry"
    }

    var formattedLatency: String {
        if elapsedUs < 1000 {
            return "\(elapsedUs)μs"
        } else {
            return String(format: "%.2fms", Double(elapsedUs) / 1000.0)
        }
    }
}

struct VerifyResult: Codable {
    let safe: Bool
    let categories: [String: CategoryResult]?
    let input: String?
    let inputHash: String?

    enum CodingKeys: String, CodingKey {
        case safe, categories, input
        case inputHash = "input_hash"
    }
}

struct CategoryResult: Codable {
    let passed: Bool
    let violations: [String]?
}

// MARK: - Calculate Request/Response

struct CalculateRequest: Codable {
    let expression: String
}

struct CalculateResponse: Codable {
    let verified: Bool
    let result: Double?
    let expression: String?
    let code: Int
    let elapsedUs: Int
    let fingerprint: String

    enum CodingKeys: String, CodingKey {
        case verified, result, expression, code, fingerprint
        case elapsedUs = "elapsed_us"
    }

    var formattedResult: String {
        guard let result else { return "—" }
        if result.truncatingRemainder(dividingBy: 1) == 0 {
            return String(format: "%.0f", result)
        }
        return String(format: "%.6g", result)
    }

    var formattedLatency: String {
        if elapsedUs < 1000 {
            return "\(elapsedUs)μs"
        } else {
            return String(format: "%.2fms", Double(elapsedUs) / 1000.0)
        }
    }
}

// MARK: - Generic API Error

struct APIError: Codable, Error, LocalizedError {
    let detail: String?
    let message: String?

    var errorDescription: String? {
        detail ?? message ?? "Unknown error"
    }
}
