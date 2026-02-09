//
//  SettingsView.swift
//  Newton
//
//  App configuration and server settings.
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var serverURL: String = ""
    @State private var isTestingConnection = false
    @State private var connectionStatus: ConnectionStatus?

    var body: some View {
        NavigationStack {
            Form {
                // Server Configuration
                Section {
                    TextField("Server URL", text: $serverURL)
                        .keyboardType(.URL)
                        .textContentType(.URL)
                        .autocorrectionDisabled()
                        .textInputAutocapitalization(.never)

                    Button {
                        Task { await testConnection() }
                    } label: {
                        HStack {
                            if isTestingConnection {
                                ProgressView()
                                    .padding(.trailing, 4)
                            }
                            Text(isTestingConnection ? "Testing..." : "Test Connection")
                        }
                    }
                    .disabled(serverURL.isEmpty || isTestingConnection)

                    if let status = connectionStatus {
                        HStack {
                            Image(systemName: status.icon)
                                .foregroundStyle(status.color)
                            Text(status.message)
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                        }
                    }
                } header: {
                    Text("Server")
                } footer: {
                    Text("Enter the URL of your Newton API server.")
                }

                // Appearance
                Section("Appearance") {
                    Toggle(isOn: $settings.darkMode) {
                        Label("Dark Mode", systemImage: "moon.fill")
                    }
                }

                // About
                Section("About") {
                    LabeledContent("Version", value: "1.0.0")
                    LabeledContent("Build", value: "2026.01.04")

                    Link(destination: URL(string: "https://github.com/jaredlewiswechs/Newton-api")!) {
                        HStack {
                            Label("Source Code", systemImage: "chevron.left.forwardslash.chevron.right")
                            Spacer()
                            Image(systemName: "arrow.up.right")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }

                // Credits
                Section {
                    VStack(alignment: .center, spacing: 8) {
                        Image(systemName: "atom")
                            .font(.system(size: 40))
                            .foregroundStyle(.accent)

                        Text("Newton Supercomputer")
                            .font(.headline)

                        Text("Verified computation.\nConstraint-first design.")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                            .multilineTextAlignment(.center)

                        Text("© 2025-2026 Jared Lewis")
                            .font(.caption2)
                            .foregroundStyle(.tertiary)
                            .padding(.top, 4)

                        Text("Ada Computing Company · Houston, Texas")
                            .font(.caption2)
                            .foregroundStyle(.tertiary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 8)
                }
            }
            .navigationTitle("Settings")
            .onAppear {
                serverURL = settings.serverURL
            }
            .onChange(of: serverURL) { _, newValue in
                settings.serverURL = newValue
                connectionStatus = nil
            }
        }
    }

    // MARK: - Connection Test

    private func testConnection() async {
        isTestingConnection = true
        connectionStatus = nil

        let api = NewtonAPI(baseURL: settings.baseURL)

        do {
            let health = try await api.health()
            connectionStatus = .success(version: health.version)
            triggerHaptic(.success)
        } catch {
            connectionStatus = .failure(error: error)
            triggerHaptic(.error)
        }

        isTestingConnection = false
    }

    private func triggerHaptic(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(type)
    }
}

// MARK: - Connection Status

enum ConnectionStatus {
    case success(version: String)
    case failure(error: Error)

    var icon: String {
        switch self {
        case .success: return "checkmark.circle.fill"
        case .failure: return "xmark.circle.fill"
        }
    }

    var color: Color {
        switch self {
        case .success: return .green
        case .failure: return .red
        }
    }

    var message: String {
        switch self {
        case .success(let version):
            return "Connected to Newton v\(version)"
        case .failure(let error):
            return error.localizedDescription
        }
    }
}

#Preview {
    SettingsView()
        .environmentObject(AppSettings())
}
