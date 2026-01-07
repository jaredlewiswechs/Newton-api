#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
Tests for Newton Constraint Compositor
═══════════════════════════════════════════════════════════════════════════════

The compositor SOLVES instead of stacks. Every frame is a (layout, proof) tandem.
If constraints cannot be satisfied, nothing renders—finfr.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from newton.tinytalk import (
    LawViolation,
    Rect,
    Color,
    BLACK,
    WHITE,
    VisualElement,
    NoOverlap,
    NoOverlapGroup,
    MinContrast,
    FullyVisible,
    RelativePosition,
    EvenSpacing,
    MinSize,
    AspectRatio,
    ConstraintPriority,
    ConstraintStatus,
    CompositorBlueprint,
    KineticCompositor,
    Frame,
    create_compositor,
    verify_frame,
)


class TestRectPrimitives:
    """Test Rect primitive operations."""

    def test_rect_properties(self):
        r = Rect(10, 20, 100, 50)
        assert r.left == 10
        assert r.right == 110
        assert r.top == 20
        assert r.bottom == 70
        assert r.center == (60, 45)
        assert r.area == 5000

    def test_rect_intersection(self):
        r1 = Rect(0, 0, 100, 100)
        r2 = Rect(50, 50, 100, 100)
        r3 = Rect(200, 200, 50, 50)

        assert r1.intersects(r2)
        assert r2.intersects(r1)
        assert not r1.intersects(r3)
        assert r1.intersection_area(r2) == 2500  # 50x50

    def test_rect_contains(self):
        outer = Rect(0, 0, 200, 200)
        inner = Rect(50, 50, 50, 50)
        outside = Rect(250, 250, 50, 50)

        assert outer.contains(inner)
        assert not inner.contains(outer)
        assert not outer.contains(outside)

    def test_rect_moved(self):
        r = Rect(10, 20, 100, 50)
        moved = r.moved(5, -10)
        assert moved.x == 15
        assert moved.y == 10
        assert moved.width == 100  # Size unchanged

    def test_rect_at(self):
        r = Rect(10, 20, 100, 50)
        repositioned = r.at(0, 0)
        assert repositioned.x == 0
        assert repositioned.y == 0
        assert repositioned.width == 100


class TestColorPrimitives:
    """Test Color primitive operations."""

    def test_color_creation(self):
        c = Color(255, 128, 0, 0.5)
        assert c.r == 255
        assert c.g == 128
        assert c.b == 0
        assert c.a == 0.5

    def test_color_validation(self):
        with pytest.raises(ValueError):
            Color(256, 0, 0)  # r out of range

        with pytest.raises(ValueError):
            Color(0, 0, 0, 1.5)  # alpha out of range

    def test_color_luminance(self):
        assert BLACK.luminance == pytest.approx(0.0, abs=0.001)
        assert WHITE.luminance == pytest.approx(1.0, abs=0.001)

    def test_color_contrast_ratio(self):
        # Black on white should be 21:1 (maximum)
        ratio = BLACK.contrast_ratio(WHITE)
        assert ratio == pytest.approx(21.0, abs=0.1)

        # Same color should be 1:1
        ratio = WHITE.contrast_ratio(WHITE)
        assert ratio == pytest.approx(1.0, abs=0.001)


class TestNoOverlapConstraint:
    """Test NoOverlap constraint."""

    def test_no_overlap_satisfied(self):
        # Non-overlapping elements
        el_a = VisualElement("a", Rect(0, 0, 50, 50))
        el_b = VisualElement("b", Rect(100, 0, 50, 50))

        constraint = NoOverlap("a", "b")
        result = constraint.evaluate({"a": el_a, "b": el_b}, Rect(0, 0, 1000, 1000))

        assert result.satisfied

    def test_no_overlap_violated(self):
        # Overlapping elements
        el_a = VisualElement("a", Rect(0, 0, 100, 100))
        el_b = VisualElement("b", Rect(50, 50, 100, 100))

        constraint = NoOverlap("a", "b")
        result = constraint.evaluate({"a": el_a, "b": el_b}, Rect(0, 0, 1000, 1000))

        assert result.violated
        assert result.violation_amount == 2500  # 50x50 overlap

    def test_no_overlap_with_tolerance(self):
        # Overlapping but within tolerance
        el_a = VisualElement("a", Rect(0, 0, 100, 100))
        el_b = VisualElement("b", Rect(95, 0, 100, 100))  # 5px overlap in x

        constraint = NoOverlap("a", "b", allowed_overlap=600)  # 5x100 = 500
        result = constraint.evaluate({"a": el_a, "b": el_b}, Rect(0, 0, 1000, 1000))

        assert result.satisfied


