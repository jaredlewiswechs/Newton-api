"""
═══════════════════════════════════════════════════════════════════════════════
 Newton Interface Builder - Verified UI Generation System
═══════════════════════════════════════════════════════════════════════════════

Build verified interfaces from natural language intent. The "Tiny Tank" pattern
ensures every UI component passes constraint verification before generation.

"The interface IS the specification. The template IS the constraint."

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable
from enum import Enum
from .core import Blueprint, field as tt_field, forge, law, when, finfr, LawViolation, ratio
import hashlib
import time
import json
import re


# ═══════════════════════════════════════════════════════════════════════════════
# INTERFACE TYPES & COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

class ComponentType(Enum):
    """Types of UI components that can be generated."""
    # Layout
    CONTAINER = "container"
    GRID = "grid"
    FLEX = "flex"
    SIDEBAR = "sidebar"
    HEADER = "header"
    FOOTER = "footer"
    CARD = "card"
    MODAL = "modal"

    # Input
    BUTTON = "button"
    INPUT = "input"
    TEXTAREA = "textarea"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TOGGLE = "toggle"
    SLIDER = "slider"

    # Display
    TEXT = "text"
    HEADING = "heading"
    BADGE = "badge"
    METRIC = "metric"
    CODE = "code"
    TABLE = "table"
    LIST = "list"
    IMAGE = "image"
    ICON = "icon"

    # Feedback
    ALERT = "alert"
    TOAST = "toast"
    PROGRESS = "progress"
    SPINNER = "spinner"
    SKELETON = "skeleton"


class InterfaceType(Enum):
    """Types of interfaces that can be built."""
    FORM = "form"
    DASHBOARD = "dashboard"
    BUILDER = "builder"
    LANDING = "landing"
    SETTINGS = "settings"
    DATA_TABLE = "data_table"
    WIZARD = "wizard"
    EMPTY_STATE = "empty_state"


class LayoutPattern(Enum):
    """Common layout patterns."""
    SINGLE_COLUMN = "single_column"
    TWO_COLUMN = "two_column"
    THREE_COLUMN = "three_column"
    SIDEBAR_CONTENT = "sidebar_content"
    HEADER_CONTENT = "header_content"
    DASHBOARD_GRID = "dashboard_grid"
    CARD_GRID = "card_grid"
    MASONRY = "masonry"
    SPLIT = "split"


class Variant(Enum):
    """Component style variants."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DANGER = "danger"
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"
    GHOST = "ghost"
    OUTLINE = "outline"
    LINK = "link"


class Size(Enum):
    """Component sizes."""
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"


