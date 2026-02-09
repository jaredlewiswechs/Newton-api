# Newton GUI Design Guide

**January 4, 2026** · **Jared Nashon Lewis** · **Ada Computing Company** · **Houston, Texas**

---

## The Magic: How Newton Speaks macOS

Newton's cartridge system maps directly to Apple's platform architecture. This guide shows you how to visualize Newton in **Figma** or **Canva**, understand the underlying magic, and extend the system.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NEWTON → macOS MAPPING                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   NEWTON CARTRIDGE              macOS / COCOA                               │
│   ════════════════              ════════════════                            │
│                                                                              │
│   Visual Cartridge    ───────►  AppKit / SwiftUI Views                     │
│                                 Core Graphics, Core Animation              │
│                                 Metal (GPU rendering)                       │
│                                                                              │
│   Sound Cartridge     ───────►  AVFoundation                                │
│                                 Core Audio, AudioToolbox                    │
│                                 MIDI, Audio Units                           │
│                                                                              │
│   Sequence Cartridge  ───────►  AVFoundation (video)                        │
│                                 Core Animation                              │
│                                 SpriteKit, SceneKit                         │
│                                                                              │
│   Data Cartridge      ───────►  Core Data, SwiftData                        │
│                                 CloudKit, Foundation                        │
│                                                                              │
│   Rosetta Cartridge   ───────►  Swift Compiler                              │
│                                 Xcode Build System                          │
│                                                                              │
│   Physics Cartridge   ───────►  SpriteKit Physics                           │
│                                 SceneKit Physics                            │
│                                 GameplayKit                                 │
│                                                                              │
│   AI Cartridge        ───────►  GameplayKit (GKBehavior, GKAgent)          │
│                                 Core ML, Create ML                          │
│                                                                              │
│   Input Cartridge     ───────►  GameController framework                    │
│                                 AppKit Events, UIKit Gestures              │
│                                                                              │
│   Network Cartridge   ───────►  GameKit (multiplayer)                       │
│                                 Network.framework, MultipeerConnectivity   │
│                                                                              │
│   Haptic Cartridge    ───────►  Core Haptics                                │
│                                 UIFeedbackGenerator (iOS)                   │
│                                                                              │
│   Save Cartridge      ───────►  FileManager, UserDefaults                   │
│                                 CloudKit, Game Center                       │
│                                                                              │
│   Locale Cartridge    ───────►  Foundation Localization                     │
│                                 String Catalogs, Bundle                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Designing in Figma: The Newton Way

### Step 1: Understand the Cartridge → Component Mapping

When you design in Figma, every frame, component, and style maps to a Newton cartridge:

```
FIGMA ELEMENT                    NEWTON CARTRIDGE           macOS COMPONENT
═══════════════                  ════════════════           ═══════════════

Frame / Artboard        ───────► Visual Cartridge   ───────► NSWindow / View
  └─ Auto Layout                   └─ Layout Spec            └─ StackView

Component               ───────► Visual Cartridge   ───────► NSView subclass
  └─ Variants                      └─ State Spec             └─ @State

Color Style             ───────► Visual Cartridge   ───────► NSColor / Asset
  └─ Light/Dark                    └─ Palette Spec           └─ .primary

Text Style              ───────► Visual Cartridge   ───────► NSFont
  └─ SF Pro                        └─ Typography             └─ .title

Effect (Shadow)         ───────► Visual Cartridge   ───────► NSShadow
  └─ Drop shadow                   └─ Effects Spec           └─ .shadow()

Prototype Link          ───────► Sequence Cartridge ───────► NavigationStack
  └─ Transitions                   └─ Transition Spec        └─ .animation()

Interactive Component   ───────► Input Cartridge    ───────► Gesture/Action
  └─ Hover states                  └─ Event Spec             └─ .onTapGesture
```

### Step 2: Create Your Newton Design System in Figma

