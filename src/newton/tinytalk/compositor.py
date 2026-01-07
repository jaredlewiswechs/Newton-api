"""
═══════════════════════════════════════════════════════════════════════════════
 Newton Constraint Compositor
═══════════════════════════════════════════════════════════════════════════════

A compositor that SOLVES instead of stacks.

Traditional compositor: "Put window A at (100, 200), window B at (150, 250)"
Newton compositor: "A and B must not overlap. B must be right of A. Solve."

Every visual element has constraints. The compositor finds pixel positions
that satisfy ALL constraints. If no solution exists—if constraints contradict—
nothing renders. Finfr. Invalid visual state is unrepresentable.

The frame itself becomes a tandem pair:
    (pixels, proof_that_all_visual_constraints_hold)

You can't draw invalid states. The GPU becomes a proof-carrying renderer.
"""

from dataclasses import dataclass, field as dataclass_field
from typing import Any, Dict, List, Optional, Set, Tuple, Callable, Union
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
import time
import math

from .core import (
    Blueprint, Field, field, Law, LawResult, LawViolation,
    when, finfr, ratio, law, forge
)
from .engine import Presence, Delta, KineticEngine


# ═══════════════════════════════════════════════════════════════════════════════
# VISUAL PRIMITIVES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Rect:
    """Immutable rectangle for bounds calculations."""
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)

    @property
    def area(self) -> float:
        return self.width * self.height

    def intersects(self, other: 'Rect') -> bool:
        """Check if this rect overlaps with another."""
        return not (
            self.right <= other.left or
            self.left >= other.right or
            self.bottom <= other.top or
            self.top >= other.bottom
        )

    def intersection_area(self, other: 'Rect') -> float:
        """Calculate overlapping area."""
        if not self.intersects(other):
            return 0.0

        x_overlap = max(0, min(self.right, other.right) - max(self.left, other.left))
        y_overlap = max(0, min(self.bottom, other.bottom) - max(self.top, other.top))
        return x_overlap * y_overlap

    def contains(self, other: 'Rect') -> bool:
        """Check if this rect fully contains another."""
        return (
            self.left <= other.left and
            self.right >= other.right and
            self.top <= other.top and
            self.bottom >= other.bottom
        )

    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside rect."""
        return self.left <= x <= self.right and self.top <= y <= self.bottom

    def moved(self, dx: float, dy: float) -> 'Rect':
        """Return new rect moved by delta."""
        return Rect(self.x + dx, self.y + dy, self.width, self.height)

    def at(self, x: float, y: float) -> 'Rect':
        """Return new rect at position."""
        return Rect(x, y, self.width, self.height)


@dataclass(frozen=True)
class Color:
    """RGBA color with contrast calculations."""
    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255
    a: float = 1.0  # 0.0-1.0

    def __post_init__(self):
        # Validate ranges (frozen=True requires object.__setattr__)
        if not (0 <= self.r <= 255 and 0 <= self.g <= 255 and 0 <= self.b <= 255):
            raise ValueError("RGB values must be 0-255")
        if not (0.0 <= self.a <= 1.0):
            raise ValueError("Alpha must be 0.0-1.0")

    @property
    def luminance(self) -> float:
        """Calculate relative luminance per WCAG 2.1."""
        def channel_luminance(c: int) -> float:
            c_norm = c / 255.0
            if c_norm <= 0.03928:
                return c_norm / 12.92
            return ((c_norm + 0.055) / 1.055) ** 2.4

        return (
            0.2126 * channel_luminance(self.r) +
            0.7152 * channel_luminance(self.g) +
            0.0722 * channel_luminance(self.b)
        )

    def contrast_ratio(self, other: 'Color') -> float:
        """Calculate WCAG contrast ratio against another color."""
        l1 = self.luminance
        l2 = other.luminance
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    def to_tuple(self) -> Tuple[int, int, int, float]:
        return (self.r, self.g, self.b, self.a)


# Predefined colors
BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
TRANSPARENT = Color(0, 0, 0, 0.0)


# ═══════════════════════════════════════════════════════════════════════════════
# VISUAL CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

class ConstraintPriority(Enum):
    """Priority levels for constraint solving."""
    REQUIRED = 1000      # Must be satisfied or finfr
    STRONG = 750         # Should be satisfied
    MEDIUM = 500         # Prefer to satisfy
    WEAK = 250           # Nice to have


class ConstraintStatus(Enum):
    """Result of constraint evaluation."""
    SATISFIED = "satisfied"
    VIOLATED = "violated"
    UNKNOWN = "unknown"  # Cannot evaluate (missing data)


@dataclass
class ConstraintResult:
    """Result of evaluating a constraint."""
    status: ConstraintStatus
    constraint_name: str
    message: str = ""
    violation_amount: float = 0.0  # How much it's violated by
    affected_elements: List[str] = dataclass_field(default_factory=list)

    @property
    def satisfied(self) -> bool:
        return self.status == ConstraintStatus.SATISFIED

    @property
    def violated(self) -> bool:
        return self.status == ConstraintStatus.VIOLATED


class VisualConstraint(ABC):
    """Base class for all visual constraints."""

    def __init__(
        self,
        name: str = "",
        priority: ConstraintPriority = ConstraintPriority.REQUIRED
    ):
        self.name = name or self.__class__.__name__
        self.priority = priority

    @abstractmethod
    def evaluate(self, elements: Dict[str, 'VisualElement'], viewport: Rect) -> ConstraintResult:
        """Evaluate this constraint against current element positions."""
        pass

    @abstractmethod
    def get_affected_elements(self) -> Set[str]:
        """Return IDs of elements this constraint affects."""
        pass

    def is_required(self) -> bool:
        return self.priority == ConstraintPriority.REQUIRED


class NoOverlap(VisualConstraint):
    """
    Constraint: Two elements must not overlap.

    Usage:
        NoOverlap("panel_a", "panel_b")
        NoOverlap("panel_a", "panel_b", allowed_overlap=10)  # Allow 10px overlap
    """

    def __init__(
        self,
        element_a: str,
        element_b: str,
        allowed_overlap: float = 0.0,
        name: str = "",
        priority: ConstraintPriority = ConstraintPriority.REQUIRED
    ):
        super().__init__(name or f"NoOverlap({element_a}, {element_b})", priority)
        self.element_a = element_a
        self.element_b = element_b
        self.allowed_overlap = allowed_overlap

    def evaluate(self, elements: Dict[str, 'VisualElement'], viewport: Rect) -> ConstraintResult:
        a = elements.get(self.element_a)
        b = elements.get(self.element_b)

        if not a or not b:
            return ConstraintResult(
                status=ConstraintStatus.UNKNOWN,
                constraint_name=self.name,
                message=f"Element not found",
                affected_elements=[self.element_a, self.element_b]
            )

        overlap = a.bounds.intersection_area(b.bounds)

        if overlap <= self.allowed_overlap:
            return ConstraintResult(
                status=ConstraintStatus.SATISFIED,
                constraint_name=self.name,
                affected_elements=[self.element_a, self.element_b]
            )

        return ConstraintResult(
            status=ConstraintStatus.VIOLATED,
            constraint_name=self.name,
            message=f"Elements overlap by {overlap - self.allowed_overlap:.1f}px",
            violation_amount=overlap - self.allowed_overlap,
            affected_elements=[self.element_a, self.element_b]
        )

    def get_affected_elements(self) -> Set[str]:
        return {self.element_a, self.element_b}


class NoOverlapGroup(VisualConstraint):
    """
    Constraint: No elements in a group may overlap each other.

    Usage:
        NoOverlapGroup(["panel_a", "panel_b", "panel_c"])
    """

    def __init__(
        self,
        elements: List[str],
        allowed_overlap: float = 0.0,
        name: str = "",
        priority: ConstraintPriority = ConstraintPriority.REQUIRED
    ):
        super().__init__(name or f"NoOverlapGroup({len(elements)} elements)", priority)
        self.elements = elements
        self.allowed_overlap = allowed_overlap

    def evaluate(self, elements: Dict[str, 'VisualElement'], viewport: Rect) -> ConstraintResult:
        violations = []
        max_violation = 0.0

        for i, id_a in enumerate(self.elements):
            for id_b in self.elements[i+1:]:
                a = elements.get(id_a)
                b = elements.get(id_b)

                if not a or not b:
                    continue

                overlap = a.bounds.intersection_area(b.bounds)
                if overlap > self.allowed_overlap:
                    violations.append((id_a, id_b, overlap))
                    max_violation = max(max_violation, overlap - self.allowed_overlap)

        if not violations:
            return ConstraintResult(
                status=ConstraintStatus.SATISFIED,
                constraint_name=self.name,
                affected_elements=self.elements
            )

        return ConstraintResult(
            status=ConstraintStatus.VIOLATED,
            constraint_name=self.name,
            message=f"{len(violations)} overlapping pairs",
            violation_amount=max_violation,
            affected_elements=self.elements
        )

    def get_affected_elements(self) -> Set[str]:
        return set(self.elements)


class MinContrast(VisualConstraint):
    """
    Constraint: Text must have minimum contrast ratio against background.

    WCAG AA: 4.5:1 for normal text, 3:1 for large text
    WCAG AAA: 7:1 for normal text, 4.5:1 for large text

    Usage:
        MinContrast("label", "background", ratio=4.5)
    """

    def __init__(
        self,
        foreground_element: str,
        background_element: str,
        min_ratio: float = 4.5,
        name: str = "",
        priority: ConstraintPriority = ConstraintPriority.REQUIRED
    ):
        super().__init__(name or f"MinContrast({foreground_element}, {min_ratio}:1)", priority)
        self.foreground_element = foreground_element
        self.background_element = background_element
        self.min_ratio = min_ratio

    def evaluate(self, elements: Dict[str, 'VisualElement'], viewport: Rect) -> ConstraintResult:
        fg = elements.get(self.foreground_element)
        bg = elements.get(self.background_element)

        if not fg or not bg:
            return ConstraintResult(
                status=ConstraintStatus.UNKNOWN,
                constraint_name=self.name,
                message="Element not found",
                affected_elements=[self.foreground_element, self.background_element]
            )

        actual_ratio = fg.color.contrast_ratio(bg.color)

        if actual_ratio >= self.min_ratio:
            return ConstraintResult(
                status=ConstraintStatus.SATISFIED,
                constraint_name=self.name,
                message=f"Contrast {actual_ratio:.2f}:1 >= {self.min_ratio}:1",
                affected_elements=[self.foreground_element, self.background_element]
            )

        return ConstraintResult(
            status=ConstraintStatus.VIOLATED,
            constraint_name=self.name,
            message=f"Contrast {actual_ratio:.2f}:1 < required {self.min_ratio}:1",
            violation_amount=self.min_ratio - actual_ratio,
            affected_elements=[self.foreground_element, self.background_element]
        )

    def get_affected_elements(self) -> Set[str]:
        return {self.foreground_element, self.background_element}


class FullyVisible(VisualConstraint):
    """
    Constraint: Element must be fully visible within viewport.

    Usage:
        FullyVisible("important_panel")
        FullyVisible("dialog", margin=20)  # Must have 20px margin from edges
    """

    def __init__(
        self,
        element: str,
        margin: float = 0.0,
        name: str = "",
        priority: ConstraintPriority = ConstraintPriority.REQUIRED
    ):
        super().__init__(name or f"FullyVisible({element})", priority)
        self.element = element
        self.margin = margin

    def evaluate(self, elements: Dict[str, 'VisualElement'], viewport: Rect) -> ConstraintResult:
        el = elements.get(self.element)

        if not el:
            return ConstraintResult(
                status=ConstraintStatus.UNKNOWN,
                constraint_name=self.name,
                message="Element not found",
                affected_elements=[self.element]
            )

        # Create effective viewport with margin
        effective_viewport = Rect(
            viewport.x + self.margin,
            viewport.y + self.margin,
            viewport.width - 2 * self.margin,
            viewport.height - 2 * self.margin
        )

        if effective_viewport.contains(el.bounds):
            return ConstraintResult(
                status=ConstraintStatus.SATISFIED,
                constraint_name=self.name,
                affected_elements=[self.element]
            )

        # Calculate how much is outside
        outside = 0.0
        if el.bounds.left < effective_viewport.left:
            outside = max(outside, effective_viewport.left - el.bounds.left)
        if el.bounds.right > effective_viewport.right:
            outside = max(outside, el.bounds.right - effective_viewport.right)
        if el.bounds.top < effective_viewport.top:
            outside = max(outside, effective_viewport.top - el.bounds.top)
        if el.bounds.bottom > effective_viewport.bottom:
            outside = max(outside, el.bounds.bottom - effective_viewport.bottom)

        return ConstraintResult(
            status=ConstraintStatus.VIOLATED,
            constraint_name=self.name,
            message=f"Element extends {outside:.1f}px outside viewport",
            violation_amount=outside,
            affected_elements=[self.element]
        )

    def get_affected_elements(self) -> Set[str]:
        return {self.element}


class RelativePosition(VisualConstraint):
    """
    Constraint: Element A must be positioned relative to element B.

    Usage:
        RelativePosition("tooltip", "button", relation="above")
        RelativePosition("sidebar", "main", relation="left_of", gap=10)
    """

    RELATIONS = {"above", "below", "left_of", "right_of"}

    def __init__(
        self,
        element_a: str,
        element_b: str,
        relation: str,  # "above", "below", "left_of", "right_of"
        gap: float = 0.0,
        name: str = "",
        priority: ConstraintPriority = ConstraintPriority.REQUIRED
    ):
        if relation not in self.RELATIONS:
            raise ValueError(f"Invalid relation: {relation}. Must be one of {self.RELATIONS}")

        super().__init__(name or f"RelativePosition({element_a} {relation} {element_b})", priority)
        self.element_a = element_a
        self.element_b = element_b
        self.relation = relation
        self.gap = gap

    def evaluate(self, elements: Dict[str, 'VisualElement'], viewport: Rect) -> ConstraintResult:
        a = elements.get(self.element_a)
        b = elements.get(self.element_b)

        if not a or not b:
            return ConstraintResult(
                status=ConstraintStatus.UNKNOWN,
                constraint_name=self.name,
                message="Element not found",
                affected_elements=[self.element_a, self.element_b]
            )

        satisfied = False
        actual_gap = 0.0

        if self.relation == "above":
            actual_gap = b.bounds.top - a.bounds.bottom
            satisfied = actual_gap >= self.gap
        elif self.relation == "below":
            actual_gap = a.bounds.top - b.bounds.bottom
            satisfied = actual_gap >= self.gap
        elif self.relation == "left_of":
            actual_gap = b.bounds.left - a.bounds.right
            satisfied = actual_gap >= self.gap
        elif self.relation == "right_of":
            actual_gap = a.bounds.left - b.bounds.right
            satisfied = actual_gap >= self.gap

        if satisfied:
            return ConstraintResult(
                status=ConstraintStatus.SATISFIED,
                constraint_name=self.name,
                affected_elements=[self.element_a, self.element_b]
            )

        return ConstraintResult(
            status=ConstraintStatus.VIOLATED,
            constraint_name=self.name,
            message=f"Gap is {actual_gap:.1f}px, required {self.gap:.1f}px",
            violation_amount=self.gap - actual_gap,
            affected_elements=[self.element_a, self.element_b]
        )

    def get_affected_elements(self) -> Set[str]:
        return {self.element_a, self.element_b}


class EvenSpacing(VisualConstraint):
    """
    Constraint: Elements must be evenly spaced.

    Usage:
        EvenSpacing(["btn1", "btn2", "btn3"], axis="horizontal")
        EvenSpacing(["item1", "item2", "item3"], axis="vertical", tolerance=2)
    """

    def __init__(
        self,
        elements: List[str],
        axis: str = "horizontal",  # "horizontal" or "vertical"
        tolerance: float = 1.0,
        name: str = "",
        priority: ConstraintPriority = ConstraintPriority.REQUIRED
    ):
        super().__init__(name or f"EvenSpacing({len(elements)} elements, {axis})", priority)
        self.elements = elements
        self.axis = axis
        self.tolerance = tolerance

    def evaluate(self, elements: Dict[str, 'VisualElement'], viewport: Rect) -> ConstraintResult:
        if len(self.elements) < 2:
            return ConstraintResult(
                status=ConstraintStatus.SATISFIED,
                constraint_name=self.name,
                affected_elements=self.elements
            )

        # Get positions along axis
        positions = []
        for el_id in self.elements:
            el = elements.get(el_id)
            if not el:
                return ConstraintResult(
                    status=ConstraintStatus.UNKNOWN,
                    constraint_name=self.name,
                    message=f"Element {el_id} not found",
                    affected_elements=self.elements
                )

            if self.axis == "horizontal":
                positions.append((el_id, el.bounds.center[0]))
            else:
                positions.append((el_id, el.bounds.center[1]))

        # Sort by position
        positions.sort(key=lambda x: x[1])

        # Calculate gaps
        gaps = []
        for i in range(1, len(positions)):
            gaps.append(positions[i][1] - positions[i-1][1])

        if not gaps:
            return ConstraintResult(
                status=ConstraintStatus.SATISFIED,
                constraint_name=self.name,
                affected_elements=self.elements
            )

        # Check if gaps are equal within tolerance
        avg_gap = sum(gaps) / len(gaps)
        max_deviation = max(abs(g - avg_gap) for g in gaps)

        if max_deviation <= self.tolerance:
            return ConstraintResult(
                status=ConstraintStatus.SATISFIED,
                constraint_name=self.name,
                message=f"Max deviation {max_deviation:.1f}px within tolerance",
                affected_elements=self.elements
            )

        return ConstraintResult(
            status=ConstraintStatus.VIOLATED,
            constraint_name=self.name,
            message=f"Max spacing deviation {max_deviation:.1f}px exceeds tolerance {self.tolerance:.1f}px",
            violation_amount=max_deviation - self.tolerance,
            affected_elements=self.elements
        )

    def get_affected_elements(self) -> Set[str]:
        return set(self.elements)


class MinSize(VisualConstraint):
    """
    Constraint: Element must meet minimum size requirements.

    Usage:
        MinSize("button", min_width=44, min_height=44)  # Touch target
    """

    def __init__(
        self,
        element: str,
        min_width: float = 0.0,
        min_height: float = 0.0,
        name: str = "",
        priority: ConstraintPriority = ConstraintPriority.REQUIRED
    ):
        super().__init__(name or f"MinSize({element})", priority)
        self.element = element
        self.min_width = min_width
        self.min_height = min_height

    def evaluate(self, elements: Dict[str, 'VisualElement'], viewport: Rect) -> ConstraintResult:
        el = elements.get(self.element)

        if not el:
            return ConstraintResult(
                status=ConstraintStatus.UNKNOWN,
                constraint_name=self.name,
                message="Element not found",
                affected_elements=[self.element]
            )

        width_ok = el.bounds.width >= self.min_width
        height_ok = el.bounds.height >= self.min_height

        if width_ok and height_ok:
            return ConstraintResult(
                status=ConstraintStatus.SATISFIED,
                constraint_name=self.name,
                affected_elements=[self.element]
            )

        violations = []
        max_violation = 0.0
        if not width_ok:
            violations.append(f"width {el.bounds.width:.1f} < {self.min_width}")
            max_violation = max(max_violation, self.min_width - el.bounds.width)
        if not height_ok:
            violations.append(f"height {el.bounds.height:.1f} < {self.min_height}")
            max_violation = max(max_violation, self.min_height - el.bounds.height)

        return ConstraintResult(
            status=ConstraintStatus.VIOLATED,
            constraint_name=self.name,
            message="; ".join(violations),
            violation_amount=max_violation,
            affected_elements=[self.element]
        )

    def get_affected_elements(self) -> Set[str]:
        return {self.element}


class AspectRatio(VisualConstraint):
    """
    Constraint: Element must maintain aspect ratio.

    Usage:
        AspectRatio("video", ratio=16/9, tolerance=0.01)
    """

    def __init__(
        self,
        element: str,
        aspect_ratio: float,
        tolerance: float = 0.01,
        name: str = "",
        priority: ConstraintPriority = ConstraintPriority.REQUIRED
    ):
        super().__init__(name or f"AspectRatio({element}, {aspect_ratio:.2f})", priority)
        self.element = element
        self.aspect_ratio = aspect_ratio
        self.tolerance = tolerance

    def evaluate(self, elements: Dict[str, 'VisualElement'], viewport: Rect) -> ConstraintResult:
        el = elements.get(self.element)

        if not el:
            return ConstraintResult(
                status=ConstraintStatus.UNKNOWN,
                constraint_name=self.name,
                message="Element not found",
                affected_elements=[self.element]
            )

        if el.bounds.height == 0:
            return ConstraintResult(
                status=ConstraintStatus.VIOLATED,
                constraint_name=self.name,
                message="Element has zero height",
                violation_amount=float('inf'),
                affected_elements=[self.element]
            )

        actual_ratio = el.bounds.width / el.bounds.height
        deviation = abs(actual_ratio - self.aspect_ratio)

        if deviation <= self.tolerance:
            return ConstraintResult(
                status=ConstraintStatus.SATISFIED,
                constraint_name=self.name,
                affected_elements=[self.element]
            )

        return ConstraintResult(
            status=ConstraintStatus.VIOLATED,
            constraint_name=self.name,
            message=f"Aspect ratio {actual_ratio:.3f} deviates from {self.aspect_ratio:.3f}",
            violation_amount=deviation - self.tolerance,
            affected_elements=[self.element]
        )

    def get_affected_elements(self) -> Set[str]:
        return {self.element}


# ═══════════════════════════════════════════════════════════════════════════════
# VISUAL ELEMENTS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VisualElement:
    """
    A visual element with position and constraints.

    Elements don't have fixed positions—they have constraints.
    The compositor solves for positions that satisfy all constraints.
    """
    id: str
    bounds: Rect
    color: Color = dataclass_field(default_factory=lambda: WHITE)
    z_index: int = 0
    visible: bool = True
    content: Any = None  # Text, image data, etc.
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "bounds": {
                "x": self.bounds.x,
                "y": self.bounds.y,
                "width": self.bounds.width,
                "height": self.bounds.height
            },
            "color": self.color.to_tuple(),
            "z_index": self.z_index,
            "visible": self.visible,
            "metadata": self.metadata
        }

    def moved(self, dx: float, dy: float) -> 'VisualElement':
        """Return copy of element moved by delta."""
        return VisualElement(
            id=self.id,
            bounds=self.bounds.moved(dx, dy),
            color=self.color,
            z_index=self.z_index,
            visible=self.visible,
            content=self.content,
            metadata=self.metadata.copy()
        )

    def at(self, x: float, y: float) -> 'VisualElement':
        """Return copy of element at position."""
        return VisualElement(
            id=self.id,
            bounds=self.bounds.at(x, y),
            color=self.color,
            z_index=self.z_index,
            visible=self.visible,
            content=self.content,
            metadata=self.metadata.copy()
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT SOLVER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SolverResult:
    """Result of constraint solving."""
    success: bool
    elements: Dict[str, VisualElement]
    satisfied_constraints: List[str]
    violated_constraints: List[ConstraintResult]
    iterations: int
    message: str = ""


class ConstraintSolver:
    """
    Solves for element positions that satisfy all constraints.

    Uses iterative refinement with priority-based resolution.
    If no solution exists (constraints contradict), returns failure.
    """

    def __init__(self, max_iterations: int = 1000, tolerance: float = 0.1):
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def solve(
        self,
        elements: Dict[str, VisualElement],
        constraints: List[VisualConstraint],
        viewport: Rect
    ) -> SolverResult:
        """
        Solve for element positions that satisfy all constraints.

        Returns SolverResult with success=False if constraints are unsatisfiable.
        """
        # Work with copies
        working_elements = {
            k: VisualElement(
                id=v.id,
                bounds=Rect(v.bounds.x, v.bounds.y, v.bounds.width, v.bounds.height),
                color=v.color,
                z_index=v.z_index,
                visible=v.visible,
                content=v.content,
                metadata=v.metadata.copy()
            )
            for k, v in elements.items()
        }

        # Sort constraints by priority (required first)
        sorted_constraints = sorted(
            constraints,
            key=lambda c: c.priority.value,
            reverse=True
        )

        iterations = 0
        last_violations = None

        while iterations < self.max_iterations:
            iterations += 1

            # Evaluate all constraints
            results = []
            for constraint in sorted_constraints:
                result = constraint.evaluate(working_elements, viewport)
                results.append((constraint, result))

            # Check if all required constraints are satisfied
            violations = [
                (c, r) for c, r in results
                if r.violated and c.is_required()
            ]

            if not violations:
                # Success!
                satisfied = [c.name for c, r in results if r.satisfied]
                non_required_violations = [
                    r for c, r in results if r.violated and not c.is_required()
                ]

                return SolverResult(
                    success=True,
                    elements=working_elements,
                    satisfied_constraints=satisfied,
                    violated_constraints=non_required_violations,
                    iterations=iterations,
                    message="All required constraints satisfied"
                )

            # Check for convergence (no progress)
            current_violation_score = sum(r.violation_amount for _, r in violations)
            if last_violations is not None:
                if abs(current_violation_score - last_violations) < self.tolerance:
                    # Not making progress
                    return SolverResult(
                        success=False,
                        elements=working_elements,
                        satisfied_constraints=[c.name for c, r in results if r.satisfied],
                        violated_constraints=[r for _, r in violations],
                        iterations=iterations,
                        message=f"Cannot satisfy constraints: {[r.constraint_name for _, r in violations]}"
                    )
            last_violations = current_violation_score

            # Try to resolve violations
            for constraint, result in violations:
                self._attempt_resolution(
                    working_elements,
                    constraint,
                    result,
                    viewport
                )

        # Max iterations reached
        final_results = [(c, c.evaluate(working_elements, viewport)) for c in sorted_constraints]
        final_violations = [r for _, r in final_results if r.violated]

        return SolverResult(
            success=False,
            elements=working_elements,
            satisfied_constraints=[c.name for c, r in final_results if r.satisfied],
            violated_constraints=final_violations,
            iterations=iterations,
            message=f"Max iterations reached. Remaining violations: {len(final_violations)}"
        )

    def _attempt_resolution(
        self,
        elements: Dict[str, VisualElement],
        constraint: VisualConstraint,
        result: ConstraintResult,
        viewport: Rect
    ) -> bool:
        """Attempt to resolve a single constraint violation."""

        # Different resolution strategies based on constraint type
        if isinstance(constraint, NoOverlap):
            return self._resolve_overlap(elements, constraint, result)
        elif isinstance(constraint, FullyVisible):
            return self._resolve_visibility(elements, constraint, result, viewport)
        elif isinstance(constraint, RelativePosition):
            return self._resolve_relative_position(elements, constraint, result)
        elif isinstance(constraint, NoOverlapGroup):
            return self._resolve_group_overlap(elements, constraint, result)

        # Default: no resolution strategy
        return False

    def _resolve_overlap(
        self,
        elements: Dict[str, VisualElement],
        constraint: NoOverlap,
        result: ConstraintResult
    ) -> bool:
        """Push elements apart to resolve overlap."""
        a = elements.get(constraint.element_a)
        b = elements.get(constraint.element_b)

        if not a or not b:
            return False

        # Calculate push direction (from center to center)
        ax, ay = a.bounds.center
        bx, by = b.bounds.center

        dx = bx - ax
        dy = by - ay
        dist = math.sqrt(dx*dx + dy*dy)

        if dist < 0.001:
            # Elements at same position, push in arbitrary direction
            dx, dy, dist = 1, 0, 1

        # Normalize and scale by violation amount
        push = (result.violation_amount / 2 + 1) / dist
        push_x = dx * push
        push_y = dy * push

        # Push elements apart (b moves in direction, a moves opposite)
        elements[constraint.element_b] = b.moved(push_x, push_y)
        elements[constraint.element_a] = a.moved(-push_x, -push_y)

        return True

    def _resolve_group_overlap(
        self,
        elements: Dict[str, VisualElement],
        constraint: NoOverlapGroup,
        result: ConstraintResult
    ) -> bool:
        """Resolve overlaps within a group."""
        # Simple approach: spread elements out from center
        group_elements = [elements.get(eid) for eid in constraint.elements if elements.get(eid)]

        if len(group_elements) < 2:
            return False

        # Calculate center
        center_x = sum(e.bounds.center[0] for e in group_elements) / len(group_elements)
        center_y = sum(e.bounds.center[1] for e in group_elements) / len(group_elements)

        # Push each element away from center
        for el in group_elements:
            ex, ey = el.bounds.center
            dx = ex - center_x
            dy = ey - center_y
            dist = math.sqrt(dx*dx + dy*dy)

            if dist < 0.001:
                # At center, push in arbitrary direction based on index
                angle = 2 * math.pi * constraint.elements.index(el.id) / len(constraint.elements)
                dx, dy = math.cos(angle), math.sin(angle)
                dist = 1

            push = 5 / dist  # Push 5 pixels outward
            elements[el.id] = el.moved(dx * push, dy * push)

        return True

    def _resolve_visibility(
        self,
        elements: Dict[str, VisualElement],
        constraint: FullyVisible,
        result: ConstraintResult,
        viewport: Rect
    ) -> bool:
        """Move element into viewport."""
        el = elements.get(constraint.element)

        if not el:
            return False

        margin = constraint.margin
        effective_viewport = Rect(
            viewport.x + margin,
            viewport.y + margin,
            viewport.width - 2 * margin,
            viewport.height - 2 * margin
        )

        # Calculate needed movement
        dx = 0.0
        dy = 0.0

        if el.bounds.left < effective_viewport.left:
            dx = effective_viewport.left - el.bounds.left
        elif el.bounds.right > effective_viewport.right:
            dx = effective_viewport.right - el.bounds.right

        if el.bounds.top < effective_viewport.top:
            dy = effective_viewport.top - el.bounds.top
        elif el.bounds.bottom > effective_viewport.bottom:
            dy = effective_viewport.bottom - el.bounds.bottom

        elements[constraint.element] = el.moved(dx, dy)
        return True

    def _resolve_relative_position(
        self,
        elements: Dict[str, VisualElement],
        constraint: RelativePosition,
        result: ConstraintResult
    ) -> bool:
        """Adjust positions to satisfy relative constraint."""
        a = elements.get(constraint.element_a)
        b = elements.get(constraint.element_b)

        if not a or not b:
            return False

        gap = constraint.gap

        if constraint.relation == "above":
            # A should be above B with gap
            target_y = b.bounds.top - a.bounds.height - gap
            elements[constraint.element_a] = a.at(a.bounds.x, target_y)
        elif constraint.relation == "below":
            # A should be below B with gap
            target_y = b.bounds.bottom + gap
            elements[constraint.element_a] = a.at(a.bounds.x, target_y)
        elif constraint.relation == "left_of":
            # A should be left of B with gap
            target_x = b.bounds.left - a.bounds.width - gap
            elements[constraint.element_a] = a.at(target_x, a.bounds.y)
        elif constraint.relation == "right_of":
            # A should be right of B with gap
            target_x = b.bounds.right + gap
            elements[constraint.element_a] = a.at(target_x, a.bounds.y)

        return True


# ═══════════════════════════════════════════════════════════════════════════════
# FRAME & PROOF
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ConstraintProof:
    """Proof that all constraints were satisfied for a frame."""
    frame_hash: str
    timestamp: int
    constraints_checked: List[str]
    all_satisfied: bool
    solver_iterations: int
    verification_hash: str  # Hash of (frame_hash + constraints_checked + results)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_hash": self.frame_hash,
            "timestamp": self.timestamp,
            "constraints_checked": self.constraints_checked,
            "all_satisfied": self.all_satisfied,
            "solver_iterations": self.solver_iterations,
            "verification_hash": self.verification_hash
        }

    def export_certificate(self) -> Dict[str, Any]:
        """Export verification certificate."""
        return {
            "certificate": {
                "version": "1.0",
                "type": "constraint_proof",
                "frame_hash": self.frame_hash,
                "timestamp": self.timestamp,
                "all_satisfied": self.all_satisfied,
                "verification_hash": self.verification_hash
            },
            "proof": {
                "constraints": self.constraints_checked,
                "iterations": self.solver_iterations
            }
        }


@dataclass
class Frame:
    """
    A frame is a tandem pair: (layout, proof).

    The layout contains the solved element positions.
    The proof certifies all constraints were satisfied.

    Invalid visual states are unrepresentable—if constraints
    cannot be satisfied, no frame is produced (finfr).
    """
    elements: Dict[str, VisualElement]
    proof: ConstraintProof
    viewport: Rect
    frame_number: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_number": self.frame_number,
            "viewport": {
                "x": self.viewport.x,
                "y": self.viewport.y,
                "width": self.viewport.width,
                "height": self.viewport.height
            },
            "elements": [el.to_dict() for el in self.elements.values()],
            "proof": self.proof.to_dict()
        }

    def get_element(self, element_id: str) -> Optional[VisualElement]:
        """Get element by ID."""
        return self.elements.get(element_id)

    def elements_at_point(self, x: float, y: float) -> List[VisualElement]:
        """Get all elements at a point, sorted by z-index (top first)."""
        hits = [
            el for el in self.elements.values()
            if el.visible and el.bounds.contains_point(x, y)
        ]
        return sorted(hits, key=lambda e: e.z_index, reverse=True)


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSITOR BLUEPRINT
# ═══════════════════════════════════════════════════════════════════════════════

class CompositorBlueprint(Blueprint):
    """
    Newton Constraint Compositor.

    A compositor that SOLVES instead of stacks.

    Traditional: "Put A at (100, 200), B at (150, 250)"
    Newton: "A and B must not overlap. B right of A. Solve."

    Every frame is a tandem pair: (layout, proof).
    If constraints cannot be satisfied, the frame cannot exist (finfr).

    Usage:
        compositor = CompositorBlueprint(viewport=Rect(0, 0, 1920, 1080))

        # Add elements
        compositor.add_element(VisualElement("panel_a", Rect(100, 100, 200, 200)))
        compositor.add_element(VisualElement("panel_b", Rect(150, 150, 200, 200)))

        # Add constraints
        compositor.add_constraint(NoOverlap("panel_a", "panel_b"))
        compositor.add_constraint(FullyVisible("panel_a"))
        compositor.add_constraint(FullyVisible("panel_b"))

        # Render frame (solves constraints, produces proof)
        frame = compositor.render()

        # frame.elements contains solved positions
        # frame.proof certifies all constraints satisfied
    """

    viewport = field(Rect, default=None)
    frame_count = field(int, default=0)

    def __init__(self, viewport: Rect = None, **kwargs):
        super().__init__(**kwargs)
        self.viewport = viewport or Rect(0, 0, 1920, 1080)
        self._elements: Dict[str, VisualElement] = {}
        self._constraints: List[VisualConstraint] = []
        self._solver = ConstraintSolver()
        self.frame_count = 0

    # ─────────────────────────────────────────────────────────────────────────
    # Laws - Governance Layer
    # ─────────────────────────────────────────────────────────────────────────

    @law
    def valid_viewport(self):
        """Viewport must have positive dimensions."""
        when(
            self.viewport is None or
            self.viewport.width <= 0 or
            self.viewport.height <= 0,
            finfr
        )

    @law
    def no_duplicate_ids(self):
        """Element IDs must be unique (enforced by dict, but explicit)."""
        # Implicitly satisfied by using dict
        pass

    # ─────────────────────────────────────────────────────────────────────────
    # Forges - Executive Layer
    # ─────────────────────────────────────────────────────────────────────────

    @forge
    def add_element(self, element: VisualElement) -> str:
        """Add a visual element to the compositor."""
        self._elements[element.id] = element
        return element.id

    @forge
    def remove_element(self, element_id: str) -> bool:
        """Remove a visual element."""
        if element_id in self._elements:
            del self._elements[element_id]
            return True
        return False

    @forge
    def update_element(self, element_id: str, **updates) -> bool:
        """Update element properties."""
        el = self._elements.get(element_id)
        if not el:
            return False

        new_bounds = el.bounds
        if 'x' in updates or 'y' in updates:
            new_bounds = Rect(
                updates.get('x', el.bounds.x),
                updates.get('y', el.bounds.y),
                updates.get('width', el.bounds.width),
                updates.get('height', el.bounds.height)
            )
        elif 'width' in updates or 'height' in updates:
            new_bounds = Rect(
                el.bounds.x,
                el.bounds.y,
                updates.get('width', el.bounds.width),
                updates.get('height', el.bounds.height)
            )

        self._elements[element_id] = VisualElement(
            id=element_id,
            bounds=new_bounds,
            color=updates.get('color', el.color),
            z_index=updates.get('z_index', el.z_index),
            visible=updates.get('visible', el.visible),
            content=updates.get('content', el.content),
            metadata={**el.metadata, **updates.get('metadata', {})}
        )
        return True

    def add_constraint(self, constraint: VisualConstraint) -> None:
        """Add a visual constraint."""
        self._constraints.append(constraint)

    def remove_constraint(self, name: str) -> bool:
        """Remove a constraint by name."""
        for i, c in enumerate(self._constraints):
            if c.name == name:
                self._constraints.pop(i)
                return True
        return False

    def clear_constraints(self) -> None:
        """Remove all constraints."""
        self._constraints.clear()

    # ─────────────────────────────────────────────────────────────────────────
    # Rendering
    # ─────────────────────────────────────────────────────────────────────────

    @forge
    def render(self) -> Frame:
        """
        Render a frame by solving all constraints.

        Returns Frame (layout, proof) tandem pair.
        Raises LawViolation if constraints cannot be satisfied.
        """
        # Solve constraints
        result = self._solver.solve(
            self._elements,
            self._constraints,
            self.viewport
        )

        if not result.success:
            # Constraints unsatisfiable - finfr
            violations = ", ".join(r.constraint_name for r in result.violated_constraints)
            raise LawViolation(
                "constraint_unsatisfiable",
                f"Cannot satisfy constraints: [{violations}]. "
                f"Invalid visual state is unrepresentable."
            )

        # Build proof
        self.frame_count += 1

        # Hash the frame state
        frame_data = {
            "frame_number": self.frame_count,
            "elements": sorted([el.to_dict() for el in result.elements.values()], key=lambda x: x['id']),
            "viewport": {"x": self.viewport.x, "y": self.viewport.y,
                        "w": self.viewport.width, "h": self.viewport.height}
        }
        frame_hash = hashlib.sha256(
            str(frame_data).encode()
        ).hexdigest()

        # Hash the verification
        verification_data = {
            "frame_hash": frame_hash,
            "constraints": result.satisfied_constraints,
            "iterations": result.iterations
        }
        verification_hash = hashlib.sha256(
            str(verification_data).encode()
        ).hexdigest()

        proof = ConstraintProof(
            frame_hash=frame_hash,
            timestamp=int(time.time() * 1000),
            constraints_checked=result.satisfied_constraints,
            all_satisfied=True,
            solver_iterations=result.iterations,
            verification_hash=verification_hash
        )

        return Frame(
            elements=result.elements,
            proof=proof,
            viewport=self.viewport,
            frame_number=self.frame_count
        )

    def try_render(self) -> Tuple[Optional[Frame], Optional[str]]:
        """
        Try to render, returning (Frame, None) on success or (None, error) on failure.

        Use this when you want to handle unsatisfiable constraints gracefully
        instead of raising finfr.
        """
        try:
            frame = self.render()
            return (frame, None)
        except LawViolation as e:
            return (None, str(e))

    def evaluate_constraints(self) -> List[ConstraintResult]:
        """Evaluate all constraints without solving/rendering."""
        return [
            c.evaluate(self._elements, self.viewport)
            for c in self._constraints
        ]

    # ─────────────────────────────────────────────────────────────────────────
    # State Access
    # ─────────────────────────────────────────────────────────────────────────

    def get_element(self, element_id: str) -> Optional[VisualElement]:
        """Get element by ID."""
        return self._elements.get(element_id)

    def get_all_elements(self) -> List[VisualElement]:
        """Get all elements."""
        return list(self._elements.values())

    def get_constraints(self) -> List[VisualConstraint]:
        """Get all constraints."""
        return list(self._constraints)

    def to_presence(self) -> Presence:
        """Convert current state to a Presence for motion calculations."""
        state = {
            el_id: {"x": el.bounds.x, "y": el.bounds.y}
            for el_id, el in self._elements.items()
        }
        return Presence(state=state, label=f"frame_{self.frame_count}")


# ═══════════════════════════════════════════════════════════════════════════════
# KINETIC COMPOSITOR - Animation with Constraints
# ═══════════════════════════════════════════════════════════════════════════════

class KineticCompositor(KineticEngine):
    """
    Compositor with motion support.

    Extends KineticEngine to animate between compositor states
    while maintaining constraint satisfaction at every frame.

    Usage:
        compositor = CompositorBlueprint(viewport)
        # ... add elements and constraints ...

        kinetic = KineticCompositor(compositor)

        # Animate element movement
        frames = kinetic.animate_to(
            target_positions={"panel_a": (200, 200)},
            steps=30
        )

        # Each frame in `frames` is a verified (layout, proof) pair
    """

    def __init__(self, compositor: CompositorBlueprint):
        super().__init__()
        self.compositor = compositor

    def animate_to(
        self,
        target_positions: Dict[str, Tuple[float, float]],
        steps: int = 10
    ) -> List[Frame]:
        """
        Animate elements to target positions while maintaining constraints.

        Returns list of Frame objects, each with proof of constraint satisfaction.
        Raises LawViolation if any intermediate frame violates constraints.
        """
        if steps < 2:
            steps = 2

        # Capture start positions
        start_positions = {
            el_id: (el.bounds.x, el.bounds.y)
            for el_id, el in self.compositor._elements.items()
        }

        frames = []

        for i in range(steps):
            t = i / (steps - 1)  # 0 to 1

            # Interpolate positions
            for el_id, (target_x, target_y) in target_positions.items():
                if el_id in start_positions:
                    start_x, start_y = start_positions[el_id]
                    current_x = start_x + (target_x - start_x) * t
                    current_y = start_y + (target_y - start_y) * t
                    self.compositor.update_element(el_id, x=current_x, y=current_y)

            # Render frame (will finfr if constraints violated)
            frame = self.compositor.render()
            frames.append(frame)

        return frames

    def transition(
        self,
        from_state: Dict[str, VisualElement],
        to_state: Dict[str, VisualElement],
        steps: int = 10
    ) -> List[Frame]:
        """
        Transition between two complete states.

        Both states must satisfy constraints.
        """
        # Set start state
        self.compositor._elements = {
            k: VisualElement(
                id=v.id,
                bounds=Rect(v.bounds.x, v.bounds.y, v.bounds.width, v.bounds.height),
                color=v.color,
                z_index=v.z_index,
                visible=v.visible,
                content=v.content,
                metadata=v.metadata.copy()
            )
            for k, v in from_state.items()
        }

        # Build target positions
        target_positions = {
            el_id: (el.bounds.x, el.bounds.y)
            for el_id, el in to_state.items()
        }

        return self.animate_to(target_positions, steps)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_compositor(
    width: int = 1920,
    height: int = 1080
) -> CompositorBlueprint:
    """Create a compositor with the given viewport dimensions."""
    return CompositorBlueprint(viewport=Rect(0, 0, width, height))


def verify_frame(frame: Frame, constraints: List[VisualConstraint]) -> bool:
    """
    Independently verify that a frame satisfies all constraints.

    This allows external verification of frame proofs.
    """
    for constraint in constraints:
        result = constraint.evaluate(frame.elements, frame.viewport)
        if result.violated and constraint.is_required():
            return False
    return True


def frame_to_presence(frame: Frame) -> Presence:
    """Convert a Frame to a Presence for kinetic calculations."""
    state = {
        el_id: {
            "x": el.bounds.x,
            "y": el.bounds.y,
            "width": el.bounds.width,
            "height": el.bounds.height
        }
        for el_id, el in frame.elements.items()
    }
    return Presence(
        state=state,
        timestamp=frame.proof.timestamp / 1000.0,
        label=f"frame_{frame.frame_number}"
    )
