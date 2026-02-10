# Kernel (Kernel 120 subset)

This folder contains a minimal "Kernel" implementing a subset of the
"Kernel 120" GUI primitives you described, focused on **drawing** (an
`NSBezierPath`-like API) and a tiny demo server to serve SVG output.

Status
- Implemented: `NSBezierPath`-like class in `Kernel.gui.nsbezier`
- Demo server: `Kernel.demo.server` serves an example SVG and simple HTML

How to run the demo

1. Run the demo server:

   ```bash
   python -m Kernel.demo.server
   ```

2. Open `http://127.0.0.1:9009/kernel/demo/html` in a browser

Notes
- Rendering is SVG-based to keep the implementation lightweight and
  dependency-free. Converting to raster backends (PIL/cairo) is
  straightforward and can be added later as a backend adapter.