# ═══════════════════════════════════════════════════════════════════════════════
# COMPONENT DEFINITION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Component:
    """
    A verified UI component specification.

    Every component has constraints that must be satisfied for generation.
    """
    id: str
    type: ComponentType
    props: Dict[str, Any] = field(default_factory=dict)
    children: List['Component'] = field(default_factory=list)
    variant: Variant = Variant.PRIMARY
    size: Size = Size.MD
    className: str = ""
    constraints: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "props": self.props,
            "children": [c.to_dict() for c in self.children],
            "variant": self.variant.value,
            "size": self.size.value,
            "className": self.className,
            "constraints": self.constraints
        }

    def to_jsx(self, indent: int = 0) -> str:
        """Generate JSX code for this component."""
        pad = "  " * indent

        # Map component types to Newton component names
        component_map = {
            ComponentType.BUTTON: "Button",
            ComponentType.INPUT: "Input",
            ComponentType.CARD: "Card",
            ComponentType.BADGE: "Badge",
            ComponentType.METRIC: "Metric",
            ComponentType.CODE: "CodeBlock",
            ComponentType.SIDEBAR: "Sidebar",
            ComponentType.MODAL: "Modal",
            ComponentType.HEADING: "h1",
            ComponentType.TEXT: "p",
            ComponentType.CONTAINER: "div",
            ComponentType.GRID: "div",
            ComponentType.FLEX: "div",
        }

        tag = component_map.get(self.type, "div")

        # Build props string
        props_list = []
        if self.variant != Variant.PRIMARY:
            props_list.append(f'variant="{self.variant.value}"')
        if self.size != Size.MD:
            props_list.append(f'size="{self.size.value}"')
        if self.className:
            props_list.append(f'className="{self.className}"')
        for key, value in self.props.items():
            if isinstance(value, str):
                props_list.append(f'{key}="{value}"')
            elif isinstance(value, bool):
                if value:
                    props_list.append(key)
            else:
                props_list.append(f'{key}={{{json.dumps(value)}}}')

        props_str = " " + " ".join(props_list) if props_list else ""

        if self.children:
            children_jsx = "\n".join(c.to_jsx(indent + 1) for c in self.children)
            return f"{pad}<{tag}{props_str}>\n{children_jsx}\n{pad}</{tag}>"
        elif "content" in self.props or "label" in self.props:
            content = self.props.get("content") or self.props.get("label", "")
            return f"{pad}<{tag}{props_str}>{content}</{tag}>"
        else:
            return f"{pad}<{tag}{props_str} />"

    def to_html(self, indent: int = 0) -> str:
        """Generate HTML code for this component."""
        pad = "  " * indent

        # Map component types to HTML elements with Newton classes
        html_map = {
            ComponentType.BUTTON: ("button", "newton-button"),
            ComponentType.INPUT: ("input", "newton-input"),
            ComponentType.CARD: ("div", "newton-card"),
            ComponentType.BADGE: ("span", "newton-badge"),
            ComponentType.METRIC: ("div", "newton-metric"),
            ComponentType.CODE: ("pre", "newton-code-block"),
            ComponentType.SIDEBAR: ("aside", "newton-sidebar"),
            ComponentType.MODAL: ("div", "newton-modal"),
            ComponentType.HEADING: ("h1", ""),
            ComponentType.TEXT: ("p", ""),
            ComponentType.CONTAINER: ("div", "newton-container"),
            ComponentType.GRID: ("div", "newton-grid"),
            ComponentType.FLEX: ("div", "newton-flex"),
            ComponentType.HEADER: ("header", "newton-header"),
            ComponentType.FOOTER: ("footer", "newton-footer"),
        }

        tag, base_class = html_map.get(self.type, ("div", ""))

        # Build class list
        classes = [base_class] if base_class else []
        if self.variant != Variant.PRIMARY:
            classes.append(f"{base_class}--{self.variant.value}" if base_class else self.variant.value)
        if self.size != Size.MD:
            classes.append(f"{base_class}--{self.size.value}" if base_class else self.size.value)
        if self.className:
            classes.append(self.className)

        class_str = f' class="{" ".join(classes)}"' if classes else ""

        # Build other attributes
        attrs = []
        for key, value in self.props.items():
            if key not in ["content", "label", "children"]:
                if isinstance(value, bool):
                    if value:
                        attrs.append(key)
                else:
                    attrs.append(f'{key}="{value}"')
        attrs_str = " " + " ".join(attrs) if attrs else ""

        if self.children:
            children_html = "\n".join(c.to_html(indent + 1) for c in self.children)
            return f"{pad}<{tag}{class_str}{attrs_str}>\n{children_html}\n{pad}</{tag}>"
        elif "content" in self.props or "label" in self.props:
            content = self.props.get("content") or self.props.get("label", "")
            return f"{pad}<{tag}{class_str}{attrs_str}>{content}</{tag}>"
        else:
            return f"{pad}<{tag}{class_str}{attrs_str}></{tag}>"