class TestMinContrastConstraint:
    """Test MinContrast constraint."""

    def test_min_contrast_satisfied(self):
        # Black text on white background
        fg = VisualElement("text", Rect(0, 0, 100, 20), color=BLACK)
        bg = VisualElement("bg", Rect(0, 0, 200, 200), color=WHITE)

        constraint = MinContrast("text", "bg", min_ratio=4.5)
        result = constraint.evaluate({"text": fg, "bg": bg}, Rect(0, 0, 1000, 1000))

        assert result.satisfied

    def test_min_contrast_violated(self):
        # Light gray on white (poor contrast)
        light_gray = Color(200, 200, 200)
        fg = VisualElement("text", Rect(0, 0, 100, 20), color=light_gray)
        bg = VisualElement("bg", Rect(0, 0, 200, 200), color=WHITE)

        constraint = MinContrast("text", "bg", min_ratio=4.5)
        result = constraint.evaluate({"text": fg, "bg": bg}, Rect(0, 0, 1000, 1000))

        assert result.violated


class TestFullyVisibleConstraint:
    """Test FullyVisible constraint."""

    def test_fully_visible_satisfied(self):
        el = VisualElement("panel", Rect(100, 100, 200, 200))
        viewport = Rect(0, 0, 1000, 1000)

        constraint = FullyVisible("panel")
        result = constraint.evaluate({"panel": el}, viewport)

        assert result.satisfied

    def test_fully_visible_violated(self):
        # Element extends beyond viewport
        el = VisualElement("panel", Rect(900, 100, 200, 200))  # Right edge at 1100
        viewport = Rect(0, 0, 1000, 1000)

        constraint = FullyVisible("panel")
        result = constraint.evaluate({"panel": el}, viewport)

        assert result.violated
        assert result.violation_amount == 100  # 100px outside

    def test_fully_visible_with_margin(self):
        # Element within viewport but not within margin
        el = VisualElement("panel", Rect(5, 5, 50, 50))
        viewport = Rect(0, 0, 1000, 1000)

        constraint = FullyVisible("panel", margin=20)
        result = constraint.evaluate({"panel": el}, viewport)

        assert result.violated  # Only 5px from edge, needs 20


class TestRelativePositionConstraint:
    """Test RelativePosition constraint."""

    def test_relative_left_of(self):
        el_a = VisualElement("sidebar", Rect(0, 0, 100, 500))
        el_b = VisualElement("main", Rect(110, 0, 500, 500))

        constraint = RelativePosition("sidebar", "main", "left_of", gap=10)
        result = constraint.evaluate({"sidebar": el_a, "main": el_b}, Rect(0, 0, 1000, 1000))

        assert result.satisfied

    def test_relative_above(self):
        el_a = VisualElement("header", Rect(0, 0, 500, 50))
        el_b = VisualElement("content", Rect(0, 60, 500, 400))

        constraint = RelativePosition("header", "content", "above", gap=10)
        result = constraint.evaluate({"header": el_a, "content": el_b}, Rect(0, 0, 1000, 1000))

        assert result.satisfied

    def test_relative_violated(self):
        # Sidebar is right of main, not left
        el_a = VisualElement("sidebar", Rect(600, 0, 100, 500))
        el_b = VisualElement("main", Rect(0, 0, 500, 500))

        constraint = RelativePosition("sidebar", "main", "left_of", gap=10)
        result = constraint.evaluate({"sidebar": el_a, "main": el_b}, Rect(0, 0, 1000, 1000))

        assert result.violated


