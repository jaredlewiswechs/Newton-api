# f/g Visual Language Specification
## The Newton Ratio Made Visible

---

## Core Concept

The f/g ratio is Newton's implementation of dimensional analysis:

```
f = forge/fact/function (what you're attempting)
g = ground/goal/governance (what reality allows)

f/g → permission state
```

This document specifies how f/g manifests visually across all aid-a surfaces.

---

## The Glyph

### Basic Form

```
    ┌─────────────────┐
    │                 │
    │    ┌───────┐    │
    │    │       │    │
    │    │   f   │    │ ← Inner circle (intention)
    │    │       │    │
    │    └───────┘    │
    │                 │
    │        g        │ ← Outer circle (boundary)
    │                 │
    └─────────────────┘
```

Two concentric circles:
- **Inner (f)**: Your intention, action, or state
- **Outer (g)**: The constraint boundary, reality, governance

### Ratio Visualization

The relationship between the circles indicates the f/g state:

```
ALLOWED (f/g < 0.9 × threshold)
┌─────────────────┐
│       ───       │  Circles clearly separated
│      ╱   ╲      │  Plenty of room to grow
│     │  f  │     │  GREEN glow
│      ╲   ╱      │
│       ───       │
│                 │
│  ───────────    │
│ ╱           ╲   │
│ │     g     │   │
│ ╲           ╱   │
│  ───────────    │
└─────────────────┘

WARNING (0.9 × threshold ≤ f/g < threshold)
┌─────────────────┐
│                 │  Inner approaching outer
│   ─────────     │  Tension visible
│  ╱    ────  ╲   │  AMBER glow
│ │   ╱    ╲  │   │
│ │   │ f  │  │   │
│ │   ╲    ╱  │   │
│  ╲   ────   ╱   │
│   ─────────     │
│                 │
│        g        │
└─────────────────┘

FORBIDDEN (f/g ≥ threshold)
┌─────────────────┐
│                 │  Inner exceeds outer
│    ┌───────┐    │  Impossible overlap
│   ─│───────│─   │  RED flash
│  ╱ │       │ ╲  │
│ │  │   f   │  │ │
│  ╲ │       │ ╱  │
│   ─│───────│─   │
│    └───────┘    │
│        g        │
└─────────────────┘

UNDEFINED (g ≈ 0)
┌─────────────────┐
│                 │  Outer collapses to point
│                 │  Inner has nowhere to exist
│       ╳         │  RED pulse, "finfr"
│                 │  Ontological death
│                 │
└─────────────────┘
```

---

## Color Specification

### Primary States

| State | f/g Range | Color | Hex | HSL | Meaning |
|-------|-----------|-------|-----|-----|---------|
| Verified | f/g < 0.9θ | Green | `#00C853` | 145, 100%, 39% | Safe margin |
| Warning | 0.9θ ≤ f/g < θ | Amber | `#FFD600` | 50, 100%, 50% | Approaching boundary |
| Forbidden | f/g ≥ θ | Red | `#FF1744` | 348, 100%, 54% | Constraint violated |
| Undefined | g ≈ 0 | Deep Red | `#B71C1C` | 0, 74%, 40% | Ontological death |

### Secondary States

| State | Color | Hex | Use |
|-------|-------|-----|-----|
| Checking | Blue pulse | `#2979FF` | Verification in progress |
| Historical | Silver | `#B0BEC5` | Past states in ledger |
| Proof Available | Blue ring | `#304FFE` | Merkle proof exportable |
| Pristine | White | `#FFFFFF` | Never violated |

### Dark Mode Variants

| Light Mode | Dark Mode | Notes |
|------------|-----------|-------|
| `#00C853` | `#00E676` | Lighter green for contrast |
| `#FFD600` | `#FFEA00` | Brighter amber |
| `#FF1744` | `#FF5252` | Softer red, less aggressive |
| `#B0BEC5` | `#78909C` | Deeper silver |

---

## Animation Specification

### Verification Pulse

When a constraint passes verification:

```
t=0ms     t=50ms    t=100ms   t=150ms   t=200ms
  ○         ⬤         ⬤         ○         ○
 dim      bright    bright     dim       dim
                    +10%       -5%      normal
               (brief overshoot)
```

- Duration: 200ms
- Easing: ease-out
- Overshoot: 10% brightness increase at peak

### Warning Oscillation

When in warning zone (0.9θ ≤ f/g < θ):

