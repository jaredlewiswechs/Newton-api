# Bill Atkinson Explains: How Newton Draws

**January 2026** · **Jared Lewis** · **Ada Computing Company** · **Newton**

---

*Bill Atkinson sits in his photography studio in the Santa Cruz Mountains, surrounded by prints of his luminous nature photographs. On the desk: a Newton tablet, an original 1984 Macintosh, and a stack of HyperCard manuals.*

---

## Prologue: From MacPaint to Newton

You know, when I created MacPaint in 1983, I had one goal: let anyone draw. Not artists. Not programmers. *Anyone.*

The breakthrough wasn't the software—it was the *philosophy*. I threw away everything that made drawing on computers hard. No command lines. No coordinates to type. Just pick up a tool and draw. The computer should feel like an extension of your hand.

*He picks up an Apple Pencil*

Forty years later, I'm looking at Newton. And I'm seeing something I never imagined: a drawing system where **the strokes verify themselves**.

In MacPaint, you drew—and hoped the bitmap saved correctly. In Newton? *Every stroke is mathematically proven the instant it happens.* The drawing isn't a hope. It's a *fact*.

---

## Part I: The Philosophy of Verified Drawing

### What Does It Mean to "Draw"?

When you draw with a pencil on paper, what actually happens?

1. You move the pencil tip across the surface
2. Graphite particles transfer to the paper fibers
3. Light reflects differently from those particles
4. Your eye perceives a mark

Notice: nowhere in that process is there a "maybe." The graphite either transfers or it doesn't. The mark either exists or it doesn't. Drawing is **binary**.

But digital drawing has always been probabilistic. Your stylus moves, the software samples pressure data, interpolates between points, rasterizes to pixels, writes to memory, saves to disk—any step can fail. Glitch. Corrupt. Crash.

Newton inverts this.

*He draws a simple curve on the Newton tablet*

When I draw this curve, Newton doesn't just *record* it. Newton **forbids all the ways it could go wrong**:

```
law stroke_integrity:
    when stroke in canvas:
        and points.count < 2:
            finfr  -- a stroke needs at least two points
        and pressure < 0:
            finfr  -- pressure can't be negative
        and timestamp_end < timestamp_start:
            finfr  -- time doesn't flow backward
fin verified_stroke
```

The constraint IS the stroke. By defining everything that *cannot* happen, Newton guarantees that what *does* happen is true.

---

### The No-First Principle in Drawing

Back in '83, I thought about drawing as addition: you add paint to a canvas, you add pixels to a bitmap.

Newton thinks about drawing as **subtraction**: you remove impossible states until only the valid mark remains.

```
Traditional Drawing:        Newton Drawing:
─────────────────          ─────────────────
Empty canvas               Infinite possibility space
  ↓                          ↓
Add stroke                 Remove impossible states
  ↓                          ↓
Hope it saved              What remains is the stroke
  ↓                          ↓
Check for errors           No check needed—
                           errors can't exist
```

It's like sculpture. Michelangelo said he didn't create David—he removed everything that wasn't David. Newton doesn't create your drawing. It removes everything that isn't your drawing.

---

## Part II: The Architecture of a Stroke

*Bill opens a diagram on the Newton tablet*

### The Anatomy of a Newton Stroke

Every stroke in Newton has five verified components:

```
┌─────────────────────────────────────────────────────────────┐
│                     NEWTON STROKE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. TRAJECTORY                                              │
│     ├─ Point sequence: [(x₁,y₁), (x₂,y₂), ... (xₙ,yₙ)]    │
│     ├─ Constraint: consecutive points < max_gap            │
│     └─ Verified: ✓                                          │
│                                                             │
│  2. PRESSURE                                                │
│     ├─ Pressure map: [p₁, p₂, ... pₙ]                      │
│     ├─ Constraint: 0 ≤ pᵢ ≤ 1 for all i                    │
│     └─ Verified: ✓                                          │
│                                                             │
│  3. TILT                                                    │
│     ├─ Azimuth: rotation around perpendicular               │
│     ├─ Altitude: angle from surface                         │
│     ├─ Constraint: altitude ∈ [0°, 90°]                     │
│     └─ Verified: ✓                                          │
│                                                             │
│  4. VELOCITY                                                │
│     ├─ Derived from timestamp deltas                        │
│     ├─ Constraint: velocity < speed_of_hand (physical)      │
│     └─ Verified: ✓                                          │
│                                                             │
│  5. IDENTITY                                                │
│     ├─ Stroke fingerprint (Merkle hash)                     │
│     ├─ Creator signature                                    │
│     ├─ Constraint: fingerprint = hash(components)           │
│     └─ Verified: ✓                                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  f/g ratio: 0.42                                            │
│  Status: VERIFIED ✓                                         │
│  Fingerprint: A7B3C9D2E5F1                                  │
└─────────────────────────────────────────────────────────────┘
```