@dataclass
class InterfaceSpec:
    """
    Complete interface specification with all components and layout.
    """
    id: str
    name: str
    type: InterfaceType
    layout: LayoutPattern
    components: List[Component] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    styles: Dict[str, str] = field(default_factory=dict)
    scripts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "layout": self.layout.value,
            "components": [c.to_dict() for c in self.components],
            "meta": self.meta,
            "styles": self.styles,
            "scripts": self.scripts
        }

    def to_jsx(self) -> str:
        """Generate complete React component."""
        component_jsx = "\n".join(c.to_jsx(2) for c in self.components)

        layout_class = {
            LayoutPattern.SINGLE_COLUMN: "newton-layout--single",
            LayoutPattern.TWO_COLUMN: "newton-layout--two-column",
            LayoutPattern.THREE_COLUMN: "newton-layout--three-column",
            LayoutPattern.SIDEBAR_CONTENT: "newton-layout",
            LayoutPattern.DASHBOARD_GRID: "newton-metrics-grid",
            LayoutPattern.CARD_GRID: "newton-card-grid",
        }.get(self.layout, "newton-layout")

        return f'''import React from 'react';
import {{ Button, Input, Card, Badge, Metric, Sidebar, Modal }} from '@/components';
import './styles.css';

export const {self.name.replace(" ", "")} = () => {{
  return (
    <div className="{layout_class}">
{component_jsx}
    </div>
  );
}};

export default {self.name.replace(" ", "")};'''

    def to_html(self) -> str:
        """Generate complete HTML page."""
        component_html = "\n".join(c.to_html(3) for c in self.components)

        layout_class = {
            LayoutPattern.SINGLE_COLUMN: "newton-layout--single",
            LayoutPattern.TWO_COLUMN: "newton-layout--two-column",
            LayoutPattern.THREE_COLUMN: "newton-layout--three-column",
            LayoutPattern.SIDEBAR_CONTENT: "newton-layout",
            LayoutPattern.DASHBOARD_GRID: "newton-metrics-grid",
            LayoutPattern.CARD_GRID: "newton-card-grid",
        }.get(self.layout, "newton-layout")

        custom_styles = "\n".join(f"    {k}: {v};" for k, v in self.styles.items())

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.name} - Newton Interface Builder</title>
    <link rel="stylesheet" href="/styles.css">
    <style>
        :root {{
{custom_styles}
        }}
    </style>
</head>
<body>
    <div class="{layout_class}">
{component_html}
    </div>
    <script src="/app.js"></script>
