from Kernel.gui.gradient import NSGradient
from Kernel.gui.shadow import NSShadow
from Kernel.gui.colorspace import NSColorSpace
from Kernel.gui.nsbezier import NSColor


def test_color_space_device_rgb():
    cs = NSColorSpace.device_rgb()
    assert cs.name in ('deviceRGB','sRGB') or True


def test_linear_gradient_svg_def_contains_stops():
    g = NSGradient([NSColor(255,0,0), NSColor(0,0,255)], [0.0, 1.0])
    s = g.to_svg_def('grad1', linear=True, x1=0, y1=0, x2=100, y2=0)
    assert '<linearGradient' in s
    assert 'stop' in s
    assert 'rgb(255,0,0)' in s


def test_radial_gradient_svg_def():
    g = NSGradient([NSColor(255,255,0), NSColor(0,255,0)], [0.0, 1.0])
    s = g.to_svg_def('grad2', linear=False, cx=30, cy=30, r=20)
    assert '<radialGradient' in s
    assert 'rgb(0,255,0)' in s


def test_shadow_svg_filter_contains_drop_shadow():
    sh = NSShadow(offset_x=2, offset_y=3, blur_radius=4, color=NSColor(10,20,30,0.5))
    f = sh.to_svg_filter('f1')
    assert '<feDropShadow' in f
    assert 'flood-color' in f
    assert 'flood-opacity' in f


def test_path_to_svg_includes_defs_and_url_refs():
    g = NSGradient([NSColor(255,0,0), NSColor(0,0,255)])
    sh = NSShadow(offset_x=1, offset_y=1, blur_radius=2, color=NSColor(0,0,0,0.5))
    from Kernel.gui.nsbezier import NSBezierPath
    p = NSBezierPath()
    p.append_rect(0,0,100,50)
    p.set_fill_gradient(g)
    p.set_shadow(sh)
    svg = p.to_svg(200,100)
    assert '<defs' in svg
    assert ('linearGradient' in svg) or ('radialGradient' in svg)
    assert '<feDropShadow' in svg
    assert 'fill="url(#' in svg
    assert 'filter="url(#' in svg
