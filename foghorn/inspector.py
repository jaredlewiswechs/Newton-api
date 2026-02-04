"""
═══════════════════════════════════════════════════════════════════════════════
FOGHORN INSPECTOR — Unified Object Inspection System
═══════════════════════════════════════════════════════════════════════════════

The Inspector is NeXTSTEP's killer feature: a universal panel that shows
detailed information about ANY selected object.

In Nina, the Inspector combines:
- General info (type, hash, timestamps)
- Object-specific attributes
- Meta Newton analysis (verification status)
- Ada understanding (semantic parsing)
- Grounding results (source citations)
- Bézier data (shape/trajectory)
- Available services (context menu)

This is the "glass box" principle in action.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type
from enum import Enum

from .objects import (
    FoghornObject, ObjectType, Card, Query, ResultSet,
    FileAsset, Task, Receipt, LinkCurve, Rule,
    get_object_store
)
from .services import get_service_registry, ServiceCategory


class InspectorTab(Enum):
    """Inspector panel tabs."""
    GENERAL = "general"
    ATTRIBUTES = "attributes"
    VERIFICATION = "verification"
    UNDERSTANDING = "understanding"
    SOURCES = "sources"
    BEZIER = "bezier"
    SERVICES = "services"
    CHAIN = "chain"


@dataclass
class InspectorSection:
    """A section within an inspector tab."""
    title: str
    fields: Dict[str, Any]
    collapsed: bool = False
    icon: str = ""


@dataclass
class InspectorTab:
    """An inspector tab with sections."""
    name: str
    icon: str
    sections: List[InspectorSection]
    enabled: bool = True


@dataclass
class InspectorData:
    """
    Complete inspector data for an object.
    
    This is the unified view that the UI renders.
    """
    
    # The inspected object
    obj: Optional[FoghornObject] = None
    
    # Tabs
    tabs: List[InspectorTab] = field(default_factory=list)
    
    # Quick actions
    actions: List[Dict[str, str]] = field(default_factory=list)
    
    # Status
    selection_count: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API/UI."""
        if not self.obj:
            return {"empty": True, "message": "No selection"}
        
        return {
            "object": self.obj.to_dict(),
            "tabs": [
                {
                    "name": tab.name,
                    "icon": tab.icon,
                    "enabled": tab.enabled,
                    "sections": [
                        {
                            "title": s.title,
                            "fields": s.fields,
                            "collapsed": s.collapsed,
                            "icon": s.icon,
                        }
                        for s in tab.sections if s is not None
                    ]
                }
                for tab in self.tabs
            ],
            "actions": self.actions,
            "selection_count": self.selection_count,
        }