class TestEvenSpacingConstraint:
    """Test EvenSpacing constraint."""

    def test_even_spacing_satisfied(self):
        # Three buttons evenly spaced
        btn1 = VisualElement("btn1", Rect(100, 0, 50, 50))  # center at 125
        btn2 = VisualElement("btn2", Rect(200, 0, 50, 50))  # center at 225
        btn3 = VisualElement("btn3", Rect(300, 0, 50, 50))  # center at 325

        constraint = EvenSpacing(["btn1", "btn2", "btn3"], axis="horizontal", tolerance=1)
        result = constraint.evaluate(
            {"btn1": btn1, "btn2": btn2, "btn3": btn3},
            Rect(0, 0, 1000, 1000)
        )

        assert result.satisfied

    def test_even_spacing_violated(self):
        # Uneven spacing
        btn1 = VisualElement("btn1", Rect(100, 0, 50, 50))  # center at 125
        btn2 = VisualElement("btn2", Rect(180, 0, 50, 50))  # center at 205
        btn3 = VisualElement("btn3", Rect(400, 0, 50, 50))  # center at 425

        constraint = EvenSpacing(["btn1", "btn2", "btn3"], axis="horizontal", tolerance=1)
        result = constraint.evaluate(
            {"btn1": btn1, "btn2": btn2, "btn3": btn3},
            Rect(0, 0, 1000, 1000)
        )

        assert result.violated


class TestCompositorBasics:
    """Test basic compositor operations."""

    def test_create_compositor(self):
        comp = create_compositor(1920, 1080)
        assert comp.viewport.width == 1920
        assert comp.viewport.height == 1080

    def test_add_element(self):
        comp = create_compositor()
        el = VisualElement("panel", Rect(100, 100, 200, 200))
        comp.add_element(el)

        assert comp.get_element("panel") is not None
        assert comp.get_element("panel").bounds.x == 100

    def test_remove_element(self):
        comp = create_compositor()
        comp.add_element(VisualElement("panel", Rect(100, 100, 200, 200)))
        comp.remove_element("panel")

        assert comp.get_element("panel") is None

    def test_render_without_constraints(self):
        comp = create_compositor()
        comp.add_element(VisualElement("panel", Rect(100, 100, 200, 200)))

        frame = comp.render()

        assert isinstance(frame, Frame)
        assert frame.frame_number == 1
        assert frame.proof.all_satisfied
        assert "panel" in frame.elements


class TestCompositorConstraintSolving:
    """Test compositor constraint solving."""

    def test_solver_resolves_overlap(self):
        """Compositor should solve overlapping element positions."""
        comp = create_compositor(1000, 1000)

        # Add overlapping elements
        comp.add_element(VisualElement("a", Rect(100, 100, 100, 100)))
        comp.add_element(VisualElement("b", Rect(150, 150, 100, 100)))

        # Require no overlap
        comp.add_constraint(NoOverlap("a", "b"))

        # Should render successfully (solver finds valid positions)
        frame = comp.render()

        assert frame.proof.all_satisfied

        # Verify no overlap in result
        a = frame.elements["a"]
        b = frame.elements["b"]
        overlap = a.bounds.intersection_area(b.bounds)
        assert overlap == 0

    def test_solver_resolves_visibility(self):
        """Compositor should move off-screen elements into viewport."""
        comp = create_compositor(1000, 1000)

        # Add element partially off-screen
        comp.add_element(VisualElement("panel", Rect(950, 100, 200, 200)))

        # Require fully visible
        comp.add_constraint(FullyVisible("panel"))

        frame = comp.render()

        assert frame.proof.all_satisfied

        # Verify element is now fully visible
        panel = frame.elements["panel"]
        assert panel.bounds.right <= 1000

    def test_unsatisfiable_constraints_finfr(self):
        """Contradictory constraints should trigger finfr."""
        comp = create_compositor(200, 200)  # Small viewport

        # Add two large elements
        comp.add_element(VisualElement("a", Rect(0, 0, 150, 150)))
        comp.add_element(VisualElement("b", Rect(0, 0, 150, 150)))

        # Require both fully visible and no overlap
        # In 200x200 viewport, two 150x150 elements cannot both fit without overlap
        comp.add_constraint(NoOverlap("a", "b"))
        comp.add_constraint(FullyVisible("a"))
        comp.add_constraint(FullyVisible("b"))

        # Should raise finfr - cannot satisfy all constraints
        with pytest.raises(LawViolation):
            comp.render()

    def test_try_render_handles_finfr(self):
        """try_render should return error instead of raising."""
        comp = create_compositor(100, 100)

        comp.add_element(VisualElement("a", Rect(0, 0, 80, 80)))
        comp.add_element(VisualElement("b", Rect(0, 0, 80, 80)))

        comp.add_constraint(NoOverlap("a", "b"))
        comp.add_constraint(FullyVisible("a"))
        comp.add_constraint(FullyVisible("b"))

        frame, error = comp.try_render()

        assert frame is None
        assert error is not None
        assert "constraint" in error.lower()


