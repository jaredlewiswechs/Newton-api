# Swift & SwiftUI: A Combinatorial Guide

**January 2026** · **Jared Lewis** · **Ada Computing Company** · **Newton**

<p align="center">
  <img src="https://img.shields.io/badge/Swift-6.2-orange.svg" alt="Swift 6.2">
  <img src="https://img.shields.io/badge/SwiftUI-iOS_26-blue.svg" alt="SwiftUI iOS 26">
  <img src="https://img.shields.io/badge/Playgrounds-4.6-purple.svg" alt="Playgrounds 4.6">
  <img src="https://img.shields.io/badge/Philosophy-Combinations-green.svg" alt="Combinations">
</p>

<p align="center">
  <strong>Think in Combinations, Not Permutations</strong><br>
  <em>SwiftUI is a box of LEGO. This guide is the picture on the box.</em>
</p>

---

## The Philosophy: Why This Guide Is Different

Most programming guides teach you sequences: "First do A, then B, then C." That's **permutations thinking**—the order matters, you follow steps.

This guide teaches **combinations thinking**: here are the pieces, here's what each piece does, combine them however you need.

```
Permutations: A → B → C → D (one path, order matters)
Combinations: {A, B, C, D} → pick what you need → combine
```

SwiftUI was *built* for combinations thinking. It's declarative—you describe *what* you want, not *how* to build it step by step. The compiler figures out the rest.

**Read this guide alongside Swift Playgrounds.** When you see a building block, try it. Mix it with another. Break things. The playground shows your changes instantly.

---

## Table of Contents

