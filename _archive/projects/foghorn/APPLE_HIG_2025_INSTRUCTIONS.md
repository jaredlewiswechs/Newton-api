# Apple Human Interface Guidelines 2025 - AI Design Instructions
## Figma Make System Guidelines for Nina Desktop

> **Last Updated:** February 4, 2026  
> **Based on:** Apple HIG December 2025 (Liquid Glass Update)

---

# General Guidelines

## Core Principles

* **Hierarchy:** Establish clear visual hierarchy where controls elevate above content
* **Harmony:** Align with concentric design language — circles, rounded rectangles, consistent curvature
* **Consistency:** Maintain uniform design that adapts across window sizes and displays

## Layout Rules

* Use responsive layouts with flexbox and grid — avoid absolute positioning unless necessary
* Minimum touch target: **44×44 pt** (60×60 pt for visionOS)
* Prefer 8pt grid system for spacing consistency
* Safe areas must be respected on all edges

## Responsive Behavior

* Design for the content, not the container
* Support Dynamic Type scaling where applicable
* Test at multiple window sizes and text sizes

---

# Liquid Glass Material System (NEW 2025)

## What is Liquid Glass?

Liquid Glass is Apple's 2025 design language that creates a distinct **functional layer** for controls and navigation that floats above the content layer. It provides:

* Dynamic translucency that adapts to underlying content
* Automatic light/dark switching based on background luminance
* Specular highlights and depth effects
* Frosted blur with color passthrough

## Liquid Glass Variants

### Regular Variant
```
Use For: Sidebars, alerts, popovers, components with significant text
Behavior: Blurs and adjusts luminosity for legibility
Scroll Edge: Additional blur and opacity reduction
```

### Clear Variant
```
Use For: Controls over media (photos, videos)
Behavior: Highly translucent, prioritizes background visibility
Dimming: Add 35% dark layer behind if background is bright
```

## Liquid Glass Rules

* ✅ Use for toolbars, tab bars, navigation bars, sidebars
* ✅ Apply sparingly to primary action buttons (one or two per view)
* ✅ Let system components adopt Liquid Glass automatically
* ❌ DO NOT use Liquid Glass in the content layer
* ❌ DO NOT apply color to multiple control backgrounds
* ❌ DO NOT overuse — it should draw attention to content, not distract

## Liquid Glass Color

* Default: No inherent color, takes on colors from content behind
* Tinted: Apply accent color to ONE prominent button per view (e.g., Done button)
* Labels: Prefer monochromatic (adapt light/dark based on background)
* Avoid: Similar colors in button labels if background is colorful

---

# Typography System

## Font Family

* **Primary:** SF Pro (San Francisco Pro)
* **Compact:** SF Compact (watchOS, space-constrained)
* **Serif:** New York (NY) for editorial content
* **Rounded:** SF Pro Rounded for soft UI elements

## Text Style Hierarchy

### macOS Built-in Styles

| Style | Weight | Size | Line Height | Emphasized |
|-------|--------|------|-------------|------------|
| Large Title | Regular | 26pt | 32 | Bold |
| Title 1 | Regular | 22pt | 26 | Bold |
| Title 2 | Regular | 17pt | 22 | Bold |
| Title 3 | Regular | 15pt | 20 | Semibold |
| Headline | Bold | 13pt | 16 | Heavy |
| Body | Regular | 13pt | 16 | Semibold |
| Callout | Regular | 12pt | 15 | Semibold |
| Subheadline | Regular | 11pt | 14 | Semibold |
| Footnote | Regular | 10pt | 13 | Semibold |
| Caption 1 | Regular | 10pt | 13 | Medium |
| Caption 2 | Medium | 10pt | 13 | Semibold |

### iOS/iPadOS Default Sizes

| Style | Weight | Size | Line Height |
|-------|--------|------|-------------|
| Large Title | Regular | 34pt | 41 |
| Title 1 | Regular | 28pt | 34 |
| Title 2 | Regular | 22pt | 28 |
| Title 3 | Regular | 20pt | 25 |
| Body | Regular | 17pt | 22 |
| Callout | Regular | 16pt | 21 |
| Subhead | Regular | 15pt | 20 |
| Footnote | Regular | 13pt | 18 |
| Caption 1 | Regular | 12pt | 16 |
| Caption 2 | Regular | 11pt | 13 |