class TestFrameProof:
    """Test frame proof generation."""

    def test_frame_has_proof(self):
        comp = create_compositor()
        comp.add_element(VisualElement("panel", Rect(100, 100, 200, 200)))
        comp.add_constraint(FullyVisible("panel"))

        frame = comp.render()

        assert frame.proof is not None
        assert frame.proof.frame_hash != ""
        assert frame.proof.verification_hash != ""
        assert frame.proof.all_satisfied
        assert "FullyVisible(panel)" in frame.proof.constraints_checked

    def test_proof_certificate_export(self):
        comp = create_compositor()
        comp.add_element(VisualElement("panel", Rect(100, 100, 200, 200)))

        frame = comp.render()
        cert = frame.proof.export_certificate()

        assert cert["certificate"]["type"] == "constraint_proof"
        assert cert["certificate"]["all_satisfied"] == True
        assert "frame_hash" in cert["certificate"]

    def test_frame_to_dict(self):
        comp = create_compositor()
        comp.add_element(VisualElement("panel", Rect(100, 100, 200, 200)))

        frame = comp.render()
        data = frame.to_dict()

        assert data["frame_number"] == 1
        assert "elements" in data
        assert "proof" in data
        assert "viewport" in data


class TestVerifyFrame:
    """Test external frame verification."""

    def test_verify_valid_frame(self):
        comp = create_compositor()
        comp.add_element(VisualElement("a", Rect(0, 0, 100, 100)))
        comp.add_element(VisualElement("b", Rect(200, 0, 100, 100)))

        constraints = [NoOverlap("a", "b")]
        for c in constraints:
            comp.add_constraint(c)

        frame = comp.render()

        # External verification
        assert verify_frame(frame, constraints)

    def test_verify_detects_tampering(self):
        """If frame is modified, verification should fail."""
        comp = create_compositor()
        comp.add_element(VisualElement("a", Rect(0, 0, 100, 100)))
        comp.add_element(VisualElement("b", Rect(200, 0, 100, 100)))

        constraints = [NoOverlap("a", "b")]
        for c in constraints:
            comp.add_constraint(c)

        frame = comp.render()

        # "Tamper" with the frame by moving elements to overlap
        frame.elements["b"] = frame.elements["b"].at(50, 0)

        # Verification should now fail
        assert not verify_frame(frame, constraints)