```
  slow pulse, 2 second cycle

  ┌──────────────────────────────────────┐
  │                                      │
  │   ○ ─── ○ ─── ● ─── ● ─── ○ ─── ○   │
  │   0     0.5   1.0   1.5   2.0   2.5 s │
  │                                      │
  └──────────────────────────────────────┘
```

- Duration: 2000ms full cycle
- Brightness range: 70% to 100%
- Easing: sine wave

### Forbidden Flash

When a constraint is violated:

```
t=0ms     t=100ms   t=200ms   t=300ms   t=400ms
  ⬤         ○         ⬤         ○         ─
RED      dim       RED       dim      separate
         black               black    circles
```

- Duration: 400ms
- End state: Circles visually separate (showing impossibility)
- Accompanied by haptic error pattern

### Checking Animation

While Newton is verifying:

```
  rotating gradient around the outer circle

    ╱─╲         ─╲╱         ╲─╱         ╱─
   ╱   ╲       ╱   ─       ─   ╲       ╲   ╱
  │  f  │     │  f  │     │  f  │     │  f  │
   ╲   ╱       ╲   ╱       ╱   ╲       ╱   ─
    ╲─╱         ╱─╲       ╲─╱         ─╲╱

  t=0        t=250ms    t=500ms    t=750ms
```

- Duration: 1000ms full rotation
- Color: Blue (`#2979FF`)
- Only shown if verification takes >100ms (rare)

---

## Haptic Patterns

Mapped to iPhone Taptic Engine:

| State | Pattern | UIImpactFeedbackGenerator |
|-------|---------|---------------------------|
| Verified | Single tap | `.light` |
| Warning | Double tap | `.medium` × 2, 100ms gap |
| Forbidden | Buzz | `.heavy` × 3, 50ms gaps |
| Checking | Subtle pulse | `.soft`, repeating 500ms |
| Proof exported | Success | `.success` (system pattern) |

---

## Component Specifications

### Badge Component

```swift
struct FGBadge: View {
    let ratio: Double
    let threshold: Double = 1.0

    var state: FGState {
        if ratio < threshold * 0.9 { return .verified }
        if ratio < threshold { return .warning }
        return .forbidden
    }

    var body: some View {
        ZStack {
            // Outer circle (g)
            Circle()
                .stroke(Color.silver, lineWidth: 2)
                .frame(width: 44, height: 44)

            // Inner circle (f)
            Circle()
                .fill(state.color)
                .frame(width: 44 * ratio, height: 44 * ratio)

            // 1==1 text
            Text("1≡1")
                .font(.system(size: 10, weight: .medium, design: .monospaced))
                .foregroundColor(.white)
        }
    }
}
```

### Indicator Strip

For list views and tables, a minimal indicator strip:

```
┌──────────────────────────────────────────────────────────┐
│ ▌ Account Balance                            $4,523.00  │
│ ▌ Liabilities                                $1,234.00  │
│ ▌ Leverage Ratio                        ●    0.27:1     │
└──────────────────────────────────────────────────────────┘
  ▌ = 4px vertical bar, colored by f/g state
  ● = inline glyph for ratio columns
```

### Timeline Visualization

For Glass Box history view:

```
NOW ─●────────────────────────────────────────────────
     │ f/g = 0.27 ✓
     │
-1hr ─●────────────────────────────────────────────────
     │ f/g = 0.45 ✓ (loan taken)
     │
-2hr ─◐────────────────────────────────────────────────
     │ f/g = 0.89 ⚠ (warning zone)
     │
-3hr ─●────────────────────────────────────────────────
     │ f/g = 0.92 ⚠ → BLOCKED loan attempt
     │ (would have been f/g = 1.23 ✗)
     │
-4hr ─●────────────────────────────────────────────────
     │ f/g = 0.50 ✓ (payment received)
```

---

## Spatial Mapping

### f/g in 3D Space

For AR/VR/spatial computing:

```
                        ABOVE (allowed)
                            ●
                           ╱│╲
                          ╱ │ ╲
                         ╱  │  ╲
     LEFT ───────────── ●───┼───● ─────────────── RIGHT
     (historical)        ╲  │  ╱              (future)
                          ╲ │ ╱
                           ╲│╱
                            ●
                        BELOW (forbidden)

     Height = f/g ratio
     0 = ground plane (f/g = threshold)
     Above = safe zone
     Below = violation zone (unreachable)
```

Objects with good f/g ratios float higher. Objects approaching threshold descend toward the ground. Objects at threshold sit exactly on the ground plane.

---

## Typography in f/g Contexts

### Ratio Display

Always use monospaced font for ratio values:

