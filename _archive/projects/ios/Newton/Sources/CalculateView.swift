//
//  CalculateView.swift
//  Newton
//
//  Verified arithmetic operations with cryptographic proofs.
//

import SwiftUI

struct CalculateView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var expression = ""
    @State private var result: CalculateResponse?
    @State private var history: [CalculateResponse] = []
    @State private var isCalculating = false
    @State private var error: Error?
    @FocusState private var isInputFocused: Bool

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Display Area
                displayArea

                // Keypad
                keypad
            }
            .navigationTitle("Calculate")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        clearAll()
                    } label: {
                        Text("Clear")
                            .font(.subheadline)
                    }
                    .disabled(expression.isEmpty && result == nil)
                }
            }
        }
    }

    // MARK: - Display Area

    private var displayArea: some View {
        VStack(spacing: 12) {
            Spacer()

            // Expression
            Text(expression.isEmpty ? "0" : expression)
                .font(.system(size: 48, weight: .light, design: .monospaced))
                .lineLimit(1)
                .minimumScaleFactor(0.5)
                .frame(maxWidth: .infinity, alignment: .trailing)

            // Result
            if let result {
                HStack(spacing: 8) {
                    Image(systemName: result.verified ? "checkmark.seal.fill" : "xmark.seal.fill")
                        .foregroundStyle(result.verified ? .green : .red)

                    Text("= \(result.formattedResult)")
                        .font(.system(size: 32, weight: .medium, design: .monospaced))

                    Spacer()

                    Text(result.formattedLatency)
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                }
                .transition(.move(edge: .bottom).combined(with: .opacity))
            }

            // Fingerprint
            if let fingerprint = result?.fingerprint {
                Text(fingerprint)
                    .font(.caption2.monospaced())
                    .foregroundStyle(.tertiary)
                    .frame(maxWidth: .infinity, alignment: .trailing)
            }

            // Error
            if let error {
                Text(error.localizedDescription)
                    .font(.caption)
                    .foregroundStyle(.red)
                    .frame(maxWidth: .infinity, alignment: .trailing)
            }
        }
        .padding()
        .frame(maxHeight: .infinity)
        .background(.regularMaterial)
    }

    // MARK: - Keypad

    private var keypad: some View {
        VStack(spacing: 1) {
            ForEach(keyRows, id: \.self) { row in
                HStack(spacing: 1) {
                    ForEach(row, id: \.self) { key in
                        KeyButton(key: key) {
                            handleKey(key)
                        }
                    }
                }
            }
        }
        .background(.separator)
    }

    private let keyRows: [[String]] = [
        ["C", "(", ")", "/"],
        ["7", "8", "9", "*"],
        ["4", "5", "6", "-"],
        ["1", "2", "3", "+"],
        ["0", ".", "⌫", "="]
    ]

    // MARK: - Key Handling

    private func handleKey(_ key: String) {
        let impact = UIImpactFeedbackGenerator(style: .light)
        impact.impactOccurred()

        switch key {
        case "C":
            clearAll()
        case "⌫":
            if !expression.isEmpty {
                expression.removeLast()
            }
        case "=":
            Task { await calculate() }
        default:
            expression.append(key)
        }
    }

    private func clearAll() {
        expression = ""
        result = nil
        error = nil
    }

    // MARK: - Calculation

    private func calculate() async {
        guard !expression.isEmpty else { return }

        isCalculating = true
        error = nil

        let api = NewtonAPI(baseURL: settings.baseURL)

        do {
            let response = try await api.calculate(expression: expression)
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                result = response
            }
            if response.verified {
                history.insert(response, at: 0)
            }
            triggerHaptic(response.verified ? .success : .error)
        } catch {
            self.error = error
            triggerHaptic(.error)
        }

        isCalculating = false
    }

    private func triggerHaptic(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(type)
    }
}

// MARK: - Key Button

struct KeyButton: View {
    let key: String
    let action: () -> Void

    private var isOperator: Bool {
        ["/", "*", "-", "+", "="].contains(key)
    }

    private var isFunction: Bool {
        ["C", "(", ")", "⌫"].contains(key)
    }

    private var backgroundColor: Color {
        if key == "=" { return .accentColor }
        if isOperator { return Color(.systemGray4) }
        if isFunction { return Color(.systemGray5) }
        return Color(.systemGray6)
    }

    private var foregroundColor: Color {
        if key == "=" { return .white }
        if isOperator { return .accentColor }
        return .primary
    }

    var body: some View {
        Button(action: action) {
            Text(key)
                .font(.title.weight(isOperator ? .medium : .regular))
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(backgroundColor)
                .foregroundStyle(foregroundColor)
        }
        .buttonStyle(.plain)
        .frame(height: 72)
    }
}

#Preview {
    CalculateView()
        .environmentObject(AppSettings())
}