```
📁 NEWTON DESIGN SYSTEM (Figma File Structure)
│
├── 📄 Cover
│
├── 📁 🎨 Foundation (Visual Cartridge)
│   ├── Colors
│   │   ├── Primary Palette      → Visual.palette
│   │   ├── Semantic Colors      → Visual.style.color_scheme
│   │   └── Dark Mode Variants   → Visual.style.theme
│   │
│   ├── Typography
│   │   ├── SF Pro Display       → Visual.style.typography
│   │   ├── SF Pro Text
│   │   └── SF Mono
│   │
│   ├── Spacing
│   │   └── 8pt Grid             → Visual.viewBox
│   │
│   └── Effects
│       ├── Shadows              → Visual.style.effects
│       ├── Blurs
│       └── Gradients            → Visual.elements["gradient"]
│
├── 📁 🧩 Components (All Cartridges)
│   │
│   ├── 🔲 Containers            → Visual Cartridge
│   │   ├── Card
│   │   ├── Panel
│   │   └── Modal
│   │
│   ├── 🎛️ Controls              → Input Cartridge
│   │   ├── Button
│   │   ├── Toggle
│   │   ├── Slider
│   │   └── Picker
│   │
│   ├── 📊 Data Display          → Data Cartridge
│   │   ├── Chart
│   │   ├── Table
│   │   └── List
│   │
│   ├── 🔔 Feedback              → Haptic + Sound Cartridge
│   │   ├── Alert
│   │   ├── Toast
│   │   └── Progress
│   │
│   └── 🎮 Game Elements         → Game Cartridges
│       ├── HUD                  → Visual + Economy
│       ├── Minimap              → World + Visual
│       ├── Inventory            → Economy + Visual
│       └── Dialogue Box         → Narrative + Visual
│
├── 📁 🖥️ Screens (Composed)
│   ├── Onboarding               → Sequence + Visual
│   ├── Main Menu                → Input + Visual + Sound
│   ├── Game View                → All Game Cartridges
│   ├── Settings                 → Save + Locale + Input
│   └── Multiplayer Lobby        → Network + Visual
│
└── 📁 📖 Documentation
    ├── Cartridge Mapping
    ├── Constraint Reference
    └── Export Specs
```

---

## The Magic: How Newton Informs Your Design

### Understanding Constraints as Design Decisions

When you design in Figma/Canva, Newton's constraints become your design guardrails:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONSTRAINT → DESIGN DECISION                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  NEWTON CONSTRAINT                 YOUR DESIGN DECISION                     │
│  ═════════════════                 ════════════════════                     │
│                                                                              │
│  Visual.dimensions.max: 4096      "My canvas won't exceed 4K"               │
│                                    → Design for retina, not infinite        │
│                                                                              │
│  Visual.elements.max: 1000        "Keep UI elements manageable"             │
│                                    → Paginate, virtualize long lists        │
│                                                                              │
│  Visual.colors.max: 256           "Limit my palette"                        │
│                                    → Use semantic colors, not arbitrary     │
│                                                                              │
│  Sound.duration.max: 5min         "Audio must be focused"                   │
│                                    → Loop ambient, one-shot effects         │
│                                                                              │
│  Sound.frequency.max: 22050Hz     "Respect hearing safety"                  │
│                                    → No ultrasonic/subsonic abuse           │
│                                                                              │
│  Sequence.fps.max: 120            "Animation has bounds"                    │
│                                    → 60fps is plenty, save battery          │
│                                                                              │
│  Input.deadzone.min: 0.0          "Controllers need tolerance"              │
│                                    → Always add dead zones in Figma mockup  │
│                                                                              │
│  Network.tick_rate.max: 128       "Multiplayer has physics"                 │
│                                    → Design for latency, show predictions   │
│                                                                              │
│  Economy.inflation_rate.max: 1.0  "Economy must be balanced"                │
│                                    → Show sinks and faucets in UI           │
│                                                                              │
│  Particle.max: 100000             "Effects have limits"                     │
│                                    → Design for LOD, use sprites at distance│
│                                                                              │
│  Haptic.duration.max: 5000ms      "Vibration is brief"                      │
│                                    → Indicate haptic feedback in prototypes │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Canva Workflow: Rapid Prototyping with Newton

### For Quick Game UI Mockups

