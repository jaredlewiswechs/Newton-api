//
//  ContentView.swift
//  Newton
//
//  Main tab navigation with Liquid Glass design.
//

import SwiftUI

struct ContentView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tabItem {
                    Label("Dashboard", systemImage: "gauge.with.needle")
                }
                .tag(0)

            VerifyView()
                .tabItem {
                    Label("Verify", systemImage: "checkmark.shield")
                }
                .tag(1)

            CalculateView()
                .tabItem {
                    Label("Calculate", systemImage: "function")
                }
                .tag(2)

            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
                .tag(3)
        }
        .tint(.accentColor)
    }
}

#Preview {
    ContentView()
        .environmentObject(AppSettings())
}
