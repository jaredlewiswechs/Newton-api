//
//  DashboardView.swift
//  Newton
//
//  System health dashboard with Liquid Glass design.
//

import SwiftUI

struct DashboardView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var health: HealthResponse?
    @State private var isLoading = false
    @State private var error: Error?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // Status Card
                    statusCard

                    // Metrics Grid
                    metricsGrid

                    // Quick Actions
                    quickActions
                }
                .padding()
            }
            .navigationTitle("Newton")
            .refreshable {
                await fetchHealth()
            }
            .task {
                await fetchHealth()
            }
        }
    }

    // MARK: - Status Card

    private var statusCard: some View {
        VStack(spacing: 16) {
            HStack {
                Image(systemName: statusIcon)
                    .font(.system(size: 48))
                    .foregroundStyle(statusColor)
                    .symbolEffect(.pulse, options: .repeating, value: health?.isHealthy ?? false)

                VStack(alignment: .leading, spacing: 4) {
                    Text(statusTitle)
                        .font(.title2.bold())
                    Text(statusSubtitle)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                Spacer()
            }
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20))
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .strokeBorder(.quaternary, lineWidth: 0.5)
        )
    }

    private var statusIcon: String {
        if isLoading { return "arrow.trianglehead.2.clockwise" }
        if error != nil { return "exclamationmark.triangle.fill" }
        return health?.isHealthy == true ? "checkmark.seal.fill" : "xmark.seal.fill"
    }

    private var statusColor: Color {
        if isLoading { return .secondary }
        if error != nil { return .orange }
        return health?.isHealthy == true ? .green : .red
    }

    private var statusTitle: String {
        if isLoading { return "Connecting..." }
        if error != nil { return "Connection Error" }
        return health?.isHealthy == true ? "Operational" : "Degraded"
    }

    private var statusSubtitle: String {
        if isLoading { return "Checking system status" }
        if let error { return error.localizedDescription }
        if let health {
            return "v\(health.version) · Uptime: \(health.formattedUptime)"
        }
        return "—"
    }

    // MARK: - Metrics Grid

    private var metricsGrid: some View {
        LazyVGrid(columns: [
            GridItem(.flexible()),
            GridItem(.flexible())
        ], spacing: 16) {
            MetricCard(
                title: "Version",
                value: health?.version ?? "—",
                icon: "tag",
                color: .blue
            )

            MetricCard(
                title: "Uptime",
                value: health?.formattedUptime ?? "—",
                icon: "clock",
                color: .green
            )

            MetricCard(
                title: "Latency",
                value: "<3ms",
                icon: "bolt",
                color: .orange
            )

            MetricCard(
                title: "Throughput",
                value: "605/s",
                icon: "arrow.up.arrow.down",
                color: .purple
            )
        }
    }

    // MARK: - Quick Actions

    private var quickActions: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Quick Actions")
                .font(.headline)
                .foregroundStyle(.secondary)

            HStack(spacing: 12) {
                QuickActionButton(
                    title: "Verify",
                    icon: "checkmark.shield",
                    color: .green
                ) {
                    // Navigate to verify tab
                }

                QuickActionButton(
                    title: "Calculate",
                    icon: "function",
                    color: .blue
                ) {
                    // Navigate to calculate tab
                }
            }
        }
    }

    // MARK: - Data Fetching

    private func fetchHealth() async {
        isLoading = true
        error = nil

        let api = NewtonAPI(baseURL: settings.baseURL)

        do {
            health = try await api.health()
            triggerHaptic(.success)
        } catch {
            self.error = error
            triggerHaptic(.error)
        }

        isLoading = false
    }

    private func triggerHaptic(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(type)
    }
}

// MARK: - Metric Card

struct MetricCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundStyle(color)
                Spacer()
            }

            Text(value)
                .font(.title2.bold().monospacedDigit())

            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16))
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .strokeBorder(.quaternary, lineWidth: 0.5)
        )
    }
}

// MARK: - Quick Action Button

struct QuickActionButton: View {
    let title: String
    let icon: String
    let color: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                Text(title)
            }
            .font(.subheadline.weight(.medium))
            .frame(maxWidth: .infinity)
            .padding()
            .background(color.opacity(0.15), in: RoundedRectangle(cornerRadius: 12))
            .foregroundStyle(color)
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    DashboardView()
        .environmentObject(AppSettings())
}