```
CANVA ELEMENT                NEWTON MAPPING                EXPORT TO
═════════════                ══════════════                ═════════

Rectangle                    Visual.elements["rect"]       SwiftUI Rectangle
  → Corner radius: 12        Visual.style.corner_radius    .cornerRadius(12)
  → Fill: gradient           Visual.elements["gradient"]   LinearGradient

Text                         Visual.elements["text"]       SwiftUI Text
  → Font: Inter Bold         Visual.style.typography       .font(.title)
  → Size: 24                  Visual.spec.font_size         .bold()

Image                        Visual.elements["image"]      SwiftUI Image
  → Placeholder              Visual.spec.placeholder        AsyncImage

Icon (from Elements)         Visual.elements["path"]       SF Symbols
  → Search: "play"           Visual.style.icons             Image(systemName:)

Button (from Elements)       Input Cartridge               SwiftUI Button
  → Primary style            Input.mappings.actions         .buttonStyle()

Chart (from Elements)        Data Cartridge                Swift Charts
  → Bar chart                Data.visualizations["bar"]     Chart { }
```

### Newton-Informed Canva Template

Create a Canva template with these pages:

```
PAGE 1: 🎮 GAME HUD
├── Health Bar               → Economy.progression.health
├── Currency Display         → Economy.currencies[0].display
├── Minimap Frame            → World.streaming.minimap
├── Objective Text           → Narrative.quests.current
└── Control Hints            → Input.mappings.hints

PAGE 2: 📊 INVENTORY
├── Grid Layout              → Economy.items.display_grid
├── Item Slot                → Economy.items.slot
├── Rarity Border Colors     → Economy.items.rarities
│   ├── Common: #888888
│   ├── Uncommon: #00FF00
│   ├── Rare: #0088FF
│   ├── Epic: #AA00FF
│   └── Legendary: #FFAA00
├── Item Count Badge         → Economy.items.stack
└── Selection Highlight      → Input.mappings.select

PAGE 3: 💬 DIALOGUE
├── Speaker Portrait         → Narrative.dialogue.speaker
├── Dialogue Box             → Narrative.dialogue.box
├── Choice Buttons           → Narrative.dialogue.choices
├── Continue Indicator       → Input.mappings.confirm
└── Skip Button              → Input.mappings.cancel

PAGE 4: ⚙️ SETTINGS
├── Volume Sliders           → Sound.spec.volume
├── Graphics Quality         → Visual.spec.quality
├── Control Rebinding        → Input.settings.rebinding
├── Language Picker          → Locale.target_languages
├── Accessibility Toggle     → Locale.accessibility
└── Save/Load Buttons        → Save.slots
```

---

## The Complete Picture: Newton → Figma → Xcode

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE NEWTON DESIGN PIPELINE                           │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │    INTENT    │   "Create an iOS roguelike with pixel art"
     │  (Your Idea) │
     └──────┬───────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NEWTON CARTRIDGES                                  │
│                                                                              │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│   │ Visual  │ │  Sound  │ │ Physics │ │   AI    │ │ Economy │              │
│   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘              │
│        │           │           │           │           │                    │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│   │  Input  │ │  World  │ │Narrative│ │Particle │ │  Save   │              │
│   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘              │
│        │           │           │           │           │                    │
│        └───────────┴───────────┴───────────┴───────────┘                    │
│                                │                                             │
│                    ┌───────────▼───────────┐                                │
│                    │   VERIFIED SPECS      │                                │
│                    │   (~15KB JSON)        │                                │
│                    └───────────┬───────────┘                                │
│                                │                                             │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
            ▼                    ▼                    ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│      FIGMA        │ │      CANVA        │ │      XCODE        │
│                   │ │                   │ │                   │
│  Design System    │ │  Quick Mockups    │ │  Implementation   │
│  Components       │ │  Presentations    │ │  SwiftUI Views    │
│  Prototypes       │ │  Marketing        │ │  Game Logic       │
│                   │ │                   │ │                   │
│  ┌─────────────┐  │ │  ┌─────────────┐  │ │  ┌─────────────┐  │
│  │ Import JSON │  │ │  │ Use Template│  │ │  │ Parse Specs │  │
│  │ Specs       │  │ │  │ Styles      │  │ │  │ Generate    │  │
│  └─────────────┘  │ │  └─────────────┘  │ │  │ Code        │  │
│                   │ │                   │ │  └─────────────┘  │
└─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     FINAL GAME        │
                    │                       │
                    │  • Verified by Newton │
                    │  • Designed in Figma  │
                    │  • Built in Swift     │
                    │  • Runs on macOS/iOS  │
                    │                       │
                    └───────────────────────┘
```

---

## macOS/Cocoa Framework Mapping

### Visual Cartridge → AppKit/SwiftUI

```swift
// Newton Visual Spec
let visualSpec = visual.compile(
    intent: "Game HUD with health bar and score",
    width: 1920,
    height: 1080
)

