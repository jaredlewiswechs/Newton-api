#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TYPED DICTIONARY - From Words to Laws

"A dictionary gives you labels.
 A thesaurus gives you relations.
 Math turns them into constraints.
 Only then do you get code."

This module implements the insight that natural language IS almost the code—
but only once you add math, types, and constraints.

The key transformation:

    Word → Typed Concept → Predicate/Relation → Constraint

Example:
    "overdraw" → Action type → withdrawal/balance > 1.0 → finfr constraint
    "overdraft" → State type → balance < 0 → forbidden_state constraint

Synonyms in English (safe, allowed, permitted) are NOT equal computationally:
    - safe       → invariant preserved
    - allowed    → policy permits
    - permitted  → authority grants

They need DISTANCE, not EQUALITY. That distance is math.

═══════════════════════════════════════════════════════════════════════════════

THE SYNTHESIS:

A dictionary/thesaurus gives you:
    - Definitions (natural language)
    - Parts of speech
    - Synonyms (≈ similarity)
    - Antonyms (≈ opposition)

That's already a graph: words as nodes, synonym/antonym edges.

But data ≠ computation.

What's missing: ADMISSIBILITY.

The dictionary tells you "overdraft" and "overdraw" are related.
It does NOT tell you:
    - When one is allowed
    - When one is forbidden
    - Whether one is an action or a state
    - What happens if you cross a boundary

Natural language is descriptive, not normative.
Computation needs norms.

This module provides the missing layer: math + typing.

═══════════════════════════════════════════════════════════════════════════════

"You're not hand-waving. You're describing how language becomes law."

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from enum import Enum, auto
import hashlib
import json


# ═══════════════════════════════════════════════════════════════════════════════
# SEMANTIC TYPES - Words must choose a role
# ═══════════════════════════════════════════════════════════════════════════════

class SemanticType(Enum):
    """
    The fundamental roles a word can play in computation.

    In English, "overdraw" and "overdraft" are related.
    In Newton, one is an ACTION (verb), one is a STATE (noun).

    This distinction is computationally critical:
    - Actions can be forbidden BEFORE they happen
    - States can be detected AFTER they exist
    """
    # Fundamental types
    ACTION = "action"           # A verb - something that happens
    STATE = "state"             # A noun - something that exists
    INVARIANT = "invariant"     # A property that must always hold
    TRANSITION = "transition"   # A change from one state to another

    # Constraint types
    BOUNDARY = "boundary"       # A limit that cannot be crossed
    THRESHOLD = "threshold"     # A value that triggers behavior
    CONDITION = "condition"     # A boolean test

    # Relation types
    PREREQUISITE = "prerequisite"   # Must happen before
    CONSEQUENCE = "consequence"     # Happens after
    EXCLUSION = "exclusion"         # Cannot coexist

    # Entity types
    AGENT = "agent"             # Who does the action
    PATIENT = "patient"         # What receives the action
    RESOURCE = "resource"       # What is consumed/produced


class ConstraintRole(Enum):
    """
    How a typed concept participates in constraint logic.

    The same word might be:
    - FORBIDDEN: balance < 0 must never occur
    - REQUIRED: authentication must exist
    - CONDITIONAL: approval needed if amount > threshold
    """
    FORBIDDEN = "forbidden"     # finfr if this occurs
    REQUIRED = "required"       # finfr if this doesn't occur
    CONDITIONAL = "conditional" # depends on context
    OBSERVABLE = "observable"   # can be measured but not constrained
    DERIVED = "derived"         # computed from other values


