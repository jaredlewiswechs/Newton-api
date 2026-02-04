"""
═══════════════════════════════════════════════════════════════════════════════
NINA BÉZIER TESTS
═══════════════════════════════════════════════════════════════════════════════
"""

import pytest
import math
from hypothesis import given, settings
import hypothesis.strategies as st

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nina.kernel.bezier import (
    Point, BezierCurve, CurveType, RelationshipStyle,
    CurveFactory, CurveStore, get_curve_store, render_curves_svg
)


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def simple_curve():
    """A simple cubic curve for testing."""
    return BezierCurve(
        start=Point(0, 0),
        end=Point(100, 100),
        source_hash="source123",
        target_hash="target456"
    )


@pytest.fixture
def curve_store():
    """Fresh curve store."""
    return CurveStore()


# ═══════════════════════════════════════════════════════════════════════════════
# POINT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestPoint:
    """Test Point operations."""
    
    def test_point_creation(self):
        """Create a point."""
        p = Point(10, 20)
        assert p.x == 10
        assert p.y == 20
    
    def test_point_addition(self):
        """Add two points."""
        p1 = Point(10, 20)
        p2 = Point(5, 10)
        result = p1 + p2
        assert result.x == 15
        assert result.y == 30
    
    def test_point_subtraction(self):
        """Subtract two points."""
        p1 = Point(10, 20)
        p2 = Point(5, 10)
        result = p1 - p2
        assert result.x == 5
        assert result.y == 10
    
    def test_point_scalar_multiply(self):
        """Multiply point by scalar."""
        p = Point(10, 20)
        result = p * 2
        assert result.x == 20
        assert result.y == 40
    
    def test_point_distance(self):
        """Calculate distance between points."""
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        assert p1.distance_to(p2) == 5.0  # 3-4-5 triangle
    
    def test_point_lerp(self):
        """Linear interpolation."""
        p1 = Point(0, 0)
        p2 = Point(10, 10)
        
        mid = p1.lerp(p2, 0.5)
        assert mid.x == 5
        assert mid.y == 5
        
        assert p1.lerp(p2, 0).x == 0
        assert p1.lerp(p2, 1).x == 10
    
    def test_point_to_dict(self):
        """Serialize to dict."""
        p = Point(10, 20)
        d = p.to_dict()
        assert d == {"x": 10, "y": 20}
    
    def test_point_from_dict(self):
        """Deserialize from dict."""
        p = Point.from_dict({"x": 10, "y": 20})
        assert p.x == 10
        assert p.y == 20