class TestKineticCompositor:
    """Test animated compositor."""

    def test_animate_to(self):
        comp = create_compositor(1000, 1000)
        comp.add_element(VisualElement("panel", Rect(0, 0, 100, 100)))
        comp.add_constraint(FullyVisible("panel"))

        kinetic = KineticCompositor(comp)
        frames = kinetic.animate_to(
            target_positions={"panel": (500, 500)},
            steps=5
        )

        assert len(frames) == 5

        # First frame should be at/near start
        first_panel = frames[0].elements["panel"]
        assert first_panel.bounds.x == pytest.approx(0, abs=1)

        # Last frame should be at target
        last_panel = frames[-1].elements["panel"]
        assert last_panel.bounds.x == pytest.approx(500, abs=1)
        assert last_panel.bounds.y == pytest.approx(500, abs=1)

        # All frames should have valid proofs
        for frame in frames:
            assert frame.proof.all_satisfied

    def test_animation_respects_constraints(self):
        """Animation should maintain constraint satisfaction throughout."""
        comp = create_compositor(1000, 1000)
        comp.add_element(VisualElement("a", Rect(0, 0, 100, 100)))
        comp.add_element(VisualElement("b", Rect(200, 0, 100, 100)))

        comp.add_constraint(NoOverlap("a", "b"))
        comp.add_constraint(FullyVisible("a"))
        comp.add_constraint(FullyVisible("b"))

        kinetic = KineticCompositor(comp)

        # Try to animate A toward B (would cause overlap if not constrained)
        # The compositor should adjust to maintain constraints
        frames = kinetic.animate_to(
            target_positions={"a": (150, 0)},  # Would overlap with B
            steps=5
        )

        # All frames should still satisfy constraints
        for frame in frames:
            a = frame.elements["a"]
            b = frame.elements["b"]
            overlap = a.bounds.intersection_area(b.bounds)
            assert overlap == 0, f"Frame {frame.frame_number} has overlap"


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_dashboard_layout(self):
        """Simulate a dashboard with header, sidebar, main content."""
        comp = create_compositor(1920, 1080)

        # Add elements
        comp.add_element(VisualElement("header", Rect(0, 0, 1920, 60), color=Color(50, 50, 50)))
        comp.add_element(VisualElement("sidebar", Rect(0, 60, 250, 1020)))
        comp.add_element(VisualElement("main", Rect(250, 60, 1670, 1020)))

        # Add constraints
        comp.add_constraint(FullyVisible("header"))
        comp.add_constraint(FullyVisible("sidebar"))
        comp.add_constraint(FullyVisible("main"))
        comp.add_constraint(NoOverlapGroup(["header", "sidebar", "main"]))
        comp.add_constraint(RelativePosition("sidebar", "main", "left_of"))
        comp.add_constraint(RelativePosition("header", "sidebar", "above"))
        comp.add_constraint(RelativePosition("header", "main", "above"))

        frame = comp.render()

        assert frame.proof.all_satisfied
        assert len(frame.proof.constraints_checked) >= 6

    def test_accessible_button(self):
        """Ensure button meets accessibility requirements."""
        comp = create_compositor(1000, 1000)

        # Button with text
        button_color = Color(0, 100, 200)
        text_color = WHITE

        comp.add_element(VisualElement("button", Rect(100, 100, 120, 48), color=button_color))
        comp.add_element(VisualElement("button_text", Rect(110, 114, 100, 20), color=text_color))

        # Accessibility constraints
        comp.add_constraint(MinSize("button", min_width=44, min_height=44))  # Touch target
        comp.add_constraint(MinContrast("button_text", "button", min_ratio=4.5))  # WCAG AA
        comp.add_constraint(FullyVisible("button"))

        frame = comp.render()

        assert frame.proof.all_satisfied

    def test_responsive_cards(self):
        """Test evenly spaced card layout."""
        comp = create_compositor(1200, 800)

        # Three cards
        for i, name in enumerate(["card1", "card2", "card3"]):
            comp.add_element(VisualElement(name, Rect(100 + i * 350, 100, 300, 400)))

        # Constraints
        comp.add_constraint(NoOverlapGroup(["card1", "card2", "card3"]))
        comp.add_constraint(EvenSpacing(["card1", "card2", "card3"], axis="horizontal", tolerance=5))
        for card in ["card1", "card2", "card3"]:
            comp.add_constraint(FullyVisible(card))

        frame = comp.render()

        assert frame.proof.all_satisfied


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