// Maps to SwiftUI
struct GameHUD: View {
    // From Visual.palette
    let colors = visualSpec.spec["palette"] as! [String]

    // From Visual.elements
    var body: some View {
        ZStack {
            // Visual.elements["rect"] → Rectangle
            Rectangle()
                .fill(Color(hex: colors[0]))

            // Visual.elements["text"] → Text
            Text("Score: 0")
                .font(.system(
                    size: visualSpec.spec["style"]["font_size"]
                ))
        }
        .frame(
            width: visualSpec.spec["width"],
            height: visualSpec.spec["height"]
        )
    }
}
```

### Physics Cartridge → SpriteKit/SceneKit

```swift
// Newton Physics Spec
let physicsSpec = physics.compile(
    intent: "2D platformer with wall jumping",
    gravity: 20.0
)

// Maps to SpriteKit
class GameScene: SKScene {
    override func didMove(to view: SKView) {
        // From Physics.simulation.gravity
        physicsWorld.gravity = CGVector(
            dx: physicsSpec.spec["simulation"]["gravity"]["x"],
            dy: physicsSpec.spec["simulation"]["gravity"]["y"]
        )

        // From Physics.character
        let player = SKSpriteNode()
        player.physicsBody = SKPhysicsBody(
            rectangleOf: CGSize(
                width: physicsSpec.spec["character"]["capsule"]["radius"] * 2,
                height: physicsSpec.spec["character"]["capsule"]["height"]
            )
        )

        // From Physics.character.movement
        player.physicsBody?.friction =
            physicsSpec.spec["materials"][0]["friction"]
    }
}
```

### Input Cartridge → GameController

```swift
// Newton Input Spec
let inputSpec = input.compile(
    intent: "Action RPG with gamepad and keyboard support",
    genre: "rpg"
)

// Maps to GameController
import GameController

class InputManager {
    func setupControllers() {
        // From Input.mappings.gamepad
        let gamepadMapping = inputSpec.spec["mappings"]["gamepad"]

        GCController.controllers().forEach { controller in
            controller.extendedGamepad?.buttonA.pressedChangedHandler = { _, _, pressed in
                if pressed {
                    // gamepadMapping["buttons"]["a"] = "jump"
                    self.performAction(gamepadMapping["buttons"]["a"])
                }
            }
        }

        // From Input.settings
        let deadzone = inputSpec.spec["settings"]["stick_deadzone"]
    }
}
```

### AI Cartridge → GameplayKit

```swift
// Newton AI Spec
let aiSpec = ai.compile(
    intent: "Enemy guard that patrols and chases player",
    reaction_time_ms: 300
)

// Maps to GameplayKit
import GameplayKit

class EnemyEntity: GKEntity {
    override init() {
        super.init()

        // From AI.behavior_tree
        let behaviorTree = aiSpec.spec["behavior_tree"]

        // From AI.state_machine
        let states = aiSpec.spec["state_machine"]["states"]
        let stateMachine = GKStateMachine(states: [
            IdleState(),
            PatrolState(),
            ChaseState()
        ])

        // From AI.perception
        let agent = GKAgent2D()
        agent.maxSpeed = Float(aiSpec.spec["perception"]["sight"]["range"])

        addComponent(GKSKNodeComponent(node: spriteNode))
    }
}
```

### Network Cartridge → GameKit

```swift
// Newton Network Spec
let networkSpec = network.compile(
    intent: "4 player co-op dungeon crawler",
    max_players: 4
)

// Maps to GameKit
import GameKit

class MultiplayerManager: NSObject, GKMatchDelegate {
    var match: GKMatch?

    func findMatch() {
        let request = GKMatchRequest()

        // From Network.connection.max_players
        request.maxPlayers = networkSpec.spec["connection"]["max_players"]
        request.minPlayers = 2

        // From Network.matchmaking
        let matchmaking = networkSpec.spec["matchmaking"]
        // matchmaking["algorithm"] = "quick_match"
    }

    func sendGameState(_ state: GameState) {
        // From Network.connection.tick_rate
        let tickRate = networkSpec.spec["connection"]["tick_rate"]

        // From Network.synchronization
        let interpolationDelay = networkSpec.spec["synchronization"]["interpolation_delay_ms"]
    }
}
```

### Haptic Cartridge → Core Haptics

```swift
// Newton Haptic Spec
let hapticSpec = haptic.compile(
    intent: "Weapon impact feedback",
    intensity: 0.8,
    duration_ms: 100
)