## Typography Rules

* Minimum readable size: **11pt** (iOS/iPadOS), **10pt** (macOS)
* Avoid font weights: Ultralight, Thin, Light (legibility issues)
* Prefer: Regular, Medium, Semibold, Bold weights
* Use title-style capitalization for button labels
* Start button labels with verbs (e.g., "Add to Cart")

---

# Color System

## System Colors (Light/Dark)

| Color | Light Mode RGB | Dark Mode RGB |
|-------|----------------|---------------|
| Red | 255, 56, 60 | 255, 66, 69 |
| Orange | 255, 141, 40 | 255, 146, 48 |
| Yellow | 255, 204, 0 | 255, 214, 0 |
| Green | 52, 199, 89 | 48, 209, 88 |
| Mint | 0, 200, 179 | 0, 218, 195 |
| Teal | 0, 195, 208 | 0, 210, 224 |
| Cyan | 0, 192, 232 | 60, 211, 254 |
| Blue | 0, 136, 255 | 0, 145, 255 |
| Indigo | 97, 85, 245 | 109, 124, 255 |
| Purple | 203, 48, 224 | 219, 52, 242 |
| Pink | 255, 45, 85 | 255, 55, 95 |
| Brown | 172, 127, 94 | 183, 138, 102 |

## iOS Gray Scale

| Gray Level | Light RGB | Dark RGB |
|------------|-----------|----------|
| Gray | 142, 142, 147 | 142, 142, 147 |
| Gray 2 | 174, 174, 178 | 99, 99, 102 |
| Gray 3 | 199, 199, 204 | 72, 72, 74 |
| Gray 4 | 209, 209, 214 | 58, 58, 60 |
| Gray 5 | 229, 229, 234 | 44, 44, 46 |
| Gray 6 | 242, 242, 247 | 28, 28, 30 |

## Color Usage Rules

* Use system colors via API — don't hardcode hex values
* Provide both light and dark variants for all custom colors
* Provide increased contrast variants for accessibility
* Never use color alone to convey information (accessibility)
* Test colors under various lighting conditions

---

# Button Component

## Best Practices

* Minimum hit region: **44×44 pt**
* Include enough visual padding around buttons
* Always include a press/active state
* Use style (not size) to distinguish button hierarchy

## Button Roles

| Role | Purpose | Appearance |
|------|---------|------------|
| **Primary** | Default/most likely action | Accent color background |
| **Normal** | Standard action | Default styling |
| **Cancel** | Cancel current action | Standard styling |
| **Destructive** | Data destruction action | System red color |

## Button Styling

### Prominent (Primary Action)
```css
background: accent-color (via Liquid Glass tint)
color: white or black (based on contrast)
Use: ONE per section, for main action
```

### Secondary
```css
background: transparent or subtle Liquid Glass
border: 1px accent-color (optional)
Use: Supporting actions alongside primary
```

### Tertiary
```css
background: none
color: accent-color (text only)
Use: Least important actions
```

## Button Content

* Use SF Symbols for icon buttons when possible
* Use title-style capitalization for text labels
* Start labels with verbs: "Add", "Save", "Delete", "Share"
* Add trailing ellipsis (…) if button opens another view/window
* Consider activity indicator for async operations

## macOS Specific Buttons

* **Push Button:** Standard button with rounded corners
* **Square Button:** Symbol-only, used with tables/lists
* **Help Button:** Circular with question mark
* **Image Button:** Custom image/icon button

---

# App Icons

## Specifications by Platform

| Platform | Shape | Final Shape | Size | Layers |
|----------|-------|-------------|------|--------|
| iOS/iPadOS/macOS | Square | Rounded Rectangle | 1024×1024 px | Layered |
| tvOS | Rectangle | Rounded Rectangle | 800×480 px | Parallax |
| visionOS/watchOS | Square | Circular | 1024×1024 px | 3D Layered |

