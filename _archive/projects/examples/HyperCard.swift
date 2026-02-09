// ═══════════════════════════════════════════════════════════════════════════════
// HYPERCARD FOR iPAD
// Swift Playgrounds App - January 2026
//
// Newton Rosetta Cartridge Output
// Fingerprint: 37756A7CE5EF
// Verified: ✓
// ═══════════════════════════════════════════════════════════════════════════════

import SwiftUI
import PencilKit

// MARK: - Data Models

/// A HyperCard stack - a collection of cards
@Observable
class HyperStack: Identifiable {
    let id = UUID()
    var name: String
    var cards: [HyperCard] = []
    var currentCardIndex: Int = 0

    var currentCard: HyperCard? {
        guard cards.indices.contains(currentCardIndex) else { return nil }
        return cards[currentCardIndex]
    }

    init(name: String) {
        self.name = name
        // Start with one blank card
        self.cards = [HyperCard()]
    }

    func addCard() {
        cards.append(HyperCard())
        currentCardIndex = cards.count - 1
    }

    func goToCard(_ index: Int) {
        guard cards.indices.contains(index) else { return }
        currentCardIndex = index
    }

    func nextCard() {
        if currentCardIndex < cards.count - 1 {
            currentCardIndex += 1
        }
    }

    func previousCard() {
        if currentCardIndex > 0 {
            currentCardIndex -= 1
        }
    }
}

/// A single card with background and foreground layers
@Observable
class HyperCard: Identifiable {
    let id = UUID()
    var name: String = "Untitled Card"
    var backgroundDrawing: PKDrawing = PKDrawing()
    var elements: [CardElement] = []
}

/// Elements that can be placed on a card
struct CardElement: Identifiable {
    let id = UUID()
    var kind: ElementKind
    var position: CGPoint
    var size: CGSize
    var content: String
    var targetCardIndex: Int? // For buttons: which card to navigate to

    enum ElementKind: String, CaseIterable {
        case button = "Button"
        case textField = "Text Field"
        case label = "Label"
        case image = "Image"
    }
}

// MARK: - Main App View

struct HyperCardApp: View {
    @State private var stack = HyperStack(name: "My First Stack")
    @State private var isEditing = false
    @State private var showCardList = false
    @State private var selectedElement: CardElement?

    var body: some View {
        NavigationStack {
            ZStack {
                // Card View
                if let card = stack.currentCard {
                    CardView(
                        card: card,
                        stack: stack,
                        isEditing: $isEditing,
                        selectedElement: $selectedElement
                    )
                }

                // Navigation Overlay
                if !isEditing {
                    CardNavigationOverlay(stack: stack)
                }

                // Edit Mode Toolbar
                if isEditing {
                    EditModeToolbar(
                        card: stack.currentCard,
                        selectedElement: $selectedElement,
                        isEditing: $isEditing
                    )
                }
            }
            .navigationTitle(stack.name)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button {
                        showCardList = true
                    } label: {
                        Label("Cards", systemImage: "square.stack")
                    }
                }

                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        isEditing.toggle()
                    } label: {
                        Label(
                            isEditing ? "Done" : "Edit",
                            systemImage: isEditing ? "checkmark.circle.fill" : "pencil"
                        )
                    }
                }
            }
            .sheet(isPresented: $showCardList) {
                CardListView(stack: stack, showCardList: $showCardList)
            }
            .gesture(
                // Long press to enter edit mode
                LongPressGesture(minimumDuration: 0.5)
                    .onEnded { _ in
                        withAnimation {
                            isEditing = true
                        }
                    }
            )
        }
    }
}

// MARK: - Card View

struct CardView: View {
    @Bindable var card: HyperCard
    var stack: HyperStack
    @Binding var isEditing: Bool
    @Binding var selectedElement: CardElement?