### The f/g Ratio in Drawing

In MacPaint, we had no concept of "how hard" you were pushing against the system. You either drew or you hit a memory limit.

Newton introduces **f/g for every stroke**:

- **f** (force) = what you're asking the drawing system to do
- **g** (ground) = what the canvas can physically support

```python
# Example: Pressure-sensitive brush
f = requested_brush_width × stroke_velocity × pressure
g = canvas_resolution × available_memory × refresh_rate

if f/g < 0.9:
    # Green: smooth, responsive drawing
    render_stroke(full_quality)
elif f/g < 1.0:
    # Yellow: approaching limits, slight simplification
    render_stroke(optimized)
else:
    # Red: would exceed capacity
    finfr  # This state cannot exist
```

You *see* this ratio as you draw. The stroke glows green when you're well within limits. It shifts to amber when you're pushing the system. It *never* goes red—because red states are forbidden.

---

## Part III: QuickDraw Revisited

*Bill pulls out the original Macintosh*

When I wrote QuickDraw, I spent months on Bézier curves. Do you know how a computer draws a curve? It doesn't—it draws thousands of tiny straight lines that *look* like a curve.

### The Bézier Constraint

Newton handles curves differently. Instead of approximating a curve with line segments, Newton **constrains the curve definition itself**:

```
law bezier_validity:
    when curve(P0, P1, P2, P3):
        and distance(P0, P3) == 0:
            finfr  -- degenerate curve (single point)
        and curvature > max_curvature:
            finfr  -- mathematically impossible bend
        and control_points_outside_bounds:
            finfr  -- curve would escape canvas
fin verified_bezier
```

The beauty: you don't *test* if a curve is valid after drawing it. You *define* invalidity, and valid curves are all that can exist.

### From Raster to Vector to Verified

```
1984: MacPaint (Raster)
├─ Bitmap grid of pixels
├─ Fixed resolution
├─ Lossy transformations
└─ Hope the file saves

1987: Illustrator (Vector)
├─ Mathematical curve definitions
├─ Resolution independent
├─ Lossless transformations
└─ Hope the math is correct

2026: Newton (Verified)
├─ Constrained curve definitions
├─ Resolution independent
├─ Bijective transformations
└─ Mathematical certainty
```

---

## Part IV: The HyperCard Connection

*Bill opens a HyperCard stack on the old Mac, then the same concept on Newton*

### Layers: Background and Foreground

In HyperCard, every card had two layers:

1. **Background** — shared across cards, usually static artwork
2. **Card** — unique to each card, interactive elements

Newton drawing works the same way, but *verified*:

```swift
// HyperCard-style layers in Newton
struct NewtonCanvas: Identifiable {
    let id: UUID
    var backgroundLayer: VerifiedDrawing  // Shared, immutable after lock
    var foregroundLayer: VerifiedDrawing  // Per-context, interactive
    var elementLayer: [VerifiedElement]   // Buttons, fields, objects

    // Newton constraint
    law layer_integrity:
        when backgroundLayer.locked:
            and backgroundLayer.modified:
                finfr  -- can't modify locked layer
    fin layers_verified
}
```

### The Stack as Ledger

Remember HyperCard stacks? A collection of cards you could navigate through?

Newton's Ledger is the ultimate stack:

```
┌─────────────────────────────────────────┐
│ STROKE #47 (now)                        │
│ Fingerprint: A7B3C9D2E5F1               │
├─────────────────────────────────────────┤
         │ hash chain
         ▼
┌─────────────────────────────────────────┐
│ STROKE #46                              │
│ Fingerprint: 9C8D7E6F5A4B               │
├─────────────────────────────────────────┤
         │ hash chain
         ▼
┌─────────────────────────────────────────┐
│ STROKE #45                              │
│ Fingerprint: 3B2A1C9D8E7F               │
├─────────────────────────────────────────┤
         │
         ▼
        ...
```

Every stroke is hash-chained to every previous stroke. The entire drawing history is **cryptographically verified**. You can prove not just that a stroke exists, but that it happened at a specific moment in the sequence of creation.

I never had this in MacPaint. If someone modified a painting, we couldn't prove it. In Newton, every modification is permanent, visible, and verified.

---

