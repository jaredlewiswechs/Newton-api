"""
═══════════════════════════════════════════════════════════════════════════════
 tinytalk_py - tinyTalk for Python
═══════════════════════════════════════════════════════════════════════════════

The "No-First" constraint language. Define what cannot happen.

Usage:
    import sys
    sys.path.insert(0, 'path/to/Newton-api')

    from tinytalk_py import Blueprint, field, law, forge, when, finfr

    class RiskGovernor(Blueprint):
        assets = field(float, default=1000.0)
        liabilities = field(float, default=0.0)

        @law
        def insolvency(self):
            when(self.liabilities > self.assets, finfr)

        @forge
        def execute_trade(self, amount):
            self.liabilities += amount
            return "cleared"

    gov = RiskGovernor()
    gov.execute_trade(500)   # Works: liabilities=500
    gov.execute_trade(600)   # Raises LawViolation
"""

import os as _os
import sys as _sys

# Allow both relative and absolute imports
_dir = _os.path.dirname(_os.path.abspath(__file__))
if _dir not in _sys.path:
    _sys.path.insert(0, _dir)

try:
    # Try relative imports first (when installed as package)
    from .core import (
        Blueprint,
        Law,
        LawResult,
        LawViolation,
        FinClosure,
        field,
        forge,
        law,
        when,
        fin,
        finfr,
        FINFR,
        FIN,
        # f/g Ratio Constraint System
        RatioResult,
        ratio,
        finfr_if_undefined,
    )

    from .matter import (
        Matter,
        Money,
        Mass,
        Distance,
        Temperature,
        Pressure,
        Volume,
        FlowRate,
        Velocity,
        Time,
        Celsius,
        Fahrenheit,
        PSI,
        Meters,
        Kilograms,
        Liters,
    )

    from .engine import (
        KineticEngine,
        Presence,
        Delta,
        motion,
    )

    from .education import (
        # Enums
        Subject,
        GradeLevel,
        CognitiveLevel,
        NESPhase,
        # Data Classes
        TEKSStandard,
        LessonPhase,
        StudentScore,
        # Blueprints
        NESLessonPlan,
        AssessmentAnalyzer,
        # Generators
        LessonPlanGenerator,
        SlideDeckGenerator,
        PLCReportGenerator,
        # Library
        TEKSLibrary,
        get_teks_library,
        # Cartridge
        EducationCartridge,
        get_education_cartridge,
    )

    from .interface_builder import (
        # Enums
        ComponentType,
        InterfaceType,
        LayoutPattern,
        Variant,
        Size,
        # Data Classes
        Component,
        InterfaceSpec,
        Template,
        # Classes
        TemplateLibrary,
        InterfaceBuilder,
        InterfaceBuilderCartridge,
        # Factory
        get_interface_builder,
    )

    from .knowledge import (
        # Enums
        NavigationResult,
        MasteryLevel,
        ContentType,
        # Events and Ledger
        KnowledgeEvent,
        KnowledgeLedger,
        # Content Structure
        ContentItem,
        KnowledgeNode,
        KnowledgeGraph,
        # State and Navigation
        KnowledgeState,
        KnowledgeNavigator,
        # Example Domain
        create_algebra_unit_2,
        create_navigator_for_algebra,
        # Simulations
        simulate_fast_learner,
        simulate_struggling_learner,
    )
except ImportError:
    # Fall back to absolute imports (when running directly)
    from core import (
        Blueprint,
        Law,
        LawResult,
        LawViolation,
        FinClosure,
        field,
        forge,
        law,
        when,
        fin,
        finfr,
        FINFR,
        FIN,
        # f/g Ratio Constraint System
        RatioResult,
        ratio,
        finfr_if_undefined,
    )

    from matter import (
        Matter,
        Money,
        Mass,
        Distance,
        Temperature,
        Pressure,
        Volume,
        FlowRate,
        Velocity,
        Time,
        Celsius,
        Fahrenheit,
        PSI,
        Meters,
        Kilograms,
        Liters,
    )

    from engine import (
        KineticEngine,
        Presence,
        Delta,
        motion,
    )

    from education import (
        # Enums
        Subject,
        GradeLevel,
        CognitiveLevel,
        NESPhase,
        # Data Classes
        TEKSStandard,
        LessonPhase,
        StudentScore,
        # Blueprints
        NESLessonPlan,
        AssessmentAnalyzer,
        # Generators
        LessonPlanGenerator,
        SlideDeckGenerator,
        PLCReportGenerator,
        # Library
        TEKSLibrary,
        get_teks_library,
        # Cartridge
        EducationCartridge,
        get_education_cartridge,
    )

    from interface_builder import (
        # Enums
        ComponentType,
        InterfaceType,
        LayoutPattern,
        Variant,
        Size,
        # Data Classes
        Component,
        InterfaceSpec,
        Template,
        # Classes
        TemplateLibrary,
        InterfaceBuilder,
        InterfaceBuilderCartridge,
        # Factory
        get_interface_builder,
    )

    from knowledge import (
        # Enums
        NavigationResult,
        MasteryLevel,
        ContentType,
        # Events and Ledger
        KnowledgeEvent,
        KnowledgeLedger,
        # Content Structure
        ContentItem,
        KnowledgeNode,
        KnowledgeGraph,
        # State and Navigation
        KnowledgeState,
        KnowledgeNavigator,
        # Example Domain
        create_algebra_unit_2,
        create_navigator_for_algebra,
        # Simulations
        simulate_fast_learner,
        simulate_struggling_learner,
    )

__version__ = "1.0.0"
__all__ = [
    # Core
    "Blueprint",
    "Law",
    "LawResult",
    "LawViolation",
    "FinClosure",
    "field",
    "forge",
    "law",
    "when",
    "fin",
    "finfr",
    "FINFR",
    "FIN",
    # f/g Ratio Constraint System
    "RatioResult",
    "ratio",
    "finfr_if_undefined",
    # Matter types
    "Matter",
    "Money",
    "Mass",
    "Distance",
    "Temperature",
    "Pressure",
    "Volume",
    "FlowRate",
    "Velocity",
    "Time",
    "Celsius",
    "Fahrenheit",
    "PSI",
    "Meters",
    "Kilograms",
    "Liters",
    # Engine
    "KineticEngine",
    "Presence",
    "Delta",
    "motion",
    # Education
    "Subject",
    "GradeLevel",
    "CognitiveLevel",
    "NESPhase",
    "TEKSStandard",
    "LessonPhase",
    "StudentScore",
    "NESLessonPlan",
    "AssessmentAnalyzer",
    "LessonPlanGenerator",
    "SlideDeckGenerator",
    "PLCReportGenerator",
    "TEKSLibrary",
    "get_teks_library",
    "EducationCartridge",
    "get_education_cartridge",
    # Interface Builder
    "ComponentType",
    "InterfaceType",
    "LayoutPattern",
    "Variant",
    "Size",
    "Component",
    "InterfaceSpec",
    "Template",
    "TemplateLibrary",
    "InterfaceBuilder",
    "InterfaceBuilderCartridge",
    "get_interface_builder",
    # Knowledge System
    "NavigationResult",
    "MasteryLevel",
    "ContentType",
    "KnowledgeEvent",
    "KnowledgeLedger",
    "ContentItem",
    "KnowledgeNode",
    "KnowledgeGraph",
    "KnowledgeState",
    "KnowledgeNavigator",
    "create_algebra_unit_2",
    "create_navigator_for_algebra",
    "simulate_fast_learner",
    "simulate_struggling_learner",
]