    var body: some View {
        ZStack {
            // Background Layer - PencilKit Canvas
            CanvasView(drawing: $card.backgroundDrawing, isEditing: isEditing)

            // Foreground Layer - Interactive Elements
            ForEach(card.elements) { element in
                ElementView(
                    element: element,
                    isEditing: isEditing,
                    isSelected: selectedElement?.id == element.id,
                    onTap: {
                        if isEditing {
                            selectedElement = element
                        } else if element.kind == .button,
                                  let targetIndex = element.targetCardIndex {
                            withAnimation {
                                stack.goToCard(targetIndex)
                            }
                        }
                    },
                    onDrag: { newPosition in
                        if isEditing, let index = card.elements.firstIndex(where: { $0.id == element.id }) {
                            card.elements[index].position = newPosition
                        }
                    }
                )
            }
        }
    }
}

// MARK: - PencilKit Canvas

struct CanvasView: UIViewRepresentable {
    @Binding var drawing: PKDrawing
    var isEditing: Bool

    func makeUIView(context: Context) -> PKCanvasView {
        let canvas = PKCanvasView()
        canvas.drawing = drawing
        canvas.tool = PKInkingTool(.pen, color: .black, width: 5)
        canvas.backgroundColor = .systemBackground
        canvas.drawingPolicy = .anyInput
        canvas.delegate = context.coordinator
        return canvas
    }

    func updateUIView(_ canvas: PKCanvasView, context: Context) {
        canvas.isUserInteractionEnabled = isEditing
        canvas.drawing = drawing

        // Show/hide tool picker based on edit mode
        if isEditing {
            if let window = canvas.window {
                let toolPicker = PKToolPicker.shared(for: window)
                toolPicker?.setVisible(true, forFirstResponder: canvas)
                toolPicker?.addObserver(canvas)
                canvas.becomeFirstResponder()
            }
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(drawing: $drawing)
    }

    class Coordinator: NSObject, PKCanvasViewDelegate {
        @Binding var drawing: PKDrawing

        init(drawing: Binding<PKDrawing>) {
            _drawing = drawing
        }

        func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
            drawing = canvasView.drawing
        }
    }
}

// MARK: - Element View

struct ElementView: View {
    let element: CardElement
    let isEditing: Bool
    let isSelected: Bool
    let onTap: () -> Void
    let onDrag: (CGPoint) -> Void

    @State private var dragOffset: CGSize = .zero

    var body: some View {
        elementContent
            .frame(width: element.size.width, height: element.size.height)
            .position(
                x: element.position.x + dragOffset.width,
                y: element.position.y + dragOffset.height
            )
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(isSelected ? Color.blue : Color.clear, lineWidth: 2)
            )
            .onTapGesture(perform: onTap)
            .gesture(
                isEditing ?
                DragGesture()
                    .onChanged { value in
                        dragOffset = value.translation
                    }
                    .onEnded { value in
                        let newPosition = CGPoint(
                            x: element.position.x + value.translation.width,
                            y: element.position.y + value.translation.height
                        )
                        onDrag(newPosition)
                        dragOffset = .zero
                    }
                : nil
            )
    }

    @ViewBuilder
    var elementContent: some View {
        switch element.kind {
        case .button:
            Button(action: onTap) {
                Text(element.content)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
            .disabled(isEditing)

        case .textField:
            TextField("Enter text", text: .constant(element.content))
                .textFieldStyle(.roundedBorder)
                .disabled(!isEditing)

        case .label:
            Text(element.content)
                .padding()
                .background(Color.secondary.opacity(0.2))
                .cornerRadius(8)

        case .image:
            Image(systemName: "photo")
                .resizable()
                .aspectRatio(contentMode: .fit)
                .foregroundColor(.secondary)
        }
    }
}

// MARK: - Card Navigation Overlay

struct CardNavigationOverlay: View {
    var stack: HyperStack

    var body: some View {
        HStack {
            // Previous Card
            Button {
                withAnimation {
                    stack.previousCard()
                }
            } label: {
                Image(systemName: "chevron.left.circle.fill")
                    .font(.system(size: 44))
                    .foregroundStyle(.secondary)
            }
            .opacity(stack.currentCardIndex > 0 ? 1 : 0.3)
            .disabled(stack.currentCardIndex == 0)

            Spacer()

            // Card Counter
            Text("\(stack.currentCardIndex + 1) / \(stack.cards.count)")
                .font(.caption)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(.ultraThinMaterial)
                .cornerRadius(16)

            Spacer()

            // Next Card
            Button {
                withAnimation {
                    stack.nextCard()
                }
            } label: {
                Image(systemName: "chevron.right.circle.fill")
                    .font(.system(size: 44))
                    .foregroundStyle(.secondary)
            }
            .opacity(stack.currentCardIndex < stack.cards.count - 1 ? 1 : 0.3)
            .disabled(stack.currentCardIndex >= stack.cards.count - 1)
        }
        .padding(.horizontal, 20)
        .frame(maxHeight: .infinity, alignment: .center)
    }
}