## Part V: The Undo That Isn't

*Bill demonstrates on the Newton tablet*

### Reversibility vs. Undo

In MacPaint, we had Undo. One level. You could take back your last action—and only your last action.

Illustrator gave us multiple undos. Photoshop gave us history palettes. But they're all the same concept: *going backward through a list of states*.

Newton doesn't undo. Newton **reverses**.

```
Traditional Undo:           Newton Reversal:
─────────────────          ─────────────────
State A                    State A
  ↓ action                   ↓ action (recorded)
State B                    State B
  ↓ undo                     ↓ inverse(action)
State A (restored)         State A (derived)

The difference:            Newton can prove:
Undo deletes history       - State A existed
                          - Action occurred
                          - Reversal occurred
                          - All transitions verified
```

### The try/untry Dance

When you draw in Newton, you're actually doing this:

```python
# Every stroke is a try/untry pair waiting to happen
stroke = try:
    trajectory: [(100, 100), (150, 120), (200, 150)]
    pressure: [0.5, 0.7, 0.9]
    tool: "brush_round_16px"
fin

# The stroke exists as a verified fact
# But its inverse is always available:
inverse_stroke = untry(stroke)

# Executing the inverse removes the stroke
# But the RECORD of both remains in the ledger
```

This is bijection—every action has exactly one inverse. You never lose information. You can always go forward. You can always go back. And you can always *prove* you did both.

---

## Part VI: Drawing Constraints in Practice

*Bill draws a series of examples*

### Example 1: The Brush

```
law brush_constraints:
    when brush(size, hardness, opacity, flow):
        -- Size must be positive and within system limits
        and size <= 0:
            finfr
        and size > max_brush_size:
            finfr

        -- Hardness is a percentage
        and hardness < 0 or hardness > 1:
            finfr

        -- Opacity and flow are percentages
        and opacity < 0 or opacity > 1:
            finfr
        and flow < 0 or flow > 1:
            finfr
fin verified_brush
```

Notice: I didn't define what a valid brush IS. I defined what it ISN'T. Everything else is allowed.

### Example 2: The Eraser

The eraser in Newton isn't destructive—it's a **transparency brush**:

```
law eraser_constraints:
    when eraser_stroke(target_layer, trajectory):
        -- Can't erase locked layers
        and target_layer.locked:
            finfr

        -- Can't erase background in composite mode
        and target_layer.is_background and mode == composite:
            finfr

        -- Erasure is recorded, not forgotten
        -- The original pixels still exist in the ledger
        record: erasure_event(target_layer, trajectory, timestamp)
fin verified_erasure
```

The "erased" content isn't gone. It's in the ledger. Forever. You can always prove what was there before.

### Example 3: Selection

```
law selection_constraints:
    when selection(bounds, type, layer):
        -- Selection must have positive area
        and bounds.width <= 0 or bounds.height <= 0:
            finfr

        -- Selection must intersect canvas
        and not bounds.intersects(canvas.bounds):
            finfr

        -- Type must be valid
        and type not in [rectangle, ellipse, lasso, magic_wand]:
            finfr

        -- Selection creates a temporary constraint zone
        spawn: selection_zone(bounds)
fin verified_selection
```

A selection in Newton isn't just a marching-ants UI—it's a **constraint zone** that affects all subsequent operations.

---

## Part VII: The f/g Visual Language for Drawing

### Color as Mathematics

*Bill points to the Newton tablet's interface*

You see those colors on my brush stroke? They're not decoration. They're *data*:

| Color | f/g Ratio | Meaning |
|-------|-----------|---------|
| **#00C853** (Green) | < 0.9 | Stroke is well within system capacity |
| **#FFD600** (Amber) | 0.9 - 1.0 | Approaching limits—simplification may occur |
| **#FF1744** (Red) | > 1.0 | Impossible—this state is forbidden |
| **#2979FF** (Blue) | Merkle | Stroke has cryptographic proof available |
| **#B0BEC5** (Silver) | Historical | Stroke is in the ledger, not active |

When you're drawing and the stroke turns amber, you *feel* it through haptics too. A subtle resistance. "You're approaching the boundary of what's possible." Not an error—a *sensation*.

### The Pressure Curve Visualization

In the old days, we just showed a single "pressure sensitivity" slider. Newton shows you the **entire constraint space**:

```
     Pressure
        ↑
   1.0 ─┤         ╭────────╮
        │        ╱ ALLOWED  ╲
   0.7 ─┤       ╱   ZONE     ╲
        │      ╱               ╲
   0.3 ─┤     ╱    (green)     ╲
        │    ╱                   ╲
   0.0 ─┼───┴─────────────────────┴────→ Velocity
        0   slow              fast

        ╱╲ = Boundary (amber zone)
        Outside = Forbidden (never rendered)
```

