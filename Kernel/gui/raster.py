"""Raster adapter for Kernel NSBezierPath using CairoSVG when available.

This module provides a simple bridge that converts an NSBezierPath -> SVG
(using the existing `to_svg`) and then renders that SVG to PNG bytes via
`cairosvg`.

If `cairosvg` is not available, functions will raise ImportError with a
helpful message.
"""
from typing import Optional


def rasterize_to_png_bytes(path, width: int = 400, height: int = 400, background: Optional[str] = None) -> bytes:
    try:
        import cairosvg
    except Exception as e:
        raise ImportError("cairosvg is required to rasterize paths to PNG. Install with `pip install cairosvg`.") from e

    svg = path.to_svg(width=width, height=height)
    # Optionally, wrap with background rect if requested
    if background:
        svg = svg.replace('<svg', f'<svg style="background:{background};"', 1)
    png_bytes = cairosvg.svg2png(bytestring=svg.encode('utf-8'), output_width=width, output_height=height)
    return png_bytes