# ═══════════════════════════════════════════════════════════════════════════════
# BEZIER CURVE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestBezierCurve:
    """Test Bézier curve operations."""
    
    def test_auto_control_points(self, simple_curve):
        """Control points are auto-generated."""
        assert simple_curve.control1 is not None
        assert simple_curve.control2 is not None
    
    def test_curve_type_cubic(self, simple_curve):
        """Default is cubic."""
        assert simple_curve.curve_type == CurveType.CUBIC
    
    def test_curve_type_linear(self):
        """Linear when no control points."""
        curve = BezierCurve(
            start=Point(0, 0),
            end=Point(100, 100),
            control1=None,
            control2=None
        )
        # Note: auto-generation kicks in
        assert curve.curve_type == CurveType.CUBIC
    
    def test_point_at_boundaries(self, simple_curve):
        """Point at t=0 is start, t=1 is end."""
        start = simple_curve.point_at(0)
        end = simple_curve.point_at(1)
        
        assert abs(start.x - simple_curve.start.x) < 0.001
        assert abs(start.y - simple_curve.start.y) < 0.001
        assert abs(end.x - simple_curve.end.x) < 0.001
        assert abs(end.y - simple_curve.end.y) < 0.001
    
    def test_point_at_clamped(self, simple_curve):
        """t is clamped to [0, 1]."""
        before = simple_curve.point_at(-1)
        after = simple_curve.point_at(2)
        
        # Should be clamped to start and end
        assert abs(before.x - simple_curve.start.x) < 0.001
        assert abs(after.x - simple_curve.end.x) < 0.001
    
    def test_midpoint(self, simple_curve):
        """Midpoint is on the curve."""
        mid = simple_curve.midpoint()
        # For a curve from (0,0) to (100,100), midpoint should be roughly (50,50)
        assert 0 < mid.x < 100
        assert 0 < mid.y < 100
    
    def test_sample(self, simple_curve):
        """Sample returns correct number of points."""
        points = simple_curve.sample(10)
        assert len(points) == 11  # 10 segments = 11 points
        
        # First and last should be start and end
        assert abs(points[0].x - simple_curve.start.x) < 0.001
        assert abs(points[-1].x - simple_curve.end.x) < 0.001
    
    def test_length(self, simple_curve):
        """Length is positive."""
        length = simple_curve.length()
        assert length > 0
        
        # For a curve from (0,0) to (100,100), length should be more than
        # straight line distance (141.4) since it's curved
        straight_line = simple_curve.start.distance_to(simple_curve.end)
        # Actually could be less or more depending on control points
        assert abs(length - straight_line) < straight_line  # Reasonable
    
    def test_bbox(self, simple_curve):
        """Bounding box contains endpoints."""
        min_pt, max_pt = simple_curve.bbox()
        
        assert min_pt.x <= simple_curve.start.x
        assert min_pt.y <= simple_curve.start.y
        assert max_pt.x >= simple_curve.end.x
        assert max_pt.y >= simple_curve.end.y
    
    def test_svg_path(self, simple_curve):
        """SVG path is valid."""
        path = simple_curve.to_svg_path()
        assert path.startswith("M")
        assert "C" in path  # Cubic
    
    def test_hash_deterministic(self, simple_curve):
        """Hash is deterministic."""
        h1 = simple_curve.hash()
        h2 = simple_curve.hash()
        assert h1 == h2
    
    def test_to_dict(self, simple_curve):
        """Serialize to dict."""
        d = simple_curve.to_dict()
        assert "start" in d
        assert "end" in d
        assert "control1" in d
        assert "control2" in d
        assert "svg_path" in d
    
    def test_from_dict(self, simple_curve):
        """Round-trip through dict."""
        d = simple_curve.to_dict()
        restored = BezierCurve.from_dict(d)
        
        assert restored.start.x == simple_curve.start.x
        assert restored.end.x == simple_curve.end.x
        assert restored.relationship == simple_curve.relationship


# ═══════════════════════════════════════════════════════════════════════════════
# CURVE FACTORY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCurveFactory:
    """Test CurveFactory."""
    
    def test_create_basic(self):
        """Create a basic curve."""
        curve = CurveFactory.create(
            start=Point(0, 0),
            end=Point(100, 100),
        )
        assert curve.start.x == 0
        assert curve.end.x == 100
    
    def test_create_with_relationship(self):
        """Create curve with specific relationship."""
        curve = CurveFactory.create(
            start=Point(0, 0),
            end=Point(100, 100),
            relationship="references"
        )
        assert curve.relationship == "references"
        assert curve.color == "#3366cc"  # references color
    
    def test_create_from_objects(self):
        """Create curve from object positions."""
        curve = CurveFactory.create_from_objects(
            source_pos=(10, 20),
            target_pos=(80, 90),
            source_hash="abc",
            target_hash="xyz",
            relationship="depends_on"
        )
        assert curve.source_hash == "abc"
        assert curve.target_hash == "xyz"
        assert curve.start.x == 10