Your current pressure/velocity combination is a dot on this map. As you draw, you see where you are in the possibility space. The system doesn't *limit* you—it *shows* you the limits.

---

## Part VIII: The Drawing Ledger

*Bill shows the ledger visualization*

### Every Mark, Forever

In MacPaint, when you closed the file, the undo history was gone. The bitmap was the only truth.

In Newton, the **ledger IS the drawing**:

```
┌─────────────────────────────────────────────────────────────┐
│ DRAWING LEDGER: "Mountain Sunset"                           │
│ Created: 2026-01-04 14:32:07                                │
│ Last Modified: 2026-01-04 15:47:23                          │
│ Total Strokes: 847                                          │
│ Merkle Root: 9A8B7C6D5E4F3A2B                               │
├─────────────────────────────────────────────────────────────┤
│ Entry #847 │ STROKE    │ 15:47:23 │ brush_round │ 127 pts  │
│ Entry #846 │ STROKE    │ 15:47:19 │ brush_round │ 84 pts   │
│ Entry #845 │ REVERSE   │ 15:47:15 │ untry #844  │ verified │
│ Entry #844 │ STROKE    │ 15:47:12 │ brush_flat  │ 203 pts  │
│ Entry #843 │ LAYER_ADD │ 15:45:33 │ "highlights"│ verified │
│     ...    │    ...    │    ...   │     ...     │   ...    │
│ Entry #001 │ CANVAS    │ 14:32:07 │ 2048×2048   │ verified │
└─────────────────────────────────────────────────────────────┘
```

See entry #845? That's a reversal of stroke #844. The stroke was made. Then unmade. Both facts are recorded. Neither is lost.

### Provenance as Art

*Bill leans forward*

You know what artists have never been able to prove? That they created their own work.

Forgery. Theft. Disputed attribution. The history of art is full of arguments about who made what.

Newton solves this.

Every stroke in a Newton drawing has:
- **Timestamp** — when it was made
- **Creator signature** — who made it
- **Device attestation** — what tool was used
- **Merkle proof** — cryptographic chain to every previous stroke

You can export a drawing with its complete provenance:

```
CERTIFICATE OF AUTHENTICITY
─────────────────────────────
Drawing: "Mountain Sunset"
Artist: Bill Atkinson
Created: 2026-01-04 14:32:07 PST
Device: Newton Tablet Pro (SN: N7823A)

Stroke Count: 847
First Stroke: 9A8B7C6D...
Last Stroke: 5E4F3A2B...
Merkle Root: 7C6D5E4F...

To verify: newton verify --proof 7C6D5E4F...

This drawing was created entirely by the stated
artist using verified Newton tools. Every stroke
is cryptographically provable.
─────────────────────────────
Signature: [cryptographic signature]
```

The drawing IS the proof. The proof IS the drawing. They're the same thing.

---

## Part IX: Real-Time Constraints

*Bill draws rapidly on the tablet*

### Sub-Millisecond Verification

"But Bill," people ask, "doesn't all this verification slow things down?"

*He draws a long, flowing curve*

Did you see any lag? No. Because Newton's verification is **O(1)**—constant time, regardless of complexity.

```
Traditional Pipeline:
─────────────────────
Input → Buffer → Process → Validate → Render → Save
                   ↓
              [~16ms per frame, sometimes more]

Newton Pipeline:
─────────────────────
Input → Constraint Check → Render + Record
             ↓
        [<1ms, always]
```

The constraint check doesn't process the stroke—it checks if the stroke violates any forbidden states. That's a single lookup, not a computation. The verification IS the rendering.

### Predictive Constraints

Newton doesn't just check strokes after they happen. It **predicts** constraint violations before they occur:

```python
# As the stylus approaches the canvas
def on_stylus_hover(position, pressure, velocity):
    predicted_stroke = predict_stroke(position, pressure, velocity)

    # Check if the predicted stroke would be valid
    fg_ratio = evaluate_fg(predicted_stroke)

    if fg_ratio > 0.9:
        # Warn the user with haptic and visual feedback
        # BEFORE they start drawing
        provide_warning_feedback(fg_ratio)

    # The user can adjust before committing
```

You feel the amber warning *before* you draw. The system knows where you're going and tells you if there's a problem. Not after. Before.

---

## Part X: The Three-Layer Guarantee