1. [The Building Blocks](#the-building-blocks)
2. [Values: The Atoms](#values-the-atoms)
3. [Views: The Molecules](#views-the-molecules)
4. [Containers: The Organizers](#containers-the-organizers)
5. [Modifiers: The Decorators](#modifiers-the-decorators)
6. [State: The Memory](#state-the-memory)
7. [Actions: The Reactions](#actions-the-reactions)
8. [Navigation: The Portals](#navigation-the-portals)
9. [Data Flow: The Rivers](#data-flow-the-rivers)
10. [Combination Patterns](#combination-patterns)
11. [Swift Playgrounds Setup](#swift-playgrounds-setup)
12. [Newton Integration](#newton-integration)
13. [What's New in 2025-2026](#whats-new-in-2025-2026)
14. [Quick Reference Card](#quick-reference-card)

---

## The Building Blocks

Everything in Swift/SwiftUI falls into one of these categories:

| Block Type | What It Is | Example | Combines With |
|------------|-----------|---------|---------------|
| **Value** | A piece of data | `"Hello"`, `42`, `true` | Everything |
| **View** | Something visible | `Text`, `Image`, `Button` | Containers, Modifiers |
| **Container** | Holds other views | `VStack`, `HStack`, `List` | Views, other Containers |
| **Modifier** | Changes appearance/behavior | `.font()`, `.padding()` | Views, Containers |
| **State** | Memory that triggers updates | `@State`, `@Observable` | Views (causes redraw) |
| **Action** | Something that happens | `{ code }`, `func` | Buttons, Gestures |

That's it. Six categories. Everything else is a specific instance of one of these.

---

## Values: The Atoms

Values are your raw data. Swift is **type-safe**—every value has exactly one type.

### The Essential Types

```swift
// Text
let greeting = "Hello"           // String
let letter: Character = "A"      // Character

// Numbers
let count = 42                   // Int (whole number)
let price = 19.99                // Double (decimal)
let precise: Float = 3.14        // Float (less precise decimal)

// Logic
let isActive = true              // Bool (true or false)

// Collections
let colors = ["red", "blue"]     // Array (ordered list)
let ages = ["Alice": 30]         // Dictionary (key → value)
let uniqueIDs: Set = [1, 2, 3]   // Set (unique, unordered)

// Optional (might be empty)
let maybeName: String? = nil     // Optional String
```

### Type Conversion (Casting)

Types don't auto-convert. You combine them explicitly:

```swift
let number = 42
let text = String(number)        // "42"

let input = "123"
let parsed = Int(input)          // Optional! Could be nil if invalid

// Safe unwrapping
if let value = Int(input) {
    print("Got \(value)")
}
```

### String Combinations

```swift
let name = "Newton"
let version = 2

// Interpolation (embed values in strings)
let message = "Welcome to \(name) v\(version)"

// Multi-line
let poem = """
    Roses are red,
    Violets are blue,
    Swift is declarative,
    And so are you.
    """
```

---

## Views: The Molecules

Views are the visible building blocks. Each is a noun—a thing you can see.

### Text Views

```swift
Text("Hello, World")              // Basic text
Text(verbatim: "No interpolation") // Literal text
Label("Settings", systemImage: "gear") // Icon + text
```

### Image Views

```swift
Image(systemName: "star.fill")    // SF Symbol
Image("myPhoto")                  // Asset from your project
AsyncImage(url: photoURL)         // Load from internet
```

### Input Views

```swift
TextField("Name", text: $name)    // Single line input
TextEditor(text: $notes)          // Multi-line input
SecureField("Password", text: $pw) // Hidden input
```

### Control Views

```swift
Button("Tap Me") { action() }     // Tappable
Toggle("Dark Mode", isOn: $isDark) // On/off switch
Slider(value: $volume, in: 0...100) // Draggable
Picker("Color", selection: $color) { } // Selection
Stepper("Qty: \(qty)", value: $qty) // +/- buttons
```

### Display Views

```swift
ProgressView()                    // Spinner
ProgressView(value: 0.7)          // Progress bar
Gauge(value: 0.5) { Text("50%") } // Gauge display
```

---

## Containers: The Organizers

Containers hold views and arrange them. Think of them as boxes with different packing rules.

### Stack Containers (Linear)

```swift
// Vertical (top to bottom)
VStack {
    Text("First")
    Text("Second")
    Text("Third")
}

// Horizontal (left to right)
HStack {
    Image(systemName: "star")
    Text("Rating")
}

// Layered (back to front)
ZStack {
    Color.blue           // Background
    Text("Overlay")      // Foreground
}
```

### Spacing & Alignment

```swift
VStack(alignment: .leading, spacing: 20) {
    Text("Left aligned")
    Text("With 20pt gaps")
}

HStack(alignment: .top) {
    Text("Top")
    Text("Aligned\nMultiple\nLines")
}
```

### List Containers (Scrolling)

```swift
// Static list
List {
    Text("Item 1")
    Text("Item 2")
}

// Dynamic list
List(items) { item in
    Text(item.name)
}

// Sections
List {
    Section("Favorites") {
        Text("Coffee")
    }
    Section("Others") {
        Text("Tea")
    }
}
```

### Grid Containers

```swift
// Simple grid
LazyVGrid(columns: [
    GridItem(.flexible()),
    GridItem(.flexible()),
    GridItem(.flexible())
]) {
    ForEach(1...9, id: \.self) { num in
        Text("\(num)")
    }
}

// Adaptive grid (auto-fits)
LazyVGrid(columns: [
    GridItem(.adaptive(minimum: 100))
]) {
    ForEach(photos) { photo in
        Image(photo.name)
    }
}
```

### Grouping

```swift
// Logical grouping (no visual effect)
Group {
    Text("A")
    Text("B")
}
.font(.headline)  // Applies to both

// ForEach (repeat views)
ForEach(items) { item in
    ItemView(item: item)
}

// ForEach with index
ForEach(Array(items.enumerated()), id: \.offset) { index, item in
    Text("\(index): \(item.name)")
}
```

---

## Modifiers: The Decorators

Modifiers change views. They chain together, each wrapping the previous result.

### Visual Modifiers

```swift
Text("Hello")
    .font(.title)              // Typography
    .fontWeight(.bold)
    .foregroundStyle(.blue)    // Color
    .italic()

Image(systemName: "star")
    .resizable()               // Allow sizing
    .scaledToFit()             // Maintain aspect
    .frame(width: 50, height: 50)
```

### Layout Modifiers

```swift
Text("Centered")
    .frame(maxWidth: .infinity) // Full width
    .padding()                  // Space around
    .padding(.horizontal, 20)   // Specific sides
    .background(.gray)          // Behind content
    .cornerRadius(10)           // Round corners
```

### Interaction Modifiers

```swift
Button("Tap") { }
    .disabled(isLoading)        // Gray out
    .opacity(isVisible ? 1 : 0) // Fade

Text("Tap me")
    .onTapGesture { handleTap() }
    .onLongPressGesture { handleHold() }
```

### Conditional Modifiers

```swift
Text("Dynamic")
    .font(isLarge ? .title : .body)
    .foregroundStyle(isError ? .red : .primary)

// View extension for cleaner conditionals
extension View {
    @ViewBuilder func `if`<T: View>(_ condition: Bool, transform: (Self) -> T) -> some View {
        if condition { transform(self) }
        else { self }
    }
}

// Usage
Text("Maybe Bold")
    .if(shouldBeBold) { $0.bold() }
```

### Modifier Order Matters

```swift
// Different results!
Text("A")
    .padding()
    .background(.red)    // Red box with padding

Text("B")
    .background(.red)
    .padding()           // Red text, then padding (clear)
```

Think of it like wrapping presents: the first modifier wraps the view, the second wraps that, etc.

---

## State: The Memory

State makes your UI dynamic. When state changes, views automatically update.

### The @State Pattern (Simple, Local)

```swift
struct CounterView: View {
    @State private var count = 0  // This view owns this state

    var body: some View {
        VStack {
            Text("Count: \(count)")
            Button("Add") { count += 1 }
        }
    }
}
```

**Rule**: Only the view that creates `@State` should own it.

### The @Binding Pattern (Shared, Two-Way)

```swift
// Parent owns the state
struct ParentView: View {
    @State private var name = ""

    var body: some View {
        ChildView(name: $name)  // $ creates a binding
    }
}

// Child can read AND write
struct ChildView: View {
    @Binding var name: String

    var body: some View {
        TextField("Enter name", text: $name)
    }
}
```

### The @Observable Pattern (Complex, Shared) - iOS 17+

```swift
@Observable
class AppState {
    var user: String = "Guest"
    var isLoggedIn: Bool = false
    var items: [Item] = []
}

struct ContentView: View {
    @State private var appState = AppState()  // Create once at top level

    var body: some View {
        VStack {
            Text("Welcome, \(appState.user)")

            if appState.isLoggedIn {
                ItemListView(items: appState.items)
            }
        }
        .environment(appState)  // Share with children
    }
}

struct ChildView: View {
    @Environment(AppState.self) var appState  // Access shared state

    var body: some View {
        Text(appState.user)
    }
}
```

### State Summary Table

| Decorator | Use When | Example |
|-----------|----------|---------|
| `@State` | Local to one view | Toggle, counter, form field |
| `@Binding` | Child needs to modify parent's state | TextField in a form |
| `@Observable` | Shared across many views | User session, app settings |
| `@Environment` | Access Observable from any child | Theme, user data |

---

## Actions: The Reactions

Actions are closures—chunks of code that run when triggered.

### Basic Closure Syntax

```swift
// Full syntax
let greet = { (name: String) -> String in
    return "Hello, \(name)"
}

// Simplified (inferred types)
let greet = { name in "Hello, \(name)" }

// Trailing closure (common in SwiftUI)
Button("Tap") {
    print("Tapped!")
}
```

### Common Action Patterns

```swift
// Button action
Button("Save") {
    saveData()
}

// Async action
Button("Load") {
    Task {
        await loadData()
    }
}

// Gesture action
Text("Draggable")
    .gesture(
        DragGesture()
            .onChanged { value in
                position = value.location
            }
            .onEnded { _ in
                print("Done dragging")
            }
    )

// Lifecycle actions
VStack { }
    .onAppear { loadInitialData() }
    .onDisappear { cleanup() }
    .task { await fetchFromNetwork() }  // Auto-cancels
```

### Functions as Building Blocks

```swift
// Define once
func calculateTotal(items: [Item]) -> Double {
    items.reduce(0) { $0 + $1.price }
}

// Use anywhere
Text("Total: $\(calculateTotal(items: cart))")

// Pass as parameter
func process(items: [Item], using calculator: ([Item]) -> Double) -> Double {
    calculator(items)
}
```

---

## Navigation: The Portals

Navigation moves between screens. iOS 26 uses `NavigationStack`.

### Basic Navigation

```swift
struct HomeView: View {
    var body: some View {
        NavigationStack {
            List {
                NavigationLink("Go to Detail") {
                    DetailView()
                }

                NavigationLink(value: item) {
                    Text(item.name)
                }
            }
            .navigationTitle("Home")
            .navigationDestination(for: Item.self) { item in
                ItemDetailView(item: item)
            }
        }
    }
}
```

### Programmatic Navigation

```swift
struct NavView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            VStack {
                Button("Go to Settings") {
                    path.append("settings")
                }
                Button("Go Back") {
                    path.removeLast()
                }
            }
            .navigationDestination(for: String.self) { route in
                switch route {
                case "settings": SettingsView()
                default: Text("Unknown")
                }
            }
        }
    }
}
```

### Modal Presentations

```swift
struct ModalExample: View {
    @State private var showSheet = false
    @State private var showFullScreen = false
    @State private var showAlert = false

    var body: some View {
        VStack {
            Button("Show Sheet") { showSheet = true }
            Button("Full Screen") { showFullScreen = true }
            Button("Alert") { showAlert = true }
        }
        .sheet(isPresented: $showSheet) {
            SheetView()
        }
        .fullScreenCover(isPresented: $showFullScreen) {
            FullView()
        }
        .alert("Title", isPresented: $showAlert) {
            Button("OK") { }
            Button("Cancel", role: .cancel) { }
        } message: {
            Text("Alert message here")
        }
    }
}
```

### Tab Navigation

```swift
struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house")
                }
                .tag(0)

            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
                .tag(1)
        }
    }
}
```

---

## Data Flow: The Rivers

Data flows through your app in predictable ways.

### The River Analogy

```
Source (State) → View → Child View → Grandchild
       ↑                                    |
       └──────── Binding (upstream) ────────┘
```

- **Downstream**: Data flows from parent to child automatically
- **Upstream**: Bindings let children send changes back up

### Environment: The Underground River

```swift
// Define a key
struct ThemeKey: EnvironmentKey {
    static let defaultValue: Theme = .light
}

extension EnvironmentValues {
    var theme: Theme {
        get { self[ThemeKey.self] }
        set { self[ThemeKey.self] = newValue }
    }
}

// Set at any level
ContentView()
    .environment(\.theme, .dark)

// Access anywhere below
struct DeepChildView: View {
    @Environment(\.theme) var theme

    var body: some View {
        Text("Using \(theme)")
    }
}
```

### Async Data Loading

```swift
struct AsyncDataView: View {
    @State private var items: [Item] = []
    @State private var isLoading = true
    @State private var error: Error?

    var body: some View {
        Group {
            if isLoading {
                ProgressView()
            } else if let error {
                Text("Error: \(error.localizedDescription)")
            } else {
                List(items) { item in
                    Text(item.name)
                }
            }
        }
        .task {
            do {
                items = try await fetchItems()
                isLoading = false
            } catch {
                self.error = error
                isLoading = false
            }
        }
    }
}
```

---

## Combination Patterns

These are common ways to combine building blocks.

### Pattern 1: The Form

```swift
struct ProfileForm: View {
    @State private var name = ""
    @State private var email = ""
    @State private var notifications = true

    var body: some View {
        Form {
            Section("Personal") {
                TextField("Name", text: $name)
                TextField("Email", text: $email)
            }

            Section("Preferences") {
                Toggle("Notifications", isOn: $notifications)
            }

            Section {
                Button("Save") {
                    saveProfile()
                }
            }
        }
    }
}
```

### Pattern 2: The Card

```swift
struct CardView: View {
    let title: String
    let subtitle: String
    let icon: String

    var body: some View {
        HStack {
            Image(systemName: icon)
                .font(.title)
                .foregroundStyle(.blue)

            VStack(alignment: .leading) {
                Text(title)
                    .font(.headline)
                Text(subtitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Image(systemName: "chevron.right")
                .foregroundStyle(.tertiary)
        }
        .padding()
        .background(.background)
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}
```

### Pattern 3: The List with Search

```swift
struct SearchableListView: View {
    @State private var items: [Item] = []
    @State private var searchText = ""

    var filteredItems: [Item] {
        if searchText.isEmpty {
            return items
        }
        return items.filter { $0.name.localizedCaseInsensitiveContains(searchText) }
    }

    var body: some View {
        NavigationStack {
            List(filteredItems) { item in
                Text(item.name)
            }
            .searchable(text: $searchText, prompt: "Search items")
            .navigationTitle("Items")
        }
    }
}
```

### Pattern 4: The Master-Detail

```swift
struct MasterDetailView: View {
    @State private var items: [Item] = sampleItems
    @State private var selectedItem: Item?

    var body: some View {
        NavigationSplitView {
            List(items, selection: $selectedItem) { item in
                Text(item.name)
                    .tag(item)
            }
            .navigationTitle("Items")
        } detail: {
            if let item = selectedItem {
                ItemDetailView(item: item)
            } else {
                Text("Select an item")
                    .foregroundStyle(.secondary)
            }
        }
    }
}
```

### Pattern 5: The Loading State Machine

```swift
enum LoadingState<T> {
    case idle
    case loading
    case success(T)
    case error(Error)
}

struct LoadingView<T, Content: View>: View {
    let state: LoadingState<T>
    @ViewBuilder let content: (T) -> Content

    var body: some View {
        switch state {
        case .idle:
            Color.clear
        case .loading:
            ProgressView()
        case .success(let data):
            content(data)
        case .error(let error):
            VStack {
                Image(systemName: "exclamationmark.triangle")
                    .font(.largeTitle)
                Text(error.localizedDescription)
            }
            .foregroundStyle(.red)
        }
    }
}

// Usage
LoadingView(state: dataState) { items in
    List(items) { item in
        Text(item.name)
    }
}
```

---

## Swift Playgrounds Setup

### Getting Started on iPad

1. **Download** Swift Playgrounds from the App Store
2. **Open** the app → tap **"App"** (not "Playground")
3. **Choose** a template or start blank
4. **Write code** on the left, see preview on the right

### Your First Playgrounds App

Create a new App project and replace the contents:

```swift
import SwiftUI

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @State private var tapCount = 0

    var body: some View {
        VStack(spacing: 20) {
            Text("Tapped \(tapCount) times")
                .font(.title)

            Button("Tap Me!") {
                tapCount += 1
            }
            .buttonStyle(.borderedProminent)
        }
    }
}
```

### Playgrounds Capabilities (v4.6, January 2026)

| Feature | Support |
|---------|---------|
| SwiftUI | Full |
| Swift 6.2 | Full |
| SF Symbols | All 5000+ |
| SpriteKit | Full |
| PencilKit | Full |
| Camera/Photos | Full |
| Bluetooth | Full |
| Accelerometer | Full |
| Swift Packages | Full |
| App Store Submit | Yes |

### Adding Swift Packages

1. Tap the **sidebar** icon
2. Tap **"+"** next to your app name
3. Choose **"Swift Package"**
4. Enter the package URL

---

## Newton Integration

Newton provides verified computation for your SwiftUI apps. Here's how to integrate:

### Basic Newton Client

```swift
import SwiftUI

@Observable
class NewtonClient {
    var serverURL = "https://your-newton-server.com"
    var isConnected = false

    func verify(content: String) async throws -> VerificationResult {
        let url = URL(string: "\(serverURL)/verify")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = ["content": content]
        request.httpBody = try JSONEncoder().encode(body)

        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(VerificationResult.self, from: data)
    }
}

struct VerificationResult: Codable {
    let verified: Bool
    let fingerprint: String
    let elapsed: String
}
```

### Newton-Verified View Pattern

```swift
struct VerifiedInputView: View {
    @State private var input = ""
    @State private var verificationState: LoadingState<VerificationResult> = .idle

    let newton = NewtonClient()

    var body: some View {
        VStack {
            TextField("Enter content to verify", text: $input)
                .textFieldStyle(.roundedBorder)

            Button("Verify with Newton") {
                Task {
                    verificationState = .loading
                    do {
                        let result = try await newton.verify(content: input)
                        verificationState = .success(result)
                    } catch {
                        verificationState = .error(error)
                    }
                }
            }
            .disabled(input.isEmpty)

            LoadingView(state: verificationState) { result in
                VStack {
                    Image(systemName: result.verified ? "checkmark.seal.fill" : "xmark.seal.fill")
                        .font(.largeTitle)
                        .foregroundStyle(result.verified ? .green : .red)
                    Text("Fingerprint: \(result.fingerprint)")
                        .font(.caption)
                        .monospaced()
                }
            }
        }
        .padding()
    }
}
```

### Constraint-First SwiftUI

Apply Newton's "No-First" philosophy to SwiftUI state:

```swift
@Observable
class BankAccount {
    private(set) var balance: Double = 100.0

    // Constraint: balance cannot go negative
    func withdraw(_ amount: Double) throws {
        guard balance - amount >= 0 else {
            throw AccountError.insufficientFunds
        }
        balance -= amount
    }

    enum AccountError: Error {
        case insufficientFunds
    }
}

struct AccountView: View {
    @State private var account = BankAccount()
    @State private var amount = ""
    @State private var error: Error?

    var body: some View {
        Form {
            Section("Balance") {
                Text("$\(account.balance, specifier: "%.2f")")
                    .font(.largeTitle)
            }

            Section("Withdraw") {
                TextField("Amount", text: $amount)
                    .keyboardType(.decimalPad)

                Button("Withdraw") {
                    if let value = Double(amount) {
                        do {
                            try account.withdraw(value)
                            amount = ""
                            error = nil
                        } catch {
                            self.error = error
                        }
                    }
                }
            }

            if let error {
                Section {
                    Text(error.localizedDescription)
                        .foregroundStyle(.red)
                }
            }
        }
    }
}
```

---

## What's New in 2025-2026

### Swift 6.2 (WWDC 2025)

| Feature | What It Does |
|---------|--------------|
| **InlineArray** | Fixed-size arrays on stack, 20-30% faster in loops |
| **Async in defer** | `defer { await cleanup() }` now works |
| **Improved Concurrency** | Async methods inherit actor isolation by default |
| **Runtime Macros** | Inspect macro-generated code at runtime |
| **Ownership** | Better borrowing/ownership for performance |

### SwiftUI for iOS 26

| Feature | What It Does |
|---------|--------------|
| **Liquid Glass** | New translucent material design language |
| **3D Charts** | Swift Charts + RealityKit integration |
| **Rich Text Editor** | Full AttributedString support in TextEditor |
| **10K Lists** | Performance: 10,000 items scrolls smoothly |
| **ToolbarSpacer** | Better toolbar layout control |

### Swift Platform Expansion

```
         ┌─────────────────────────────────────┐
         │            Swift 6.2+               │
         └─────────────────────────────────────┘
                           │
    ┌──────────┬───────────┼───────────┬──────────┐
    ▼          ▼           ▼           ▼          ▼
 ┌──────┐  ┌───────┐  ┌─────────┐  ┌───────┐  ┌────────┐
 │Apple │  │Android│  │ Windows │  │FreeBSD│  │Embedded│
 │(iOS, │  │(daily │  │(VS Code │  │ (14.3+│  │(WASM,  │
 │macOS)│  │builds)│  │support) │  │  )    │  │ IoT)   │
 └──────┘  └───────┘  └─────────┘  └───────┘  └────────┘
```

### @Observable (The New Standard)

**Before (iOS 16-):**
```swift
class OldWay: ObservableObject {
    @Published var name = ""
    @Published var count = 0
}

struct OldView: View {
    @ObservedObject var model: OldWay
    // Every @Published change redraws this view
}
```

**After (iOS 17+):**
```swift
@Observable
class NewWay {
    var name = ""   // Automatically tracked
    var count = 0   // Only redraws if THIS property is used
}

struct NewView: View {
    var model: NewWay  // No property wrapper needed for read-only
    // Only redraws when properties you actually READ change
}
```

---

## Quick Reference Card

### View Hierarchy

```
App
 └── Scene (WindowGroup)
      └── View
           ├── Container (VStack, HStack, ZStack)
           │    └── Views...
           └── Modifiers (.padding, .font, etc.)
```

### State Flow

```
@State (local) ──────┐
                     ▼
              ┌─────────────┐
              │   View      │
              │   body      │
              └─────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
   Child View              Child View
   (read-only)            (@Binding for write)
```

### Common Modifiers Cheat Sheet

```swift
// Layout
.frame(width:height:alignment:)
.padding(_:)
.offset(x:y:)

// Appearance
.font(_:)
.foregroundStyle(_:)
.background(_:)
.opacity(_:)

// Shape
.cornerRadius(_:)
.clipShape(_:)
.shadow(radius:)

// Interaction
.onTapGesture { }
.disabled(_:)
.allowsHitTesting(_:)

// Lifecycle
.onAppear { }
.onDisappear { }
.task { }

// Navigation
.navigationTitle(_:)
.sheet(isPresented:)
.alert(_:isPresented:)
```

### SF Symbols (5000+ Icons)

```swift
// Basic
Image(systemName: "star")
Image(systemName: "star.fill")

// With color
Image(systemName: "heart.fill")
    .foregroundStyle(.red)

// Multicolor
Image(systemName: "cloud.sun.rain.fill")
    .symbolRenderingMode(.multicolor)

// Variable
Image(systemName: "speaker.wave.3.fill", variableValue: volume)
```

### Keyboard Shortcuts (iPad)

| Shortcut | Action |
|----------|--------|
| ⌘R | Run |
| ⌘B | Build |
| ⌘/ | Comment line |
| ⌘[ | Indent left |
| ⌘] | Indent right |
| ⌘⇧O | Quick open |

---

## Further Reading

- [Swift.org](https://swift.org) — Official Swift documentation
- [Apple Developer: SwiftUI](https://developer.apple.com/swiftui/) — Framework reference
- [Hacking with Swift](https://www.hackingwithswift.com/100/swiftui) — 100 Days of SwiftUI
- [Newton API Documentation](../api-reference.md) — Newton integration guide

---

## The Combinations Mindset: A Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR APP                                  │
│                                                             │
│   Values + Views + Containers + Modifiers + State + Actions │
│                                                             │
│   Mix them. Combine them. Break them apart. Recombine.      │
│                                                             │
│   There is no "right order." There are only combinations    │
│   that work for your specific problem.                      │
│                                                             │
│   The playground is your laboratory.                        │
│   Every combination teaches you something.                  │
└─────────────────────────────────────────────────────────────┘
```

**The constraint IS the instruction. The combination IS the program.**

---

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas

*Verified computation at your fingertips.*