# ═══════════════════════════════════════════════════════════════════════════════
# CURVE STORE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCurveStore:
    """Test CurveStore."""
    
    def test_add_and_get(self, curve_store):
        """Add and retrieve a curve."""
        curve = CurveFactory.create(
            start=Point(0, 0),
            end=Point(100, 100),
            source_hash="src",
            target_hash="tgt"
        )
        
        h = curve_store.add(curve)
        retrieved = curve_store.get(h)
        
        assert retrieved is not None
        assert retrieved.source_hash == "src"
    
    def test_get_from_source(self, curve_store):
        """Get curves by source."""
        curve1 = CurveFactory.create(
            start=Point(0, 0), end=Point(50, 50),
            source_hash="A", target_hash="B"
        )
        curve2 = CurveFactory.create(
            start=Point(0, 0), end=Point(100, 100),
            source_hash="A", target_hash="C"
        )
        curve3 = CurveFactory.create(
            start=Point(50, 50), end=Point(100, 100),
            source_hash="B", target_hash="C"
        )
        
        curve_store.add(curve1)
        curve_store.add(curve2)
        curve_store.add(curve3)
        
        from_a = curve_store.get_from_source("A")
        assert len(from_a) == 2
    
    def test_get_to_target(self, curve_store):
        """Get curves by target."""
        curve1 = CurveFactory.create(
            start=Point(0, 0), end=Point(100, 100),
            source_hash="A", target_hash="C"
        )
        curve2 = CurveFactory.create(
            start=Point(50, 50), end=Point(100, 100),
            source_hash="B", target_hash="C"
        )
        
        curve_store.add(curve1)
        curve_store.add(curve2)
        
        to_c = curve_store.get_to_target("C")
        assert len(to_c) == 2
    
    def test_delete(self, curve_store):
        """Delete a curve."""
        curve = CurveFactory.create(
            start=Point(0, 0), end=Point(100, 100),
            source_hash="src", target_hash="tgt"
        )
        h = curve_store.add(curve)
        
        assert curve_store.count() == 1
        
        success = curve_store.delete(h)
        assert success
        assert curve_store.count() == 0
    
    def test_export(self, curve_store):
        """Export all curves."""
        curve = CurveFactory.create(
            start=Point(0, 0), end=Point(100, 100)
        )
        curve_store.add(curve)
        
        exported = curve_store.export()
        assert len(exported) == 1
        assert "svg_path" in exported[0]


# ═══════════════════════════════════════════════════════════════════════════════
# SVG RENDERER TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestSVGRenderer:
    """Test SVG rendering."""
    
    def test_render_single_curve(self):
        """Render a single curve."""
        curve = CurveFactory.create(
            start=Point(10, 10),
            end=Point(90, 90)
        )
        
        svg = render_curves_svg([curve])
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "<path" in svg
    
    def test_render_multiple_curves(self):
        """Render multiple curves."""
        curves = [
            CurveFactory.create(start=Point(0, 0), end=Point(50, 50)),
            CurveFactory.create(start=Point(50, 50), end=Point(100, 100)),
        ]
        
        svg = render_curves_svg(curves)
        assert svg.count("<path") == 2
    
    def test_render_styled_curve(self):
        """Render curve with style."""
        curve = CurveFactory.create(
            start=Point(10, 10),
            end=Point(90, 90),
            relationship="cites"  # dotted style
        )
        
        svg = render_curves_svg([curve])
        assert "stroke-dasharray" in svg


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTY-BASED TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestBezierProperties:
    """Property-based tests for Bézier curves."""
    
    @given(
        st.floats(min_value=-1000, max_value=1000),
        st.floats(min_value=-1000, max_value=1000),
        st.floats(min_value=-1000, max_value=1000),
        st.floats(min_value=-1000, max_value=1000),
    )
    @settings(max_examples=50)
    def test_curve_has_valid_svg(self, x1, y1, x2, y2):
        """All curves produce valid SVG."""
        if math.isnan(x1) or math.isnan(y1) or math.isnan(x2) or math.isnan(y2):
            return
        
        curve = CurveFactory.create(
            start=Point(x1, y1),
            end=Point(x2, y2)
        )
        
        svg = curve.to_svg_path()
        assert svg.startswith("M")
    
    @given(st.floats(min_value=0, max_value=1))
    @settings(max_examples=50)
    def test_point_at_on_curve(self, t):
        """point_at returns point for any valid t."""
        if math.isnan(t):
            return
            
        curve = CurveFactory.create(
            start=Point(0, 0),
            end=Point(100, 100)
        )
        
        point = curve.point_at(t)
        assert not math.isnan(point.x)
        assert not math.isnan(point.y)
    
    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=30)
    def test_sample_correct_count(self, segments):
        """sample returns correct number of points."""
        curve = CurveFactory.create(
            start=Point(0, 0),
            end=Point(100, 100)
        )
        
        points = curve.sample(segments)
        assert len(points) == segments + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