// MARK: - Edit Mode Toolbar

struct EditModeToolbar: View {
    var card: HyperCard?
    @Binding var selectedElement: CardElement?
    @Binding var isEditing: Bool

    var body: some View {
        VStack {
            Spacer()

            HStack(spacing: 16) {
                // Add Button
                ToolbarButton(icon: "button.horizontal", label: "Button") {
                    addElement(.button, content: "Tap Me")
                }

                // Add Text Field
                ToolbarButton(icon: "textformat", label: "Text") {
                    addElement(.textField, content: "")
                }

                // Add Label
                ToolbarButton(icon: "text.alignleft", label: "Label") {
                    addElement(.label, content: "Label")
                }

                // Add Image
                ToolbarButton(icon: "photo", label: "Image") {
                    addElement(.image, content: "")
                }

                Divider()
                    .frame(height: 40)

                // Delete Selected
                ToolbarButton(icon: "trash", label: "Delete") {
                    deleteSelectedElement()
                }
                .disabled(selectedElement == nil)
                .opacity(selectedElement != nil ? 1 : 0.4)
            }
            .padding()
            .background(.ultraThinMaterial)
            .cornerRadius(16)
            .padding()
        }
    }

    func addElement(_ kind: CardElement.ElementKind, content: String) {
        guard let card = card else { return }

        let newElement = CardElement(
            kind: kind,
            position: CGPoint(x: 200, y: 300),
            size: CGSize(width: 120, height: 44),
            content: content,
            targetCardIndex: nil
        )

        card.elements.append(newElement)
        selectedElement = newElement
    }

    func deleteSelectedElement() {
        guard let card = card,
              let selected = selectedElement,
              let index = card.elements.firstIndex(where: { $0.id == selected.id }) else { return }

        card.elements.remove(at: index)
        selectedElement = nil
    }
}

struct ToolbarButton: View {
    let icon: String
    let label: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.title2)
                Text(label)
                    .font(.caption2)
            }
            .frame(width: 60)
        }
    }
}

// MARK: - Card List View

struct CardListView: View {
    var stack: HyperStack
    @Binding var showCardList: Bool

    var body: some View {
        NavigationStack {
            List {
                ForEach(Array(stack.cards.enumerated()), id: \.element.id) { index, card in
                    Button {
                        stack.goToCard(index)
                        showCardList = false
                    } label: {
                        HStack {
                            Image(systemName: "rectangle.portrait")
                                .foregroundColor(.secondary)

                            VStack(alignment: .leading) {
                                Text(card.name)
                                    .font(.headline)
                                Text("Card \(index + 1)")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }

                            Spacer()

                            if index == stack.currentCardIndex {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.blue)
                            }
                        }
                    }
                    .foregroundColor(.primary)
                }
            }
            .navigationTitle("Cards")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Done") {
                        showCardList = false
                    }
                }

                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        stack.addCard()
                    } label: {
                        Label("Add Card", systemImage: "plus")
                    }
                }
            }
        }
    }
}

// MARK: - App Entry Point

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            HyperCardApp()
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// NEWTON VERIFICATION
// ═══════════════════════════════════════════════════════════════════════════════
//
// when hypercard_app:
//     and platform == ipados
//     and frameworks contains SwiftUI
//     and frameworks contains PencilKit
//     and has_card_navigation
//     and has_edit_mode
//     and has_element_placement
//     and no_security_violations
// fin hypercard_verified
//
// f/g ratio: 1.0 (all constraints satisfied)
// Fingerprint: 37756A7CE5EF
// Generated: 2026-01-04
// ═══════════════════════════════════════════════════════════════════════════════