```
f/g = 0.27     (SF Mono, regular)
f/g ≤ 1.00    (SF Mono, bold for threshold)
f/g → finfr   (SF Mono, italic for undefined)
```

### Constraint Labels

```
law no_overdraft:         (SF Mono, bold)
    when f > g:           (SF Mono, regular)
        finfr             (SF Mono, red, bold)
```

---

## Accessibility

### Color Blind Support

In addition to color, use patterns:

| State | Color | Pattern | Shape |
|-------|-------|---------|-------|
| Verified | Green | Solid | Circle |
| Warning | Amber | Diagonal stripes | Triangle |
| Forbidden | Red | Cross-hatch | Square |

### Screen Reader

VoiceOver announcements:

- "Verified. Ratio 0.27 to 1. Well within limits."
- "Warning. Ratio 0.91 to 1. Approaching threshold of 1."
- "Forbidden. Ratio 1.23 to 1. Exceeds threshold."
- "Undefined. Division by zero. Cannot proceed."

### Reduced Motion

When "Reduce Motion" is enabled:
- Replace animations with instant state changes
- Replace pulses with static glows
- Keep haptic feedback (important for non-visual confirmation)

---

## Platform Implementations

### iOS

```swift
import SwiftUI

enum FGState {
    case verified, warning, forbidden, undefined

    var color: Color {
        switch self {
        case .verified: return Color(hex: "#00C853")
        case .warning: return Color(hex: "#FFD600")
        case .forbidden: return Color(hex: "#FF1744")
        case .undefined: return Color(hex: "#B71C1C")
        }
    }

    var haptic: UIImpactFeedbackGenerator.FeedbackStyle {
        switch self {
        case .verified: return .light
        case .warning: return .medium
        case .forbidden: return .heavy
        case .undefined: return .rigid
        }
    }
}
```

### Web (CSS)

```css
:root {
    --fg-verified: #00C853;
    --fg-warning: #FFD600;
    --fg-forbidden: #FF1744;
    --fg-undefined: #B71C1C;
    --fg-checking: #2979FF;
    --fg-historical: #B0BEC5;
}

.fg-badge {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 200ms ease-out;
}

.fg-badge--verified {
    background: var(--fg-verified);
    box-shadow: 0 0 10px var(--fg-verified);
}

.fg-badge--warning {
    background: var(--fg-warning);
    animation: fg-pulse 2s ease-in-out infinite;
}

.fg-badge--forbidden {
    background: var(--fg-forbidden);
    animation: fg-flash 400ms ease-out;
}

@keyframes fg-pulse {
    0%, 100% { opacity: 0.7; }
    50% { opacity: 1; }
}

@keyframes fg-flash {
    0%, 50% { opacity: 1; transform: scale(1.1); }
    25%, 75% { opacity: 0.3; transform: scale(1); }
    100% { opacity: 1; transform: scale(1); }
}
```

### React Component

```tsx
interface FGBadgeProps {
    f: number;
    g: number;
    threshold?: number;
}

export function FGBadge({ f, g, threshold = 1.0 }: FGBadgeProps) {
    const ratio = g !== 0 ? f / g : Infinity;

    const state = useMemo(() => {
        if (g === 0) return 'undefined';
        if (ratio >= threshold) return 'forbidden';
        if (ratio >= threshold * 0.9) return 'warning';
        return 'verified';
    }, [ratio, threshold, g]);

    return (
        <div className={`fg-badge fg-badge--${state}`}>
            <span className="fg-ratio">
                {g === 0 ? '∞' : ratio.toFixed(2)}
            </span>
        </div>
    );
}
```

---

## Usage Guidelines

### DO

- Use f/g indicators for any constrained value
- Show the ratio numerically when space permits
- Animate transitions between states
- Provide haptic feedback on mobile
- Make the outer circle (g) always visible

### DON'T

- Use f/g colors for non-constraint purposes
- Hide the indicator when space is tight (shrink it instead)
- Show f/g for unconstrained values
- Use red for anything other than forbidden states
- Animate constantly (only on state change)

---

## Summary

The f/g visual language makes mathematical verification tangible. Every color, every animation, every haptic pulse corresponds to a real state in the Newton system.

When users see green, they're seeing truth. When they feel a pulse, they're feeling verification. When they touch an object, they're testing reality.

This isn't just UI. It's the mathematics made visible.

---

*f/g: The ratio of intention to permission.*
*When f/g = 1, you're at the edge of what's possible.*
*When f/g > 1, you've exceeded reality.*
*Newton keeps you honest.*
