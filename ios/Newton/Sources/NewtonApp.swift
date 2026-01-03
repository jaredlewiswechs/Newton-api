//
//  NewtonApp.swift
//  Newton
//
//  Newton Supercomputer iOS Client
//  Verified computation at your fingertips.
//
//  © 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
//

import SwiftUI

@main
struct NewtonApp: App {
    @StateObject private var settings = AppSettings()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(settings)
                .preferredColorScheme(settings.darkMode ? .dark : nil)
        }
    }
}

// MARK: - App Settings

@MainActor
class AppSettings: ObservableObject {
    @AppStorage("serverURL") var serverURL: String = "https://newton-api.onrender.com"
    @AppStorage("darkMode") var darkMode: Bool = false

    var baseURL: URL {
        URL(string: serverURL) ?? URL(string: "https://newton-api.onrender.com")!
    }
}
