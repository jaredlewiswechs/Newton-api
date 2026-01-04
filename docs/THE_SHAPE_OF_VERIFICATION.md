# The Shape of Verification

**January 4, 2026** · **Jared Nashon Lewis** · **Newton** · **Ada Computing Company**

> *"I'm in love with the shape of you"*
> — Ed Sheeran, 2017

---

## The Primitive

```
1 == 1 → execute
1 != 1 → halt

Everything else is application.
```

---

## Every Pixel is a Graph

A pixel is not a colored dot. A pixel is a **node** in a constraint graph.

```
         ┌─────────────────────────────────────────┐
         │              THE PIXEL                  │
         │                                         │
         │    ┌─────┐     ┌─────┐     ┌─────┐     │
         │    │  R  │────▶│  G  │────▶│  B  │     │
         │    │  e  │     │  r  │     │  l  │     │
         │    │  d  │     │  e  │     │  u  │     │
         │    │     │     │  e  │     │  e  │     │
         │    │  ⊗  │     │  n  │     │     │     │
         │    │     │     │     │     │  ✓  │     │
         │    └─────┘     └─────┘     └─────┘     │
         │                                         │
         │   forbidden   warning    verified       │
         └─────────────────────────────────────────┘
```

Every pixel has three states. Every pixel IS the verification result.

---

## The Shape

What is a shape? A shape is the **boundary** between what's inside and what's outside.

```
                    ╭─────────────────────╮
                   ╱                       ╲
                  │                         │
                  │         ┌───┐           │
                  │         │ f │           │     f = what you want
                  │         │   │           │     g = what's allowed
                  │         └───┘           │
                  │                         │     f/g = THE SHAPE
                  │                         │
                   ╲                       ╱
                    ╰─────────────────────╯
                              g
```

The **f/g ratio** is the shape of verification:

| Ratio | Color | State | Meaning |
|-------|-------|-------|---------|
| f/g < 0.9θ | `#00C853` Green | Verified | Inside the shape |
| 0.9θ ≤ f/g < θ | `#FFD600` Amber | Warning | Approaching the edge |
| f/g ≥ θ | `#FF1744` Red | Forbidden | Outside the shape |
| g ≈ 0 | `#B71C1C` Deep Red | finfr | No shape exists |

---

## The Music

Ed Sheeran understood the math:

```
"I'm in love with the shape of you"
         ↓
    f/g < θ → verified

"We push and pull like a magnet do"
         ↓
    constraint propagation

"Your love was handmade for somebody like me"
         ↓
    constraints crafted for domains

"Come on now, follow my lead"
         ↓
    1 == 1 → execute

"Although my heart is falling too"
         ↓
    signal drifting toward boundary
```

---

## The Pixel-Graph-RGB Trinity

```
PIXEL          GRAPH              RGB
  │               │                │
  │               │                │
  ▼               ▼                ▼
state    →    constraint    →    color
  │               │                │
  │               │                │
  ▼               ▼                ▼
position  →    f/g ratio    →   #RRGGBB
```

**Every pixel is a graph node.**
**Every graph node has a verification state.**
**Every verification state is a color.**

This is the trinity:
- **PIXEL**: The atomic unit of visual computation
- **GRAPH**: The constraint relationships
- **RGB**: The truth encoded in light

---

## The QuickDraw Connection

Bill Atkinson (1984): Pixels are coordinates in a 65,535 × 65,535 space.

Newton (2026): Words are coordinates in a 4,096 semantic space.

```
QuickDraw:  0 ─────────────────────────── 65,535
                        │
                     origin

Newton:     0 ─── 1024 ─── 2048 ─── 3072 ─── 4095
                   │       │       │
                   │  CRYSTALLINE  │
                   │     ZONE      │
                   └───────────────┘
```

Bill drew pixels. Newton draws meaning.

---

## The Primitive Visualization

```python
def verify(f, g, theta=1.0):
    """
    The shape of verification.

    f: what you want (intention)
    g: what's allowed (constraint)
    theta: the threshold (the edge)

    Returns: RGB color of truth
    """
    if g == 0:
        return "#B71C1C"  # finfr - no shape exists

    ratio = f / g

    if ratio >= theta:
        return "#FF1744"  # RED - outside the shape
    elif ratio >= 0.9 * theta:
        return "#FFD600"  # AMBER - approaching edge
    else:
        return "#00C853"  # GREEN - inside the shape
```

---

## The Algorithm of Attraction

```
The club isn't the best place to find a lover
    → Random sampling is inefficient

So the bar is where I go
    → Constrained search space

Me and my friends at the table doing shots
    → Parallel constraint propagation

Take my hand, stop, put Van the Man on the jukebox
    → 1 == 1 → execute

And then we start to dance
    → System verified, state transitions begin

I'm in love with the shape of you
    → f/g < θ → VERIFIED
```

---

## The Demo

At 6 PM, you show them this:

1. **A single pixel** on screen
2. **It's red** (forbidden state)
3. **You adjust constraints** (f or g)
4. **It turns amber** (approaching boundary)
5. **You verify** (1 == 1)
6. **It turns green** (verified)

That's the whole computer. That's the whole demo.

```
RED → AMBER → GREEN

That's Newton.
That's the shape.
That's verification.
```

---

## The Synthesis

| Ed Sheeran | Newton | Math |
|------------|--------|------|
| Shape | f/g boundary | Constraint topology |
| Love | Verification | 1 == 1 |
| Body | State | Variable bindings |
| Push and pull | Propagation | Arc consistency |
| Follow my lead | Execute | State transition |
| Heart falling | Signal drift | Approaching θ |

---

## The Final Form

Every pixel is a graph.
Every graph is RGB.
Every RGB is verification state.

The shape IS the constraint.
The love IS the verification.
The body IS the state.

```
1 == 1 → GREEN → EXECUTE → LOVE
1 != 1 → RED   → HALT    → finfr
```

---

## Tell Steve Jobs

Tell him the pixel was always a graph.
Tell him Bill Atkinson knew.
Tell him the Macintosh was a constraint machine.
Tell him Newton is the same math, forty years later.

Tell him:

```
The primitive is simple:
1 == 1 → execute
1 != 1 → halt

Everything else is application.
```

---

*© 2026 Ada Computing Company · Houston, Texas*

**"I'm in love with the shape of you"** — verification is love.

**finfr.**
