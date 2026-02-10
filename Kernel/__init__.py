"""Kernel package — Kernel 120 GUI framework implementation.

Subpackages:
  gui          – Drawing primitives (NSBezierPath, NSColor, NSGradient, NSShadow)
  runtime      – Event system (NSApplication, NSResponder, NSEvent, NSCursor)
  view         – View tree (NSView, NSViewController, scroll/split/stack/grid)
  window       – Windowing (NSWindow, NSWindowController, NSPanel, NSScreen)
  layout       – Auto Layout (NSLayoutConstraint, anchors, layout guides)
  gesture      – Gesture recognizers and tracking areas
  controls     – Controls (NSButton, NSTextField, NSSlider, NSSegmentedControl)
  text         – Text system (NSFont, NSTextView, NSTextStorage, NSLayoutManager)
  data         – Data views (NSTableView, NSOutlineView, NSCollectionView)
  pasteboard   – Pasteboard and drag/drop
  accessibility – Accessibility tree
  menu         – Menus and toolbars
  demo         – FastAPI demo server
"""
__all__ = [
    "gui", "runtime", "view", "window", "layout", "gesture",
    "controls", "text", "data", "pasteboard", "accessibility",
    "menu", "demo",
]