// Maps to Core Haptics
import CoreHaptics

class HapticManager {
    var engine: CHHapticEngine?

    func playImpact() {
        // From Haptic.patterns[0]
        let pattern = hapticSpec.spec["patterns"][0]

        let intensity = CHHapticEventParameter(
            parameterID: .hapticIntensity,
            value: Float(pattern["intensity"])
        )
        let sharpness = CHHapticEventParameter(
            parameterID: .hapticSharpness,
            value: Float(pattern["sharpness"])
        )

        let event = CHHapticEvent(
            eventType: .hapticTransient,
            parameters: [intensity, sharpness],
            relativeTime: 0
        )

        try? engine?.makePlayer(with: CHHapticPattern(
            events: [event],
            parameters: []
        )).start(atTime: 0)
    }
}
```

---

## Figma Plugin Concept: Newton Spec Importer

```javascript
// Figma Plugin: Import Newton Specs

figma.showUI(__html__, { width: 400, height: 600 });

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'import-visual-spec') {
        const spec = msg.spec;

        // Create frame from Visual spec
        const frame = figma.createFrame();
        frame.resize(spec.width, spec.height);
        frame.name = `Newton: ${spec.intent_hash}`;

        // Apply palette
        const colors = spec.palette;
        colors.forEach((hex, i) => {
            const style = figma.createPaintStyle();
            style.name = `Newton/Color${i + 1}`;
            style.paints = [{ type: 'SOLID', color: hexToRgb(hex) }];
        });

        // Create elements
        spec.elements.forEach(elem => {
            let node;
            switch (elem) {
                case 'rect':
                    node = figma.createRectangle();
                    break;
                case 'circle':
                    node = figma.createEllipse();
                    break;
                case 'text':
                    node = figma.createText();
                    break;
            }
            frame.appendChild(node);
        });

        figma.viewport.scrollAndZoomIntoView([frame]);
    }
};
```

---

## Quick Reference: Cartridge → macOS API

| Newton Cartridge | Primary macOS Framework | Secondary Frameworks |
|------------------|-------------------------|----------------------|
| Visual | SwiftUI, AppKit | Core Graphics, Metal |
| Sound | AVFoundation | Core Audio, AudioToolbox |
| Sequence | AVFoundation | Core Animation, SpriteKit |
| Data | SwiftData, Core Data | CloudKit, Foundation |
| Rosetta | Swift Compiler | Xcode Build System |
| Physics | SpriteKit, SceneKit | GameplayKit |
| AI | GameplayKit | Core ML, Create ML |
| Input | GameController | AppKit Events |
| Network | GameKit | Network.framework |
| Economy | StoreKit | SwiftData |
| Narrative | Foundation | AVSpeechSynthesizer |
| World | SpriteKit, SceneKit | GameplayKit |
| Particle | SpriteKit | SceneKit, Metal |
| Haptic | Core Haptics | UIKit |
| Save | FileManager | CloudKit, UserDefaults |
| Locale | Foundation | String Catalogs |

---

## Summary: The Creator's Workflow

### Jared's Design Process

1. **Write Intent** → "Create a cozy farming game with seasons"

2. **Newton Compiles** → All 11 cartridges generate specs
   ```
   Visual:    Pixel art palette, 320x240 upscaled
   Sound:     Ambient farm sounds, seasonal music
   Physics:   2D tile-based, simple collision
   AI:        NPC schedules, animal behavior
   Economy:   Crops, seasons, shipping
   Narrative: Friendship system, events
   World:     Procedural farm layout, seasons
   Particle:  Rain, snow, leaves, dust
   Haptic:    Tool impacts, harvest feedback
   Save:      Daily autosave, cloud sync
   Locale:    10 languages, seasonal text
   ```

3. **Design in Figma** → Import specs, create components

4. **Prototype in Canva** → Quick mockups for marketing

5. **Build in Xcode** → Rosetta generates Swift code

6. **Ship to App Store** → Newton verified, Apple approved

---

*"The constraint IS the design. The specification IS the interface. Newton IS the creative partner."*

**© 2025-2026 Ada Computing Company · Houston, Texas**