# ═══════════════════════════════════════════════════════════════════════════════
# TYPED CONCEPT - A word with mathematical meaning
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TypedConcept:
    """
    A word that has been given a computational type.

    This is the first transformation:
        Word → Typed Concept

    Example:
        word: "overdraw"
        semantic_type: ACTION
        constraint_role: FORBIDDEN
        domain: "financial"

    The word now has mathematical meaning - it's not just a label,
    it's a typed object that can participate in constraint logic.
    """
    # Identity
    word: str                           # The natural language word
    lemma: str                          # Base form (overdraw, not overdrew)

    # Type information
    semantic_type: SemanticType         # What role does this play?
    constraint_role: ConstraintRole     # How does it participate in constraints?

    # Domain binding
    domain: str = "general"             # Which domain does this belong to?

    # Mathematical binding (the key insight)
    predicate_template: Optional[str] = None  # e.g., "{field} / {reference} > 1.0"
    default_field: Optional[str] = None       # e.g., "withdrawal"
    default_reference: Optional[str] = None   # e.g., "balance"
    threshold: Optional[float] = None         # e.g., 1.0

    # Metadata
    definition: Optional[str] = None    # Natural language definition
    examples: Tuple[str, ...] = ()      # Usage examples

    def __hash__(self):
        return hash((self.word, self.lemma, self.semantic_type, self.domain))

    @property
    def id(self) -> str:
        """Unique identifier for this typed concept."""
        data = f"{self.word}:{self.semantic_type.value}:{self.domain}"
        return f"TC_{hashlib.sha256(data.encode()).hexdigest()[:8].upper()}"

    def to_predicate(self, **bindings) -> str:
        """
        Convert to a predicate string with variable bindings.

        Example:
            concept.to_predicate(field="amount", reference="limit")
            → "amount / limit > 1.0"
        """
        if not self.predicate_template:
            return f"{self.word}()"

        template = self.predicate_template
        for key, value in bindings.items():
            template = template.replace(f"{{{key}}}", str(value))

        # Apply defaults
        if self.default_field:
            template = template.replace("{field}", self.default_field)
        if self.default_reference:
            template = template.replace("{reference}", self.default_reference)

        return template


# ═══════════════════════════════════════════════════════════════════════════════
# SEMANTIC RELATIONS - Synonyms need distance, not equality
# ═══════════════════════════════════════════════════════════════════════════════

class RelationType(Enum):
    """
    Types of semantic relations between concepts.

    CRITICAL: In computation, synonyms are NOT equal.
    They are RELATED with a DISTANCE.

    "safe" and "allowed" might be synonyms in English,
    but computationally:
    - safe       → invariant preserved (system property)
    - allowed    → policy permits (authorization)

    Collapsing them creates bugs.
    Typing them creates guarantees.
    """
    # Similarity relations (traditional thesaurus)
    SYNONYM = "synonym"         # Similar meaning, DIFFERENT computation
    ANTONYM = "antonym"         # Opposite meaning → hard constraint
    HYPERNYM = "hypernym"       # More general (vehicle → car)
    HYPONYM = "hyponym"         # More specific (car → vehicle)

    # Constraint relations (Newton-specific)
    IMPLIES = "implies"         # If A then B
    EXCLUDES = "excludes"       # If A then not B
    REQUIRES = "requires"       # A needs B to be valid
    PREVENTS = "prevents"       # A makes B impossible

    # Temporal relations
    PRECEDES = "precedes"       # A happens before B
    FOLLOWS = "follows"         # A happens after B
    CONCURRENT = "concurrent"   # A and B happen together

    # Causal relations
    CAUSES = "causes"           # A leads to B
    ENABLES = "enables"         # A makes B possible
    TRIGGERS = "triggers"       # A immediately causes B