</body>
</html>'''


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATES - Pre-built Interface Patterns
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Template:
    """A reusable interface template."""
    id: str
    name: str
    description: str
    type: InterfaceType
    layout: LayoutPattern
    preview_image: str = ""
    tags: List[str] = field(default_factory=list)
    components: List[Component] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "layout": self.layout.value,
            "preview_image": self.preview_image,
            "tags": self.tags,
            "component_count": len(self.components),
            "variables": list(self.variables.keys())
        }

    def instantiate(self, variables: Dict[str, Any] = None) -> InterfaceSpec:
        """Create an interface from this template with given variables."""
        vars_to_use = {**self.variables, **(variables or {})}

        # Deep copy components and substitute variables
        components = self._substitute_components(self.components, vars_to_use)

        return InterfaceSpec(
            id=f"{self.id}_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}",
            name=vars_to_use.get("title", self.name),
            type=self.type,
            layout=self.layout,
            components=components,
            meta={"template_id": self.id, "variables": vars_to_use}
        )

    def _substitute_components(self, components: List[Component], vars: Dict[str, Any]) -> List[Component]:
        """Substitute template variables in components."""
        result = []
        for comp in components:
            new_props = {}
            for key, value in comp.props.items():
                if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                    var_name = value[2:-2].strip()
                    new_props[key] = vars.get(var_name, value)
                else:
                    new_props[key] = value

            new_children = self._substitute_components(comp.children, vars) if comp.children else []

            result.append(Component(
                id=comp.id,
                type=comp.type,
                props=new_props,
                children=new_children,
                variant=comp.variant,
                size=comp.size,
                className=comp.className,
                constraints=comp.constraints
            ))
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE LIBRARY - Built-in Templates
# ═══════════════════════════════════════════════════════════════════════════════

class TemplateLibrary:
    """Library of pre-built interface templates."""

    def __init__(self):
        self._templates: Dict[str, Template] = {}
        self._load_built_in_templates()

    def _load_built_in_templates(self):
        """Load all built-in templates."""

        # Dashboard Template
        self._add_template(Template(
            id="dashboard-basic",
            name="Basic Dashboard",
            description="A simple dashboard with metrics and activity feed",
            type=InterfaceType.DASHBOARD,
            layout=LayoutPattern.SIDEBAR_CONTENT,
            tags=["dashboard", "metrics", "analytics", "starter"],
            variables={
                "title": "Dashboard",
                "metric1_value": "0",
                "metric1_label": "Total",
                "metric2_value": "0",
                "metric2_label": "Active",
                "metric3_value": "0",
                "metric3_label": "Pending",
                "metric4_value": "0",
                "metric4_label": "Rate"
            },
            components=[
                Component(
                    id="sidebar",
                    type=ComponentType.SIDEBAR,
                    props={"productName": "{{title}}"},
                    children=[
                        Component(id="nav-dashboard", type=ComponentType.BUTTON, props={"label": "Dashboard"}, variant=Variant.GHOST),
                        Component(id="nav-analytics", type=ComponentType.BUTTON, props={"label": "Analytics"}, variant=Variant.GHOST),
                        Component(id="nav-settings", type=ComponentType.BUTTON, props={"label": "Settings"}, variant=Variant.GHOST),
                    ]
                ),
                Component(
                    id="main-content",
                    type=ComponentType.CONTAINER,
                    className="newton-main",
                    children=[
                        Component(id="header", type=ComponentType.HEADER, props={"content": "{{title}}"}),
                        Component(
                            id="metrics-grid",
                            type=ComponentType.GRID,
                            className="newton-metrics-grid",
                            children=[
                                Component(id="metric-1", type=ComponentType.METRIC, props={"value": "{{metric1_value}}", "label": "{{metric1_label}}"}),
                                Component(id="metric-2", type=ComponentType.METRIC, props={"value": "{{metric2_value}}", "label": "{{metric2_label}}"}),
                                Component(id="metric-3", type=ComponentType.METRIC, props={"value": "{{metric3_value}}", "label": "{{metric3_label}}"}),
                                Component(id="metric-4", type=ComponentType.METRIC, props={"value": "{{metric4_value}}", "label": "{{metric4_label}}"}),
                            ]
                        ),
                        Component(id="activity-card", type=ComponentType.CARD, props={"title": "Recent Activity"})
                    ]
                )
            ]
        ))

        # Form Template
        self._add_template(Template(
            id="form-contact",
            name="Contact Form",
            description="A simple contact form with validation",
            type=InterfaceType.FORM,
            layout=LayoutPattern.SINGLE_COLUMN,
            tags=["form", "contact", "input", "validation"],
            variables={
                "title": "Contact Us",
                "submit_label": "Send Message",
                "name_placeholder": "Your Name",
                "email_placeholder": "your@email.com",
                "message_placeholder": "Your message..."
            },
            components=[
                Component(id="form-container", type=ComponentType.CARD, className="newton-form-card", children=[
                    Component(id="form-title", type=ComponentType.HEADING, props={"content": "{{title}}"}),
                    Component(id="name-input", type=ComponentType.INPUT, props={"placeholder": "{{name_placeholder}}", "name": "name", "required": True}),
                    Component(id="email-input", type=ComponentType.INPUT, props={"placeholder": "{{email_placeholder}}", "name": "email", "type": "email", "required": True}),
                    Component(id="message-input", type=ComponentType.TEXTAREA, props={"placeholder": "{{message_placeholder}}", "name": "message", "rows": 4}),
                    Component(id="submit-btn", type=ComponentType.BUTTON, props={"label": "{{submit_label}}"}, variant=Variant.PRIMARY),
                ])
            ]
        ))

        # Empty State Template
        self._add_template(Template(
            id="empty-state-basic",
            name="Empty State",
            description="An empty state with illustration and CTA",
            type=InterfaceType.EMPTY_STATE,
            layout=LayoutPattern.SINGLE_COLUMN,
            tags=["empty", "placeholder", "onboarding"],
            variables={
                "title": "No items yet",
                "description": "Get started by creating your first item.",
                "cta_label": "Create Item"
            },
            components=[
                Component(id="empty-container", type=ComponentType.CONTAINER, className="newton-empty-state", children=[
                    Component(id="empty-icon", type=ComponentType.ICON, props={"name": "inbox", "size": 64}),
                    Component(id="empty-title", type=ComponentType.HEADING, props={"content": "{{title}}"}),
                    Component(id="empty-desc", type=ComponentType.TEXT, props={"content": "{{description}}"}),
                    Component(id="empty-cta", type=ComponentType.BUTTON, props={"label": "{{cta_label}}"}, variant=Variant.PRIMARY),
                ])
            ]
        ))

        # Settings Template
        self._add_template(Template(
            id="settings-basic",
            name="Settings Page",
            description="A settings page with sections and toggles",
            type=InterfaceType.SETTINGS,
            layout=LayoutPattern.SIDEBAR_CONTENT,
            tags=["settings", "preferences", "config"],
            variables={
                "title": "Settings",
                "section1_title": "General",
                "section2_title": "Notifications"
            },
            components=[
                Component(id="settings-sidebar", type=ComponentType.SIDEBAR, children=[
                    Component(id="nav-general", type=ComponentType.BUTTON, props={"label": "General"}, variant=Variant.GHOST),
                    Component(id="nav-notifications", type=ComponentType.BUTTON, props={"label": "Notifications"}, variant=Variant.GHOST),
                    Component(id="nav-security", type=ComponentType.BUTTON, props={"label": "Security"}, variant=Variant.GHOST),
                    Component(id="nav-billing", type=ComponentType.BUTTON, props={"label": "Billing"}, variant=Variant.GHOST),
                ]),
                Component(id="settings-content", type=ComponentType.CONTAINER, className="newton-main", children=[
                    Component(id="settings-header", type=ComponentType.HEADER, props={"content": "{{title}}"}),
                    Component(id="section-general", type=ComponentType.CARD, props={"title": "{{section1_title}}"}, children=[
                        Component(id="toggle-dark", type=ComponentType.TOGGLE, props={"label": "Dark Mode", "checked": True}),
                        Component(id="toggle-compact", type=ComponentType.TOGGLE, props={"label": "Compact View", "checked": False}),
                    ]),
                    Component(id="section-notifications", type=ComponentType.CARD, props={"title": "{{section2_title}}"}, children=[
                        Component(id="toggle-email", type=ComponentType.TOGGLE, props={"label": "Email Notifications", "checked": True}),
                        Component(id="toggle-push", type=ComponentType.TOGGLE, props={"label": "Push Notifications", "checked": False}),
                    ]),
                ])
            ]
        ))

        # Data Table Template
        self._add_template(Template(
            id="data-table-basic",
            name="Data Table",
            description="A data table with search and actions",
            type=InterfaceType.DATA_TABLE,
            layout=LayoutPattern.SINGLE_COLUMN,
            tags=["table", "data", "list", "crud"],
            variables={
                "title": "Items",
                "search_placeholder": "Search items...",
                "add_label": "Add Item"
            },
            components=[
                Component(id="table-container", type=ComponentType.CONTAINER, className="newton-table-view", children=[
                    Component(id="table-header", type=ComponentType.FLEX, className="newton-table-header", children=[
                        Component(id="table-title", type=ComponentType.HEADING, props={"content": "{{title}}"}),
                        Component(id="table-actions", type=ComponentType.FLEX, className="newton-table-actions", children=[
                            Component(id="search-input", type=ComponentType.INPUT, props={"placeholder": "{{search_placeholder}}", "type": "search"}),
                            Component(id="add-btn", type=ComponentType.BUTTON, props={"label": "{{add_label}}"}, variant=Variant.PRIMARY),
                        ])
                    ]),
                    Component(id="table", type=ComponentType.TABLE, props={"columns": ["Name", "Status", "Date", "Actions"]}),
                ])
            ]
        ))

        # Landing Page Template
        self._add_template(Template(
            id="landing-hero",
            name="Landing Hero",
            description="A hero section for landing pages",
            type=InterfaceType.LANDING,
            layout=LayoutPattern.SINGLE_COLUMN,
            tags=["landing", "hero", "marketing"],
            variables={
                "title": "Build Verified Interfaces",
                "subtitle": "The Newton Interface Builder generates production-ready UI from natural language.",
                "cta_primary": "Get Started",
                "cta_secondary": "Learn More"
            },
            components=[
                Component(id="hero", type=ComponentType.CONTAINER, className="newton-hero", children=[
                    Component(id="hero-content", type=ComponentType.CONTAINER, className="newton-hero-content", children=[
                        Component(id="hero-badge", type=ComponentType.BADGE, props={"content": "✓ Verified"}, variant=Variant.SUCCESS),
                        Component(id="hero-title", type=ComponentType.HEADING, props={"content": "{{title}}"}),
                        Component(id="hero-subtitle", type=ComponentType.TEXT, props={"content": "{{subtitle}}"}),
                        Component(id="hero-ctas", type=ComponentType.FLEX, className="newton-hero-ctas", children=[
                            Component(id="cta-primary", type=ComponentType.BUTTON, props={"label": "{{cta_primary}}"}, variant=Variant.PRIMARY, size=Size.LG),
                            Component(id="cta-secondary", type=ComponentType.BUTTON, props={"label": "{{cta_secondary}}"}, variant=Variant.SECONDARY, size=Size.LG),
                        ])
                    ])
                ])
            ]
        ))

        # Wizard/Stepper Template
        self._add_template(Template(
            id="wizard-basic",
            name="Step Wizard",
            description="A multi-step wizard/stepper form",
            type=InterfaceType.WIZARD,
            layout=LayoutPattern.SINGLE_COLUMN,
            tags=["wizard", "stepper", "multi-step", "onboarding"],
            variables={
                "title": "Get Started",
                "step1_title": "Account",
                "step2_title": "Profile",
                "step3_title": "Confirm"
            },
            components=[
                Component(id="wizard-container", type=ComponentType.CARD, className="newton-wizard", children=[
                    Component(id="wizard-header", type=ComponentType.HEADING, props={"content": "{{title}}"}),
                    Component(id="wizard-steps", type=ComponentType.FLEX, className="newton-wizard-steps", children=[
                        Component(id="step-1", type=ComponentType.BADGE, props={"content": "1. {{step1_title}}"}, variant=Variant.PRIMARY),
                        Component(id="step-2", type=ComponentType.BADGE, props={"content": "2. {{step2_title}}"}, variant=Variant.GHOST),
                        Component(id="step-3", type=ComponentType.BADGE, props={"content": "3. {{step3_title}}"}, variant=Variant.GHOST),
                    ]),
                    Component(id="wizard-content", type=ComponentType.CONTAINER, className="newton-wizard-content"),
                    Component(id="wizard-footer", type=ComponentType.FLEX, className="newton-wizard-footer", children=[
                        Component(id="btn-back", type=ComponentType.BUTTON, props={"label": "Back"}, variant=Variant.SECONDARY),
                        Component(id="btn-next", type=ComponentType.BUTTON, props={"label": "Next"}, variant=Variant.PRIMARY),
                    ])
                ])
            ]
        ))

    def _add_template(self, template: Template):
        """Add a template to the library."""
        self._templates[template.id] = template

    def get(self, template_id: str) -> Optional[Template]:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def list_all(self) -> List[Dict[str, Any]]:
        """List all templates."""
        return [t.to_dict() for t in self._templates.values()]

    def search(self, query: str = "", type: InterfaceType = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Search templates by query, type, or tags."""
        results = []
        for template in self._templates.values():
            # Type filter
            if type and template.type != type:
                continue

            # Tag filter
            if tags:
                if not any(tag in template.tags for tag in tags):
                    continue

            # Query filter
            if query:
                query_lower = query.lower()
                if not (
                    query_lower in template.name.lower() or
                    query_lower in template.description.lower() or
                    any(query_lower in tag for tag in template.tags)
                ):
                    continue

            results.append(template.to_dict())

        return results


# ═══════════════════════════════════════════════════════════════════════════════
# INTERFACE BUILDER BLUEPRINT
# ═══════════════════════════════════════════════════════════════════════════════

class InterfaceBuilder(Blueprint):
    """
    The Interface Builder Blueprint.

    Builds verified interfaces from natural language intent.
    Uses the "Tiny Tank" pattern: define what CANNOT happen first.
    """

    # Fields
    components = tt_field(list, default=[])
    max_components = tt_field(int, default=100)
    max_depth = tt_field(int, default=10)
    allowed_types = tt_field(list, default=None)

    @law
    def component_limit(self):
        """Cannot exceed maximum component count."""
        when(len(self.components) > self.max_components, finfr)

    @law
    def depth_limit(self):
        """Cannot exceed maximum nesting depth."""
        max_found = self._calculate_max_depth(self.components)
        when(max_found > self.max_depth, finfr)

    @law
    def valid_types(self):
        """All components must have valid types."""
        if self.allowed_types:
            for comp in self._flatten_components(self.components):
                when(comp.type.value not in self.allowed_types, finfr)

    def _calculate_max_depth(self, components: List[Component], current_depth: int = 1) -> int:
        """Calculate maximum nesting depth."""
        if not components:
            return current_depth - 1
        max_child_depth = current_depth
        for comp in components:
            if comp.children:
                child_depth = self._calculate_max_depth(comp.children, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
        return max_child_depth

    def _flatten_components(self, components: List[Component]) -> List[Component]:
        """Flatten nested components into a list."""
        result = []
        for comp in components:
            result.append(comp)
            if comp.children:
                result.extend(self._flatten_components(comp.children))
        return result

    @forge
    def add_component(self, component: Component) -> str:
        """Add a component to the interface."""
        self.components.append(component)
        return f"Added component: {component.id}"

    @forge
    def remove_component(self, component_id: str) -> str:
        """Remove a component by ID."""
        self.components = [c for c in self.components if c.id != component_id]
        return f"Removed component: {component_id}"

    @forge
    def clear(self) -> str:
        """Clear all components."""
        self.components = []
        return "Cleared all components"


# ═══════════════════════════════════════════════════════════════════════════════
# INTERFACE BUILDER CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class InterfaceBuilderCartridge:
    """
    The Interface Builder Cartridge.

    Provides high-level interface generation from intent.
    """

    def __init__(self):
        self.template_library = TemplateLibrary()
        self.builder = InterfaceBuilder()

    def get_templates(self, query: str = "", type: str = None, tags: List[str] = None) -> Dict[str, Any]:
        """Get available templates."""
        type_enum = InterfaceType(type) if type else None
        return {
            "templates": self.template_library.search(query, type_enum, tags),
            "total": len(self.template_library.list_all())
        }

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by ID."""
        template = self.template_library.get(template_id)
        if template:
            return template.to_dict()
        return None

    def build_from_template(
        self,
        template_id: str,
        variables: Dict[str, Any] = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """Build an interface from a template."""
        start_time = time.perf_counter_ns()

        template = self.template_library.get(template_id)
        if not template:
            return {
                "verified": False,
                "error": f"Template not found: {template_id}",
                "elapsed_us": 0
            }

        try:
            # Instantiate template with variables
            interface = template.instantiate(variables)

            elapsed_ns = time.perf_counter_ns() - start_time
            elapsed_us = elapsed_ns / 1000

            # Generate output based on format
            output = {
                "verified": True,
                "interface": interface.to_dict(),
                "elapsed_us": elapsed_us,
                "template_id": template_id,
                "fingerprint": hashlib.sha256(json.dumps(interface.to_dict()).encode()).hexdigest()[:16]
            }

            if output_format == "jsx":
                output["jsx"] = interface.to_jsx()
            elif output_format == "html":
                output["html"] = interface.to_html()
            elif output_format == "all":
                output["jsx"] = interface.to_jsx()
                output["html"] = interface.to_html()

            return output

        except LawViolation as e:
            elapsed_ns = time.perf_counter_ns() - start_time
            return {
                "verified": False,
                "error": f"Law violation: {e.message}",
                "law": e.law_name,
                "elapsed_us": elapsed_ns / 1000
            }

    def build_from_spec(
        self,
        spec: Dict[str, Any],
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """Build an interface from a component specification."""
        start_time = time.perf_counter_ns()

        try:
            # Parse components from spec
            components = self._parse_components(spec.get("components", []))

            # Create interface spec
            interface = InterfaceSpec(
                id=spec.get("id", f"interface_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"),
                name=spec.get("name", "Untitled Interface"),
                type=InterfaceType(spec.get("type", "dashboard")),
                layout=LayoutPattern(spec.get("layout", "single_column")),
                components=components,
                meta=spec.get("meta", {}),
                styles=spec.get("styles", {}),
                scripts=spec.get("scripts", [])
            )

            elapsed_ns = time.perf_counter_ns() - start_time
            elapsed_us = elapsed_ns / 1000

            output = {
                "verified": True,
                "interface": interface.to_dict(),
                "elapsed_us": elapsed_us,
                "fingerprint": hashlib.sha256(json.dumps(interface.to_dict()).encode()).hexdigest()[:16]
            }

            if output_format == "jsx":
                output["jsx"] = interface.to_jsx()
            elif output_format == "html":
                output["html"] = interface.to_html()
            elif output_format == "all":
                output["jsx"] = interface.to_jsx()
                output["html"] = interface.to_html()

            return output

        except (ValueError, KeyError) as e:
            elapsed_ns = time.perf_counter_ns() - start_time
            return {
                "verified": False,
                "error": f"Invalid specification: {str(e)}",
                "elapsed_us": elapsed_ns / 1000
            }
        except LawViolation as e:
            elapsed_ns = time.perf_counter_ns() - start_time
            return {
                "verified": False,
                "error": f"Law violation: {e.message}",
                "law": e.law_name,
                "elapsed_us": elapsed_ns / 1000
            }

    def _parse_components(self, component_dicts: List[Dict[str, Any]]) -> List[Component]:
        """Parse component dictionaries into Component objects."""
        components = []
        for comp_dict in component_dicts:
            comp = Component(
                id=comp_dict.get("id", f"comp_{len(components)}"),
                type=ComponentType(comp_dict.get("type", "container")),
                props=comp_dict.get("props", {}),
                variant=Variant(comp_dict.get("variant", "primary")),
                size=Size(comp_dict.get("size", "md")),
                className=comp_dict.get("className", ""),
                constraints=comp_dict.get("constraints", {}),
                children=self._parse_components(comp_dict.get("children", []))
            )
            components.append(comp)
        return components

    def get_component_types(self) -> List[Dict[str, Any]]:
        """Get all available component types."""
        return [
            {"value": t.value, "name": t.name, "category": self._get_category(t)}
            for t in ComponentType
        ]

    def _get_category(self, component_type: ComponentType) -> str:
        """Get the category for a component type."""
        layout_types = {ComponentType.CONTAINER, ComponentType.GRID, ComponentType.FLEX,
                       ComponentType.SIDEBAR, ComponentType.HEADER, ComponentType.FOOTER,
                       ComponentType.CARD, ComponentType.MODAL}
        input_types = {ComponentType.BUTTON, ComponentType.INPUT, ComponentType.TEXTAREA,
                      ComponentType.SELECT, ComponentType.CHECKBOX, ComponentType.RADIO,
                      ComponentType.TOGGLE, ComponentType.SLIDER}
        display_types = {ComponentType.TEXT, ComponentType.HEADING, ComponentType.BADGE,
                        ComponentType.METRIC, ComponentType.CODE, ComponentType.TABLE,
                        ComponentType.LIST, ComponentType.IMAGE, ComponentType.ICON}
        feedback_types = {ComponentType.ALERT, ComponentType.TOAST, ComponentType.PROGRESS,
                         ComponentType.SPINNER, ComponentType.SKELETON}

        if component_type in layout_types:
            return "layout"
        elif component_type in input_types:
            return "input"
        elif component_type in display_types:
            return "display"
        elif component_type in feedback_types:
            return "feedback"
        return "other"

    def get_info(self) -> Dict[str, Any]:
        """Get information about the Interface Builder."""
        return {
            "name": "Newton Interface Builder",
            "version": "1.0.0",
            "description": "Build verified interfaces from templates and specifications",
            "philosophy": "The interface IS the specification. The template IS the constraint.",
            "capabilities": [
                "Build from 7+ pre-built templates",
                "Generate React JSX components",
                "Generate production HTML",
                "Verify component constraints",
                "Customize via template variables"
            ],
            "templates": len(self.template_library.list_all()),
            "component_types": len(ComponentType),
            "interface_types": [t.value for t in InterfaceType],
            "layout_patterns": [l.value for l in LayoutPattern],
            "output_formats": ["json", "jsx", "html", "all"]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

_interface_builder_instance: Optional[InterfaceBuilderCartridge] = None

def get_interface_builder() -> InterfaceBuilderCartridge:
    """Get or create the Interface Builder cartridge instance."""
    global _interface_builder_instance
    if _interface_builder_instance is None:
        _interface_builder_instance = InterfaceBuilderCartridge()
    return _interface_builder_instance