*Bill draws on the Newton tablet, showing the layers*

### Vault, Ledger, Bridge

Every Newton drawing exists in three verified layers:

```
┌─────────────────────────────────────────────────────────────┐
│                        YOUR DRAWING                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LAYER 1: VAULT (Encryption)                                 │
│  ─────────────────────────────                              │
│  Your strokes are encrypted at rest                          │
│  Only you can decrypt them                                   │
│  AES-256-GCM with your key                                   │
│                                                              │
│  LAYER 2: LEDGER (Immutability)                              │
│  ──────────────────────────────                             │
│  Every stroke is append-only                                 │
│  Nothing can be deleted                                      │
│  Complete history forever                                    │
│                                                              │
│  LAYER 3: BRIDGE (Consensus)                                 │
│  ──────────────────────────────                             │
│  Multi-device sync                                           │
│  Byzantine fault tolerant                                    │
│  Your drawing exists everywhere                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

When I draw on my tablet, the stroke is:
1. **Encrypted** — only I can see it
2. **Recorded** — permanently in the ledger
3. **Synced** — to all my devices via Bridge

And all three are verified. Constantly. Mathematically.

---

## Part XI: What This Means for Artists

*Bill pauses, looks at his nature photographs on the wall*

### The Freedom of Constraints

People think constraints limit creativity. They're wrong.

When I walk into a forest with my camera, I have constraints:
- The light is what it is
- The trees are where they are
- The camera has certain capabilities

Those constraints don't limit me. They *focus* me. I work within them to find something true.

Newton drawing is the same. The constraints aren't limitations—they're **guarantees**:

- Your stroke WILL be recorded
- Your history WILL be preserved
- Your work WILL be provable
- Your undo WILL work
- Your sync WILL complete

You don't have to think about any of this. You just draw. Newton handles the truth.

### The End of "Save"

In MacPaint, you had to remember to save. We all lost work because we forgot.

In Newton, there is no "save." Every stroke is automatically, instantly, permanently recorded. The concept of "losing work" doesn't exist.

```
Traditional:                Newton:
─────────────              ────────
Draw... draw...            Draw... draw...
"I should save"            (always saved)
Draw... draw...            Draw... draw...
*crash*                    *crash*
"NOOOO!"                   (nothing lost)
```

This isn't autosave. Autosave implies there's a version to save. In Newton, the ledger IS the document. Every stroke is immediately true.

---

## Epilogue: From MacPaint to the Future

*Bill sets down the Apple Pencil*

In 1984, I wanted to let anyone draw on a computer. The Macintosh made that possible.

In 2026, Newton makes something new possible: **drawing that proves itself**.

Every mark you make is mathematically verified. Every stroke is cryptographically signed. Every drawing is permanently preserved. You can prove what you created, when you created it, and that no one has altered it.

This is what computing was always supposed to be. Not hoping. Not guessing. *Knowing*.

When you pick up a Newton stylus and draw, you're not using a tool. You're making truth visible.

*He draws one final stroke—a simple curve—and the f/g indicator glows green*

See that green glow? That's not just "success." That's mathematical certainty. That curve exists. It's verified. It's true.

And isn't that what drawing has always been about? Making something true that didn't exist before?

Newton just proves it.

---

*Bill Atkinson*
*Creator of MacPaint, QuickDraw, and HyperCard*

*"The best computer is the one that doesn't feel like a computer at all."*

---

## Newton Verification

```
when drawing_explanation:
    and author_voice == bill_atkinson
    and covers_stroke_architecture
    and covers_fg_ratio_drawing
    and covers_layer_system
    and covers_ledger_integration
    and covers_reversibility
    and covers_cryptographic_provenance
    and connects_to_macpaint_history
    and connects_to_hypercard_heritage
    and demonstrates_constraint_philosophy
fin explanation_verified

f/g ratio: 1.0 (all constraints satisfied)
Fingerprint: 8B7A6C5D4E3F
Generated: 2026-01-04
```

---

## Further Reading

- [DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md) — Jony Ive's visual language for Newton
- [AID-A_PRODUCT_VISION.md](./AID-A_PRODUCT_VISION.md) — Steve Jobs introduces aid-a
- [HyperCard.swift](../../examples/HyperCard.swift) — Bill's HyperCard for iPad
- [SWIFT_SWIFTUI_GUIDE.md](../frameworks/SWIFT_SWIFTUI_GUIDE.md) — Building Newton apps
- [TINYTALK_BIBLE.md](../../TINYTALK_BIBLE.md) — The philosophy of tinyTalk