@dataclass(frozen=True)
class SemanticRelation:
    """
    A typed, measured relation between two concepts.

    This is NOT just "these words are related."
    This is "these words are related WITH THIS DISTANCE and THIS CONSTRAINT."

    Example:
        source: "safe"
        target: "allowed"
        relation_type: SYNONYM
        distance: 0.3  # Similar but not identical
        constraint_mapping: {"safe": "invariant", "allowed": "policy"}

    The distance tells you: don't collapse these.
    The mapping tells you: how they differ computationally.
    """
    # The relation
    source: TypedConcept
    target: TypedConcept
    relation_type: RelationType

    # The measure (this is the math)
    distance: float = 0.0       # 0 = identical, 1 = unrelated
    strength: float = 1.0       # How strong is this relation?

    # Constraint implications
    # When source is true, what does it say about target?
    implication: Optional[str] = None  # e.g., "source → ¬target"

    # Bidirectional?
    symmetric: bool = False

    def __hash__(self):
        return hash((self.source.id, self.target.id, self.relation_type))

    @property
    def id(self) -> str:
        """Unique identifier for this relation."""
        data = f"{self.source.id}:{self.target.id}:{self.relation_type.value}"
        return f"SR_{hashlib.sha256(data.encode()).hexdigest()[:8].upper()}"

    def to_constraint(self) -> Optional[Dict[str, Any]]:
        """
        Convert this relation to a CDL constraint.

        Antonyms become hard constraints.
        Implications become conditional constraints.
        """
        if self.relation_type == RelationType.ANTONYM:
            # Antonyms are exclusive: if one is true, other must be false
            return {
                "logic": "not",
                "constraints": [
                    {
                        "logic": "and",
                        "constraints": [
                            {"field": self.source.lemma, "operator": "eq", "value": True},
                            {"field": self.target.lemma, "operator": "eq", "value": True}
                        ]
                    }
                ],
                "message": f"Antonyms {self.source.word} and {self.target.word} cannot both be true"
            }

        elif self.relation_type == RelationType.IMPLIES:
            # If source is true, target must be true
            return {
                "if": {"field": self.source.lemma, "operator": "eq", "value": True},
                "then": {"field": self.target.lemma, "operator": "eq", "value": True},
                "message": f"{self.source.word} implies {self.target.word}"
            }

        elif self.relation_type == RelationType.EXCLUDES:
            # If source is true, target must be false
            return {
                "if": {"field": self.source.lemma, "operator": "eq", "value": True},
                "then": {"field": self.target.lemma, "operator": "eq", "value": False},
                "message": f"{self.source.word} excludes {self.target.word}"
            }

        elif self.relation_type == RelationType.REQUIRES:
            # Source requires target to be present
            return {
                "if": {"field": self.source.lemma, "operator": "eq", "value": True},
                "then": {"field": self.target.lemma, "operator": "exists", "value": True},
                "message": f"{self.source.word} requires {self.target.word}"
            }

        return None


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT COMPILER - Words become laws
# ═══════════════════════════════════════════════════════════════════════════════

class ConstraintCompiler:
    """
    Compiles typed concepts and relations into executable constraints.

    This is the final transformation:
        Typed Concept + Relations → Constraint

    The key insight: once meaning is compiled into admissibility,
    the language IS the program.
    """

    def __init__(self):
        self._concepts: Dict[str, TypedConcept] = {}
        self._relations: Dict[str, SemanticRelation] = {}
        self._compiled: Dict[str, Dict[str, Any]] = {}

    def register_concept(self, concept: TypedConcept) -> None:
        """Register a typed concept."""
        self._concepts[concept.id] = concept

    def register_relation(self, relation: SemanticRelation) -> None:
        """Register a semantic relation."""
        self._relations[relation.id] = relation

        # If symmetric, register reverse
        if relation.symmetric:
            reverse = SemanticRelation(
                source=relation.target,
                target=relation.source,
                relation_type=relation.relation_type,
                distance=relation.distance,
                strength=relation.strength,
                implication=relation.implication,
                symmetric=False  # Don't recurse
            )
            self._relations[reverse.id] = reverse

    def compile_concept(self, concept: TypedConcept) -> Dict[str, Any]:
        """
        Compile a typed concept to a CDL constraint.

        The compilation depends on the semantic type and constraint role.
        """
        # Check cache
        if concept.id in self._compiled:
            return self._compiled[concept.id]

        constraint: Dict[str, Any] = {
            "id": concept.id,
            "source_word": concept.word,
            "domain": concept.domain,
        }

        # Compile based on type and role
        if concept.constraint_role == ConstraintRole.FORBIDDEN:
            # This state/action must never occur
            if concept.semantic_type == SemanticType.ACTION:
                # Forbidden action → ratio constraint (attempt / allowance > 1)
                constraint["type"] = "ratio"
                constraint["f_field"] = concept.default_field or "attempt"
                constraint["g_field"] = concept.default_reference or "allowance"
                constraint["operator"] = "ratio_le"
                constraint["threshold"] = concept.threshold or 1.0
                constraint["message"] = f"finfr: {concept.word} would violate constraint"

            elif concept.semantic_type == SemanticType.STATE:
                # Forbidden state → simple constraint
                constraint["type"] = "atomic"
                constraint["field"] = concept.default_field or concept.lemma
                constraint["operator"] = "ne"
                constraint["value"] = True
                constraint["message"] = f"finfr: forbidden state {concept.word}"

        elif concept.constraint_role == ConstraintRole.REQUIRED:
            # This must exist/happen
            constraint["type"] = "atomic"
            constraint["field"] = concept.default_field or concept.lemma
            constraint["operator"] = "exists"
            constraint["value"] = True
            constraint["message"] = f"Required: {concept.word}"

        elif concept.constraint_role == ConstraintRole.CONDITIONAL:
            # Depends on context - needs additional info
            constraint["type"] = "conditional"
            constraint["field"] = concept.default_field or concept.lemma
            constraint["needs_condition"] = True

        self._compiled[concept.id] = constraint
        return constraint

    def compile_all_relations(self, concept: TypedConcept) -> List[Dict[str, Any]]:
        """
        Compile all relations involving a concept into constraints.

        This is where synonyms become distance and antonyms become hard constraints.
        """
        constraints = []

        for relation in self._relations.values():
            if relation.source.id == concept.id or relation.target.id == concept.id:
                cdl = relation.to_constraint()
                if cdl:
                    constraints.append(cdl)

        return constraints

    def compile_to_tinytalk(self, concept: TypedConcept) -> str:
        """
        Compile a typed concept to TinyTalk law syntax.

        Example output:
            @law
            def no_overdraw(self):
                '''Prevents overdrawing: withdrawal/balance must be <= 1.0'''
                when(self.withdrawal / self.balance > 1.0, finfr)
        """
        lines = ["@law"]
        func_name = f"enforce_{concept.lemma.replace(' ', '_')}"
        lines.append(f"def {func_name}(self):")
        lines.append(f'    """{concept.definition or concept.word}"""')

        if concept.constraint_role == ConstraintRole.FORBIDDEN:
            if concept.predicate_template:
                predicate = concept.to_predicate()
                lines.append(f"    when({predicate}, finfr)")
            else:
                lines.append(f"    when(self.{concept.lemma}, finfr)")

        elif concept.constraint_role == ConstraintRole.REQUIRED:
            lines.append(f"    when(not self.{concept.lemma}, finfr)")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# TYPED DICTIONARY - The complete dictionary with mathematical meaning