## Icon Design Rules

* Embrace simplicity — capture essence in minimal shapes
* Use filled, overlapping shapes with transparency for depth
* Avoid text unless essential to brand
* Don't replicate UI components or use screenshots
* Prefer vector graphics (SVG/PDF) for layers
* No custom visual effects (system applies dynamically)

## Icon Appearances (iOS/iPadOS/macOS)

1. **Default** — Standard light mode
2. **Dark** — Subdued for dark backgrounds
3. **Clear Light** — Minimal, translucent light
4. **Clear Dark** — Minimal, translucent dark  
5. **Tinted Light** — Single-color tint light
6. **Tinted Dark** — Single-color tint dark

---

# Standard Materials

## Material Thickness (iOS/iPadOS)

| Material | Opacity | Use Case |
|----------|---------|----------|
| **Ultra Thin** | Most transparent | Light overlays |
| **Thin** | Moderate | Partial overlays, light scheme |
| **Regular** | Default | Standard backgrounds |
| **Thick** | Most opaque | Dark scheme overlays |

## Vibrancy Levels

For text/symbols on materials:

| Level | Contrast | Use |
|-------|----------|-----|
| **Label** | Highest | Primary text |
| **Secondary Label** | High | Subheadings, descriptions |
| **Tertiary Label** | Medium | Less important text |
| **Quaternary Label** | Lowest | Watermarks (avoid on thin materials) |

---

# Design System Guidelines for Nina Desktop

## Window Components

### Menu Bar
```
Height: 28px
Background: Liquid Glass (regular variant)
Text: 13pt SF Pro Semibold
Padding: 8px horizontal
```

### Sidebar
```
Width: 240px (collapsible)
Background: Liquid Glass (regular variant) — more opaque
Items: 32px height, 12pt SF Pro
Selected: Accent color highlight with Liquid Glass
Icons: SF Symbols, 16×16pt
```

### Toolbar
```
Height: 44-52px
Background: Liquid Glass (regular variant)
Buttons: 44×44pt minimum touch targets
Spacing: 8pt between items
```

### Dock
```
Height: 56px pill container
Background: Liquid Glass (regular variant)
Icons: 40×40pt in 48×48pt touch target
Corner Radius: Full height / 2 (pill shape)
Position: Centered, floating at bottom
```

## Interaction States

### Hover
```
Scale: 1.0 → 1.05 (subtle)
Background: Slight luminosity shift
Transition: 150ms ease-out
```

### Active/Press
```
Scale: 0.97 (subtle shrink)
Background: Increased opacity
Transition: 100ms ease-in
```

### Focus
```
Ring: 3px accent color outline
Offset: 2px from element
Animation: Subtle pulse (keyboard navigation)
```

### Disabled
```
Opacity: 0.4
Pointer: not-allowed
No hover effects
```

---

# Spacing & Layout Tokens

## Base Grid
```
Unit: 4pt
Small: 4pt (0.25rem)
Medium: 8pt (0.5rem)
Large: 16pt (1rem)
XL: 24pt (1.5rem)
XXL: 32pt (2rem)
```

## Corner Radius Scale
```
Small: 4pt (subtle rounding)
Medium: 8pt (buttons, inputs)
Large: 12pt (cards, windows)
XL: 16pt (modals, large cards)
Pill: 9999pt (full rounding)
```

## Shadows

### Elevation Levels
```css
/* Level 1 — Subtle */
box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);

/* Level 2 — Cards */
box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);

/* Level 3 — Dropdowns */
box-shadow: 0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23);

/* Level 4 — Modals */
box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);

/* Level 5 — Floating Dock */
box-shadow: 0 19px 38px rgba(0,0,0,0.30), 0 15px 12px rgba(0,0,0,0.22);
```

---

# Accessibility Requirements

## Contrast Ratios

* **Normal Text (< 18pt):** 4.5:1 minimum
* **Large Text (≥ 18pt bold or 24pt):** 3:1 minimum
* **UI Components:** 3:1 minimum
* **Focus Indicators:** 3:1 against adjacent colors

