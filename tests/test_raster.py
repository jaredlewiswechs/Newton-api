import pytest
from Kernel.gui.nsbezier import sample_star


def test_rasterize_png_bytes():
    cairosvg = pytest.importorskip('cairosvg')
    from Kernel.gui.raster import rasterize_to_png_bytes
    s = sample_star(cx=50, cy=50, r1=30, r2=12)
    s.stroke(width=2)
    png = rasterize_to_png_bytes(s, width=100, height=100)
    assert png[:8] == b'\x89PNG\r\n\x1a\n'