class Inspector:
    """
    Unified inspector that generates InspectorData for any object.
    """
    
    def __init__(self):
        # Tab providers: functions that add tabs for specific object types
        self._tab_providers: Dict[ObjectType, List[Callable]] = {
            t: [] for t in ObjectType
        }
        
        # Global providers: run for all objects
        self._global_providers: List[Callable] = []
        
        # Register built-in providers
        self._register_builtin_providers()
    
    def _register_builtin_providers(self):
        """Register the built-in tab providers."""
        self.add_global_provider(self._general_tab)
        self.add_global_provider(self._attributes_tab)
        self.add_global_provider(self._chain_tab)
        self.add_global_provider(self._services_tab)
        
        # Type-specific
        self.add_provider(ObjectType.LINK_CURVE, self._bezier_tab)
        self.add_provider(ObjectType.CARD, self._verification_tab)
        self.add_provider(ObjectType.RESULT_SET, self._sources_tab)
    
    def add_provider(self, obj_type: ObjectType, provider: Callable):
        """Add a tab provider for an object type."""
        self._tab_providers[obj_type].append(provider)
    
    def add_global_provider(self, provider: Callable):
        """Add a provider that runs for all objects."""
        self._global_providers.append(provider)
    
    def inspect(self, obj: FoghornObject) -> InspectorData:
        """
        Generate InspectorData for an object.
        """
        data = InspectorData(obj=obj)
        
        # Run global providers
        for provider in self._global_providers:
            tab = provider(obj)
            if tab:
                data.tabs.append(tab)
        
        # Run type-specific providers
        for provider in self._tab_providers.get(obj.object_type, []):
            tab = provider(obj)
            if tab:
                data.tabs.append(tab)
        
        # Add quick actions
        data.actions = self._get_quick_actions(obj)
        
        return data
    
    def inspect_multiple(self, objects: List[FoghornObject]) -> InspectorData:
        """
        Generate InspectorData for multiple selected objects.
        """
        if not objects:
            return InspectorData()
        
        if len(objects) == 1:
            data = self.inspect(objects[0])
            data.selection_count = 1
            return data
        
        # Multiple selection: show summary
        data = InspectorData(
            obj=objects[0],  # Primary selection
            selection_count=len(objects),
        )
        
        # Summary tab
        type_counts = {}
        for obj in objects:
            t = obj.object_type.value
            type_counts[t] = type_counts.get(t, 0) + 1
        
        data.tabs.append(InspectorTab(
            name="Selection",
            icon="☑",
            sections=[
                InspectorSection(
                    title="Selected Objects",
                    fields={
                        "Count": len(objects),
                        **{f"{k.title()}s": v for k, v in type_counts.items()}
                    }
                )
            ]
        ))
        
        # Find common services
        common_services = None
        for obj in objects:
            services = set(s.name for s in get_service_registry().find_for_object(obj))
            if common_services is None:
                common_services = services
            else:
                common_services &= services
        
        if common_services:
            data.actions = [
                {"name": name, "available": True}
                for name in sorted(common_services)
            ]
        
        return data
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BUILT-IN TAB PROVIDERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _general_tab(self, obj: FoghornObject) -> InspectorTab:
        """General information tab."""
        from datetime import datetime
        
        return InspectorTab(
            name="General",
            icon="ℹ",
            sections=[
                InspectorSection(
                    title="Identity",
                    icon="🔑",
                    fields={
                        "Type": obj.object_type.value.replace("_", " ").title(),
                        "ID": obj.id,
                        "Hash": obj.hash[:32] + "...",
                    }
                ),
                InspectorSection(
                    title="Timestamps",
                    icon="🕐",
                    fields={
                        "Created": datetime.fromtimestamp(obj.created_at / 1000).strftime("%Y-%m-%d %H:%M:%S"),
                    }
                ),
                InspectorSection(
                    title="Status",
                    icon="✓",
                    fields={
                        "Verified": "✓ Yes" if obj.verified else "✗ No",
                    }
                ),
            ]
        )
    
    def _attributes_tab(self, obj: FoghornObject) -> InspectorTab:
        """Object-specific attributes tab."""
        inspector_data = obj.get_inspector_data()
        
        sections = []
        for section_name, fields in inspector_data.items():
            if section_name in ("general", "metadata"):
                continue  # Skip, handled elsewhere
            
            if isinstance(fields, dict) and fields:
                sections.append(InspectorSection(
                    title=section_name.replace("_", " ").title(),
                    fields=fields,
                ))
        
        # Metadata section
        if obj.metadata:
            sections.append(InspectorSection(
                title="Metadata",
                icon="📋",
                fields=obj.metadata,
                collapsed=True,
            ))
        
        return InspectorTab(
            name="Attributes",
            icon="📝",
            sections=sections,
        ) if sections else None
    
    def _chain_tab(self, obj: FoghornObject) -> InspectorTab:
        """Hash chain / provenance tab."""
        store = get_object_store()
        chain = store.get_chain(obj.hash)
        
        chain_info = []
        for i, item in enumerate(chain[:5]):  # Limit to 5
            chain_info.append(f"{i+1}. {item.object_type.value}: {item.id}")
        
        return InspectorTab(
            name="Chain",
            icon="⛓",
            sections=[
                InspectorSection(
                    title="Provenance",
                    icon="📜",
                    fields={
                        "Chain Length": len(chain),
                        "Previous": obj.prev_hash[:16] + "..." if obj.prev_hash else "genesis",
                        "Chain Valid": "✓" if store.verify_chain(obj.hash) else "✗",
                    }
                ),
                InspectorSection(
                    title="History",
                    icon="📚",
                    fields={f"Step {i+1}": info for i, info in enumerate(chain_info)},
                    collapsed=True,
                ) if chain_info else None,
            ]
        )
    
    def _services_tab(self, obj: FoghornObject) -> InspectorTab:
        """Available services tab."""
        registry = get_service_registry()
        services = registry.find_for_object(obj)
        
        by_category = {}
        for svc in services:
            cat = svc.category.value.title()
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(svc.name)
        
        sections = []
        for cat, names in by_category.items():
            sections.append(InspectorSection(
                title=cat,
                fields={name: "→" for name in names},
            ))
        
        return InspectorTab(
            name="Services",
            icon="⚡",
            sections=sections,
        ) if sections else None
    
    def _bezier_tab(self, obj: LinkCurve) -> InspectorTab:
        """Bézier curve data tab (for LinkCurve objects)."""
        return InspectorTab(
            name="Bézier",
            icon="〰",
            sections=[
                InspectorSection(
                    title="Control Points",
                    icon="📍",
                    fields={
                        "P₀ (source)": f"({obj.p0[0]:.3f}, {obj.p0[1]:.3f})",
                        "H₁ (handle 1)": f"({obj.h1[0]:.3f}, {obj.h1[1]:.3f})",
                        "H₂ (handle 2)": f"({obj.h2[0]:.3f}, {obj.h2[1]:.3f})",
                        "P₃ (target)": f"({obj.p3[0]:.3f}, {obj.p3[1]:.3f})",
                    }
                ),
                InspectorSection(
                    title="Curve Properties",
                    icon="📐",
                    fields={
                        "Curvature": f"{obj.get_curvature():.4f}",
                        "Weight": f"{obj.weight:.2f}",
                        "Relationship": obj.relationship,
                    }
                ),
            ]
        )
    
    def _verification_tab(self, obj: Card) -> InspectorTab:
        """Verification status tab (for Cards)."""
        return InspectorTab(
            name="Verification",
            icon="✓",
            sections=[
                InspectorSection(
                    title="Status",
                    fields={
                        "Verified": "✓ Yes" if obj.verified else "✗ No",
                        "Content Hash": obj.hash[:16] + "...",
                    }
                ),
                InspectorSection(
                    title="Meta Newton",
                    fields={
                        "Constraint Check": "Pending" if not obj.verified else "Passed",
                    },
                    collapsed=True,
                ),
            ]
        )
    
    def _sources_tab(self, obj: ResultSet) -> InspectorTab:
        """Sources/grounding tab (for ResultSets)."""
        sources = []
        for i, result in enumerate(obj.results[:5]):
            source = result.get("source", "Unknown")
            sources.append(f"{i+1}. {source}")
        
        return InspectorTab(
            name="Sources",
            icon="📚",
            sections=[
                InspectorSection(
                    title="Grounding",
                    fields={
                        "Sources Checked": obj.sources_checked,
                        "Results Found": len(obj.results),
                        "Query": obj.query_hash[:16] + "...",
                    }
                ),
                InspectorSection(
                    title="Source List",
                    fields={f"Source {i+1}": s for i, s in enumerate(sources)},
                    collapsed=True,
                ) if sources else None,
            ]
        )
    
    def _get_quick_actions(self, obj: FoghornObject) -> List[Dict[str, str]]:
        """Get quick actions for an object."""
        actions = [
            {"name": "Copy Hash", "icon": "📋"},
            {"name": "Copy JSON", "icon": "{}"},
        ]
        
        # Add verification if not verified
        if not obj.verified:
            actions.append({"name": "Verify", "icon": "✓"})
        
        # Add type-specific actions
        if obj.object_type == ObjectType.CARD:
            actions.append({"name": "Create Link", "icon": "🔗"})
        
        if obj.object_type == ObjectType.QUERY:
            actions.append({"name": "Execute", "icon": "▶"})
        
        return actions


# Global inspector instance
_inspector: Optional[Inspector] = None

def get_inspector() -> Inspector:
    """Get the global inspector instance."""
    global _inspector
    if _inspector is None:
        _inspector = Inspector()
    return _inspector


def inspect(obj: FoghornObject) -> InspectorData:
    """Inspect an object using the global inspector."""
    return get_inspector().inspect(obj)


def inspect_by_hash(hash: str) -> InspectorData:
    """Inspect an object by hash."""
    store = get_object_store()
    obj = store.get(hash)
    
    if not obj:
        return InspectorData()
    
    return get_inspector().inspect(obj)