# ═══════════════════════════════════════════════════════════════════════════════

class TypedDictionary:
    """
    A dictionary where every word has a computational type.

    This is not a replacement for a natural language dictionary.
    This is a COMPILATION TARGET for natural language.

    The insight:
        - A dictionary gives you labels
        - A thesaurus gives you relations
        - Math turns them into constraints
        - Only then do you get code

    Usage:
        td = TypedDictionary()

        # Define typed concepts
        td.define("overdraw",
            semantic_type=SemanticType.ACTION,
            constraint_role=ConstraintRole.FORBIDDEN,
            predicate="{withdrawal} / {balance} > 1.0")

        td.define("overdraft",
            semantic_type=SemanticType.STATE,
            constraint_role=ConstraintRole.FORBIDDEN,
            predicate="{balance} < 0")

        # Define relations
        td.relate("overdraw", "overdraft",
            relation_type=RelationType.CAUSES,
            implication="overdraw → overdraft")

        # Compile to constraints
        constraints = td.compile("overdraw")
    """

    def __init__(self, domain: str = "general"):
        self.domain = domain
        self._concepts: Dict[str, TypedConcept] = {}
        self._relations: List[SemanticRelation] = []
        self._compiler = ConstraintCompiler()

        # Index structures
        self._by_type: Dict[SemanticType, Set[str]] = {t: set() for t in SemanticType}
        self._by_role: Dict[ConstraintRole, Set[str]] = {r: set() for r in ConstraintRole}
        self._synonyms: Dict[str, Set[str]] = {}
        self._antonyms: Dict[str, Set[str]] = {}

    def define(
        self,
        word: str,
        semantic_type: SemanticType,
        constraint_role: ConstraintRole,
        lemma: Optional[str] = None,
        predicate: Optional[str] = None,
        field: Optional[str] = None,
        reference: Optional[str] = None,
        threshold: Optional[float] = None,
        definition: Optional[str] = None,
        examples: Optional[List[str]] = None,
    ) -> TypedConcept:
        """
        Define a word with its computational type.

        This is where ambiguity is REFUSED.
        The word must choose a role.
        """
        concept = TypedConcept(
            word=word,
            lemma=lemma or word.lower(),
            semantic_type=semantic_type,
            constraint_role=constraint_role,
            domain=self.domain,
            predicate_template=predicate,
            default_field=field,
            default_reference=reference,
            threshold=threshold,
            definition=definition,
            examples=tuple(examples) if examples else ()
        )

        self._concepts[word.lower()] = concept
        self._compiler.register_concept(concept)

        # Update indices
        self._by_type[semantic_type].add(word.lower())
        self._by_role[constraint_role].add(word.lower())

        return concept

    def relate(
        self,
        source_word: str,
        target_word: str,
        relation_type: RelationType,
        distance: float = 0.0,
        strength: float = 1.0,
        implication: Optional[str] = None,
        symmetric: bool = False,
    ) -> SemanticRelation:
        """
        Define a relation between two words.

        CRITICAL: Synonyms get DISTANCE, not EQUALITY.
        """
        source = self._concepts.get(source_word.lower())
        target = self._concepts.get(target_word.lower())

        if not source:
            raise ValueError(f"Source word '{source_word}' not defined")
        if not target:
            raise ValueError(f"Target word '{target_word}' not defined")

        relation = SemanticRelation(
            source=source,
            target=target,
            relation_type=relation_type,
            distance=distance,
            strength=strength,
            implication=implication,
            symmetric=symmetric
        )

        self._relations.append(relation)
        self._compiler.register_relation(relation)

        # Update synonym/antonym indices
        if relation_type == RelationType.SYNONYM:
            if source_word.lower() not in self._synonyms:
                self._synonyms[source_word.lower()] = set()
            self._synonyms[source_word.lower()].add(target_word.lower())
            if symmetric:
                if target_word.lower() not in self._synonyms:
                    self._synonyms[target_word.lower()] = set()
                self._synonyms[target_word.lower()].add(source_word.lower())

        elif relation_type == RelationType.ANTONYM:
            if source_word.lower() not in self._antonyms:
                self._antonyms[source_word.lower()] = set()
            self._antonyms[source_word.lower()].add(target_word.lower())
            if symmetric:
                if target_word.lower() not in self._antonyms:
                    self._antonyms[target_word.lower()] = set()
                self._antonyms[target_word.lower()].add(source_word.lower())

        return relation

    def get(self, word: str) -> Optional[TypedConcept]:
        """Look up a typed concept."""
        return self._concepts.get(word.lower())

    def synonyms(self, word: str) -> Set[str]:
        """
        Get synonyms of a word.

        Remember: these are RELATED but NOT EQUAL.
        Each has a different computational meaning.
        """
        return self._synonyms.get(word.lower(), set())

    def antonyms(self, word: str) -> Set[str]:
        """
        Get antonyms of a word.

        Antonyms become HARD CONSTRAINTS:
        If one is true, the other must be false.
        """
        return self._antonyms.get(word.lower(), set())

    def by_type(self, semantic_type: SemanticType) -> Set[str]:
        """Get all words of a given type."""
        return self._by_type.get(semantic_type, set())

    def by_role(self, constraint_role: ConstraintRole) -> Set[str]:
        """Get all words with a given constraint role."""
        return self._by_role.get(constraint_role, set())

    def compile(self, word: str) -> Dict[str, Any]:
        """
        Compile a word to a CDL constraint.

        This is the final transformation:
        Word → Typed Concept → Constraint
        """
        concept = self.get(word)
        if not concept:
            raise ValueError(f"Word '{word}' not defined in dictionary")

        return self._compiler.compile_concept(concept)

    def compile_with_relations(self, word: str) -> List[Dict[str, Any]]:
        """
        Compile a word and all its relations to constraints.
        """
        concept = self.get(word)
        if not concept:
            raise ValueError(f"Word '{word}' not defined in dictionary")

        constraints = [self._compiler.compile_concept(concept)]
        constraints.extend(self._compiler.compile_all_relations(concept))
        return constraints

    def to_tinytalk(self, word: str) -> str:
        """Compile a word to TinyTalk law syntax."""
        concept = self.get(word)
        if not concept:
            raise ValueError(f"Word '{word}' not defined in dictionary")

        return self._compiler.compile_to_tinytalk(concept)

    def export(self) -> Dict[str, Any]:
        """Export the entire dictionary as JSON-serializable dict."""
        return {
            "domain": self.domain,
            "concepts": {
                word: {
                    "word": c.word,
                    "lemma": c.lemma,
                    "semantic_type": c.semantic_type.value,
                    "constraint_role": c.constraint_role.value,
                    "predicate_template": c.predicate_template,
                    "default_field": c.default_field,
                    "default_reference": c.default_reference,
                    "threshold": c.threshold,
                    "definition": c.definition,
                    "examples": list(c.examples),
                }
                for word, c in self._concepts.items()
            },
            "relations": [
                {
                    "source": r.source.word,
                    "target": r.target.word,
                    "relation_type": r.relation_type.value,
                    "distance": r.distance,
                    "strength": r.strength,
                    "implication": r.implication,
                    "symmetric": r.symmetric,
                }
                for r in self._relations
            ]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# BUILT-IN FINANCIAL DICTIONARY
# ═══════════════════════════════════════════════════════════════════════════════

def create_financial_dictionary() -> TypedDictionary:
    """
    Create a typed dictionary for financial domain.

    This demonstrates the full pipeline:
    - Words become typed concepts
    - Relations become constraints
    - Synonyms have distance, not equality
    - Antonyms become hard constraints
    """
    td = TypedDictionary(domain="financial")

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIONS (things that happen)
    # ─────────────────────────────────────────────────────────────────────────

    td.define(
        "overdraw",
        semantic_type=SemanticType.ACTION,
        constraint_role=ConstraintRole.FORBIDDEN,
        predicate="{withdrawal} / {balance} > 1.0",
        field="withdrawal",
        reference="balance",
        threshold=1.0,
        definition="To withdraw more than the available balance",
        examples=["Attempting to overdraw the account will be rejected"]
    )

    td.define(
        "withdraw",
        semantic_type=SemanticType.ACTION,
        constraint_role=ConstraintRole.CONDITIONAL,
        predicate="{amount} <= {available}",
        field="amount",
        reference="available",
        definition="To remove funds from an account",
        examples=["Withdraw $100 from checking"]
    )

    td.define(
        "deposit",
        semantic_type=SemanticType.ACTION,
        constraint_role=ConstraintRole.OBSERVABLE,
        definition="To add funds to an account",
        examples=["Deposit $500"]
    )

    td.define(
        "transfer",
        semantic_type=SemanticType.ACTION,
        constraint_role=ConstraintRole.CONDITIONAL,
        predicate="{amount} <= {source_balance}",
        field="amount",
        reference="source_balance",
        definition="To move funds between accounts"
    )

    # ─────────────────────────────────────────────────────────────────────────
    # STATES (things that exist)
    # ─────────────────────────────────────────────────────────────────────────

    td.define(
        "overdraft",
        semantic_type=SemanticType.STATE,
        constraint_role=ConstraintRole.FORBIDDEN,
        predicate="{balance} < 0",
        field="balance",
        threshold=0,
        definition="A state where the balance is negative"
    )

    td.define(
        "solvent",
        semantic_type=SemanticType.STATE,
        constraint_role=ConstraintRole.REQUIRED,
        predicate="{assets} >= {liabilities}",
        field="assets",
        reference="liabilities",
        definition="Having assets greater than or equal to liabilities"
    )

    td.define(
        "insolvent",
        semantic_type=SemanticType.STATE,
        constraint_role=ConstraintRole.FORBIDDEN,
        predicate="{liabilities} > {assets}",
        field="liabilities",
        reference="assets",
        definition="Having liabilities greater than assets"
    )

    td.define(
        "liquid",
        semantic_type=SemanticType.STATE,
        constraint_role=ConstraintRole.OBSERVABLE,
        definition="Having sufficient cash or cash equivalents"
    )

    # ─────────────────────────────────────────────────────────────────────────
    # BOUNDARIES (limits)
    # ─────────────────────────────────────────────────────────────────────────

    td.define(
        "limit",
        semantic_type=SemanticType.BOUNDARY,
        constraint_role=ConstraintRole.REQUIRED,
        definition="A maximum value that cannot be exceeded"
    )

    td.define(
        "threshold",
        semantic_type=SemanticType.THRESHOLD,
        constraint_role=ConstraintRole.CONDITIONAL,
        definition="A value that triggers special handling"
    )

    # ─────────────────────────────────────────────────────────────────────────
    # RELATIONS
    # ─────────────────────────────────────────────────────────────────────────

    # Overdraw CAUSES overdraft
    td.relate(
        "overdraw", "overdraft",
        relation_type=RelationType.CAUSES,
        implication="overdraw → overdraft",
        strength=1.0
    )

    # Solvent and insolvent are ANTONYMS (hard constraint)
    td.relate(
        "solvent", "insolvent",
        relation_type=RelationType.ANTONYM,
        distance=1.0,  # Maximum distance - completely opposite
        symmetric=True
    )

    # Withdraw is similar to overdraw but different (synonym with distance)
    td.relate(
        "withdraw", "overdraw",
        relation_type=RelationType.SYNONYM,
        distance=0.3,  # Related but distinct
        symmetric=True
    )

    # Deposit is antonym of withdraw
    td.relate(
        "deposit", "withdraw",
        relation_type=RelationType.ANTONYM,
        distance=1.0,
        symmetric=True
    )

    # Transfer REQUIRES source account to be solvent
    td.relate(
        "transfer", "solvent",
        relation_type=RelationType.REQUIRES,
        implication="transfer → source.solvent"
    )

    return td


# ═══════════════════════════════════════════════════════════════════════════════
# BUILT-IN SAFETY DICTIONARY
# ═══════════════════════════════════════════════════════════════════════════════

def create_safety_dictionary() -> TypedDictionary:
    """
    Create a typed dictionary for safety-related concepts.

    Demonstrates that synonyms in English are NOT equal computationally:
    - safe       → invariant preserved (system property)
    - allowed    → policy permits (authorization)
    - permitted  → authority grants (delegation)
    - acceptable → context-dependent tolerance (soft constraint)
    """
    td = TypedDictionary(domain="safety")

    # ─────────────────────────────────────────────────────────────────────────
    # SAFETY STATES - Each "synonym" has different computational meaning
    # ─────────────────────────────────────────────────────────────────────────

    td.define(
        "safe",
        semantic_type=SemanticType.INVARIANT,
        constraint_role=ConstraintRole.REQUIRED,
        predicate="{risk} <= {tolerance}",
        field="risk",
        reference="tolerance",
        definition="System invariant: risk never exceeds tolerance",
        examples=["The operation is safe if risk/tolerance <= 1"]
    )

    td.define(
        "allowed",
        semantic_type=SemanticType.CONDITION,
        constraint_role=ConstraintRole.CONDITIONAL,
        predicate="{policy}.permits({action})",
        definition="Policy permits this action",
        examples=["This action is allowed by the policy"]
    )

    td.define(
        "permitted",
        semantic_type=SemanticType.CONDITION,
        constraint_role=ConstraintRole.CONDITIONAL,
        predicate="{authority}.grants({action}, {agent})",
        definition="Authority has granted permission",
        examples=["The user is permitted to perform this action"]
    )

    td.define(
        "acceptable",
        semantic_type=SemanticType.THRESHOLD,
        constraint_role=ConstraintRole.OBSERVABLE,  # Soft constraint
        definition="Within context-dependent tolerance",
        examples=["The latency is acceptable for this use case"]
    )

    td.define(
        "dangerous",
        semantic_type=SemanticType.STATE,
        constraint_role=ConstraintRole.FORBIDDEN,
        predicate="{risk} > {safe_threshold}",
        field="risk",
        reference="safe_threshold",
        definition="Risk exceeds safe threshold"
    )

    # ─────────────────────────────────────────────────────────────────────────
    # RELATIONS - These "synonyms" need distance, not equality
    # ─────────────────────────────────────────────────────────────────────────

    # Safe/allowed/permitted are synonyms WITH DISTANCE
    td.relate(
        "safe", "allowed",
        relation_type=RelationType.SYNONYM,
        distance=0.4,  # Related but computationally distinct
        implication="safe → allowed (but not converse)",
        symmetric=False  # safe implies allowed, but allowed doesn't imply safe
    )

    td.relate(
        "allowed", "permitted",
        relation_type=RelationType.SYNONYM,
        distance=0.2,  # Closer than safe/allowed
        symmetric=True
    )

    td.relate(
        "safe", "permitted",
        relation_type=RelationType.SYNONYM,
        distance=0.5,
        symmetric=False
    )

    # Safe and dangerous are ANTONYMS (hard constraint)
    td.relate(
        "safe", "dangerous",
        relation_type=RelationType.ANTONYM,
        distance=1.0,
        symmetric=True
    )

    # Safe REQUIRES allowed
    td.relate(
        "safe", "allowed",
        relation_type=RelationType.REQUIRES,
        implication="safe → allowed"
    )

    return td


# ═══════════════════════════════════════════════════════════════════════════════
# CLI DEMO
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 70)
    print("NEWTON TYPED DICTIONARY - From Words to Laws")
    print("═" * 70)
    print()
    print('"A dictionary gives you labels.')
    print(' A thesaurus gives you relations.')
    print(' Math turns them into constraints.')
    print(' Only then do you get code."')
    print()
    print("═" * 70)

    # Create financial dictionary
    print("\n[1] FINANCIAL DICTIONARY")
    print("-" * 70)

    fin_dict = create_financial_dictionary()

    # Show typed concepts
    print("\nTyped Concepts:")
    for word in ["overdraw", "overdraft", "withdraw", "solvent"]:
        concept = fin_dict.get(word)
        if concept:
            print(f"  {word}:")
            print(f"    Type: {concept.semantic_type.value}")
            print(f"    Role: {concept.constraint_role.value}")
            if concept.predicate_template:
                print(f"    Predicate: {concept.predicate_template}")

    # Show relations
    print("\nRelations:")
    print("  overdraw CAUSES overdraft")
    print("  solvent ANTONYM insolvent (hard constraint: cannot both be true)")
    print("  withdraw SYNONYM overdraw (distance=0.3, NOT equal)")

    # Compile to constraints
    print("\nCompiled Constraints:")
    overdraw_constraint = fin_dict.compile("overdraw")
    print(f"  overdraw → {json.dumps(overdraw_constraint, indent=4)}")

    # Compile to TinyTalk
    print("\nTinyTalk Law:")
    print(fin_dict.to_tinytalk("overdraw"))

    # Create safety dictionary
    print("\n" + "═" * 70)
    print("[2] SAFETY DICTIONARY - Why synonyms need distance, not equality")
    print("-" * 70)

    safety_dict = create_safety_dictionary()

    print("\nIn English, these are 'synonyms':")
    print("  safe, allowed, permitted, acceptable")
    print()
    print("In Newton, they are TYPED and MEASURED:")

    for word in ["safe", "allowed", "permitted", "acceptable"]:
        concept = safety_dict.get(word)
        if concept:
            print(f"\n  {word}:")
            print(f"    Type: {concept.semantic_type.value}")
            print(f"    Role: {concept.constraint_role.value}")
            print(f"    Meaning: {concept.definition}")

    print("\nSynonym DISTANCES (not equality):")
    print("  safe ←→ allowed: distance=0.4")
    print("  allowed ←→ permitted: distance=0.2")
    print("  safe ←→ permitted: distance=0.5")
    print()
    print("If you collapse them, you get BUGS.")
    print("If you type them, you get GUARANTEES.")

    # The synthesis
    print("\n" + "═" * 70)
    print("[3] THE SYNTHESIS")
    print("-" * 70)
    print()
    print("Word")
    print("  ↓")
    print("Typed concept")
    print("  ↓")
    print("Predicate / relation")
    print("  ↓")
    print("Constraint")
    print()
    print("Example:")
    print("  • Word: overdraw")
    print("  • Type: Action")
    print("  • Predicate: withdrawal / balance > 1.0")
    print("  • Constraint: finfr (forbidden)")
    print()
    print("  • Word: overdraft")
    print("  • Type: State")
    print("  • Predicate: balance < 0")
    print("  • Constraint: forbidden_state")
    print()
    print("Same English meaning → two different mathematical objects.")
    print()
    print("═" * 70)
    print('"Once meaning is compiled into admissibility,')
    print(' the language IS the program."')
    print("═" * 70)