## Color Independence

* Never use color alone to convey meaning
* Provide text labels, icons, or patterns as alternatives
* Support Increase Contrast accessibility setting

## Motion

* Respect "Reduce Motion" system setting
* Provide static alternatives for animations
* Avoid flashing content (3 flashes/second max)

## Typography

* Support Dynamic Type sizing
* Minimum touch targets: 44×44pt
* Don't use thin/light font weights at small sizes

---

# Motion & Animation

## Timing Functions

```css
/* Standard easing */
ease-out: cubic-bezier(0.0, 0.0, 0.2, 1)    /* Deceleration */
ease-in: cubic-bezier(0.4, 0.0, 1, 1)       /* Acceleration */
ease-in-out: cubic-bezier(0.4, 0.0, 0.2, 1) /* Standard */

/* Spring-like */
spring: cubic-bezier(0.175, 0.885, 0.32, 1.275)
```

## Duration Guidelines

| Type | Duration | Use Case |
|------|----------|----------|
| Micro | 100ms | Button press, toggle |
| Short | 150-200ms | Hover, small reveals |
| Medium | 250-300ms | Panel slides, modals |
| Long | 400-500ms | Page transitions |

## Animation Rules

* Use purposeful motion that guides attention
* Prefer transforms (translate, scale) over layout changes
* Match motion to real-world physics
* Keep animations subtle — don't distract from content

---

# SF Symbols Integration

## Symbol Weights

Match symbol weight to adjacent text:
* Ultralight, Thin, Light, Regular, Medium, Semibold, Bold, Heavy, Black

## Symbol Sizes

| Context | Symbol Size | Point Size |
|---------|-------------|------------|
| Navigation | Small | 17pt |
| Toolbar | Medium | 22pt |
| Tab Bar | Medium | 24pt |
| Large Display | Large | 32pt+ |

## Rendering Modes

* **Monochrome:** Single color, matches text
* **Hierarchical:** Primary + secondary opacity layers
* **Palette:** Custom multi-color
* **Multicolor:** Apple-defined colors

---

# Quick Reference: CSS Variables

```css
:root {
  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, 'SF Pro', 'Segoe UI', sans-serif;
  --font-size-caption: 10px;
  --font-size-footnote: 11px;
  --font-size-body: 13px;
  --font-size-title3: 15px;
  --font-size-title2: 17px;
  --font-size-title1: 22px;
  --font-size-large-title: 26px;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Corner Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-pill: 9999px;
  
  /* Liquid Glass */
  --glass-blur: 20px;
  --glass-saturation: 180%;
  --glass-bg-light: rgba(255, 255, 255, 0.7);
  --glass-bg-dark: rgba(0, 0, 0, 0.5);
  
  /* System Colors - Light */
  --color-blue: rgb(0, 136, 255);
  --color-green: rgb(52, 199, 89);
  --color-red: rgb(255, 56, 60);
  --color-orange: rgb(255, 141, 40);
  --color-yellow: rgb(255, 204, 0);
  --color-purple: rgb(203, 48, 224);
  
  /* Semantic Colors */
  --color-label: rgba(0, 0, 0, 0.85);
  --color-secondary-label: rgba(0, 0, 0, 0.55);
  --color-tertiary-label: rgba(0, 0, 0, 0.35);
  --color-separator: rgba(0, 0, 0, 0.12);
  --color-background: rgb(242, 242, 247);
}
```

---

## Summary Checklist

Before finalizing any design:

- [ ] Liquid Glass used only for controls/navigation, not content
- [ ] Only ONE prominent colored button per view
- [ ] All touch targets ≥ 44×44pt
- [ ] Text meets contrast requirements (4.5:1 normal, 3:1 large)
- [ ] Color not used alone to convey meaning
- [ ] Light and dark mode variants provided
- [ ] Consistent 8pt grid spacing
- [ ] SF Pro or system fonts used
- [ ] Animations respect Reduce Motion setting
- [ ] Press/hover/focus states defined

---

*Source: [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) — December 2025 Liquid Glass Update*
