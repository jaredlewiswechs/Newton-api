//
//  VerifyView.swift
//  Newton
//
//  Content safety verification with real-time feedback.
//

import SwiftUI

struct VerifyView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var inputText = ""
    @State private var result: VerifyResponse?
    @State private var isVerifying = false
    @State private var error: Error?
    @FocusState private var isInputFocused: Bool

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // Input Section
                    inputSection

                    // Verify Button
                    verifyButton

                    // Result Section
                    if let result {
                        resultSection(result)
                    }

                    // Error Section
                    if let error {
                        errorSection(error)
                    }
                }
                .padding()
            }
            .navigationTitle("Verify")
            .toolbar {
                ToolbarItemGroup(placement: .keyboard) {
                    Spacer()
                    Button("Done") {
                        isInputFocused = false
                    }
                }
            }
        }
    }

    // MARK: - Input Section

    private var inputSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Content to Verify")
                .font(.subheadline.weight(.medium))
                .foregroundStyle(.secondary)

            TextEditor(text: $inputText)
                .focused($isInputFocused)
                .frame(minHeight: 120)
                .padding(12)
                .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16))
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .strokeBorder(.quaternary, lineWidth: 0.5)
                )
        }
    }

    // MARK: - Verify Button

    private var verifyButton: some View {
        Button {
            Task { await verify() }
        } label: {
            HStack(spacing: 8) {
                if isVerifying {
                    ProgressView()
                        .tint(.white)
                } else {
                    Image(systemName: "checkmark.shield")
                }
                Text(isVerifying ? "Verifying..." : "Verify Content")
            }
            .font(.headline)
            .frame(maxWidth: .infinity)
            .padding()
            .background(inputText.isEmpty ? Color.secondary : Color.accentColor, in: RoundedRectangle(cornerRadius: 14))
            .foregroundStyle(.white)
        }
        .disabled(inputText.isEmpty || isVerifying)
        .buttonStyle(.plain)
    }

    // MARK: - Result Section

    private func resultSection(_ response: VerifyResponse) -> some View {
        VStack(spacing: 16) {
            // Status Header
            HStack {
                Image(systemName: response.verified ? "checkmark.seal.fill" : "xmark.seal.fill")
                    .font(.system(size: 40))
                    .foregroundStyle(response.verified ? .green : .red)
                    .symbolEffect(.bounce, value: response.verified)

                VStack(alignment: .leading, spacing: 4) {
                    Text(response.verified ? "Content Safe" : "Violations Detected")
                        .font(.title3.bold())

                    Text("Verified in \(response.formattedLatency)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Spacer()
            }
            .padding()
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16))

            // Details
            VStack(alignment: .leading, spacing: 12) {
                DetailRow(label: "Fingerprint", value: response.fingerprint)

                if let ledger = response.ledgerEntry {
                    DetailRow(label: "Ledger Entry", value: "#\(ledger)")
                }

                if let categories = response.result?.categories {
                    ForEach(Array(categories.keys.sorted()), id: \.self) { key in
                        if let cat = categories[key] {
                            DetailRow(
                                label: key.capitalized,
                                value: cat.passed ? "Passed" : "Failed",
                                valueColor: cat.passed ? .green : .red
                            )
                        }
                    }
                }
            }
            .padding()
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16))
        }
    }

    // MARK: - Error Section

    private func errorSection(_ error: Error) -> some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundStyle(.orange)

            Text(error.localizedDescription)
                .font(.subheadline)

            Spacer()
        }
        .padding()
        .background(.orange.opacity(0.1), in: RoundedRectangle(cornerRadius: 12))
    }

    // MARK: - Verification

    private func verify() async {
        isVerifying = true
        error = nil
        result = nil

        let api = NewtonAPI(baseURL: settings.baseURL)

        do {
            result = try await api.verify(input: inputText)
            triggerHaptic(result?.verified == true ? .success : .warning)
        } catch {
            self.error = error
            triggerHaptic(.error)
        }

        isVerifying = false
    }

    private func triggerHaptic(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(type)
    }
}

// MARK: - Detail Row

struct DetailRow: View {
    let label: String
    let value: String
    var valueColor: Color = .primary

    var body: some View {
        HStack {
            Text(label)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            Spacer()

            Text(value)
                .font(.subheadline.monospaced())
                .foregroundStyle(valueColor)
        }
    }
}

#Preview {
    VerifyView()
        .environmentObject(AppSettings())
}
