//
//  NewtonAPI.swift
//  Newton
//
//  Network client for Newton Supercomputer API.
//

import Foundation

// MARK: - Newton API Client

@MainActor
class NewtonAPI: ObservableObject {
    private let session: URLSession
    private let baseURL: URL
    private let decoder: JSONDecoder

    init(baseURL: URL) {
        self.baseURL = baseURL
        self.decoder = JSONDecoder()

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)
    }

    // MARK: - Health Check

    func health() async throws -> HealthResponse {
        let url = baseURL.appendingPathComponent("health")
        let (data, response) = try await session.data(from: url)
        try validateResponse(response)
        return try decoder.decode(HealthResponse.self, from: data)
    }

    // MARK: - Verify Content

    func verify(input: String, constraints: [String]? = nil) async throws -> VerifyResponse {
        let url = baseURL.appendingPathComponent("verify")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = VerifyRequest(input: input, constraints: constraints)
        request.httpBody = try JSONEncoder().encode(body)

        let (data, response) = try await session.data(for: request)
        try validateResponse(response)
        return try decoder.decode(VerifyResponse.self, from: data)
    }

    // MARK: - Calculate Expression

    func calculate(expression: String) async throws -> CalculateResponse {
        let url = baseURL.appendingPathComponent("calculate")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = CalculateRequest(expression: expression)
        request.httpBody = try JSONEncoder().encode(body)

        let (data, response) = try await session.data(for: request)
        try validateResponse(response)
        return try decoder.decode(CalculateResponse.self, from: data)
    }

    // MARK: - Response Validation

    private func validateResponse(_ response: URLResponse) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NewtonError.invalidResponse
        }

        switch httpResponse.statusCode {
        case 200...299:
            return
        case 400:
            throw NewtonError.badRequest
        case 401, 403:
            throw NewtonError.unauthorized
        case 404:
            throw NewtonError.notFound
        case 500...599:
            throw NewtonError.serverError(httpResponse.statusCode)
        default:
            throw NewtonError.unknown(httpResponse.statusCode)
        }
    }
}

// MARK: - Newton Errors

enum NewtonError: LocalizedError {
    case invalidResponse
    case badRequest
    case unauthorized
    case notFound
    case serverError(Int)
    case unknown(Int)

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid response from server"
        case .badRequest:
            return "Invalid request"
        case .unauthorized:
            return "Unauthorized access"
        case .notFound:
            return "Resource not found"
        case .serverError(let code):
            return "Server error (\(code))"
        case .unknown(let code):
            return "Unknown error (\(code))"
        }
    }
}
