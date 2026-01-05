#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
TESTS FOR NEWTON TYPED DICTIONARY

"A dictionary gives you labels.
 A thesaurus gives you relations.
 Math turns them into constraints.
 Only then do you get code."

These tests verify:
1. Words can be typed (Action, State, Invariant, etc.)
2. Relations exist with distance, not equality
3. Antonyms become hard constraints
4. Concepts compile to CDL constraints
5. The word→type→predicate→constraint pipeline works

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import pytest
from core.typed_dictionary import (
    TypedDictionary,
    TypedConcept,
    SemanticRelation,
    SemanticType,
    ConstraintRole,
    RelationType,
    ConstraintCompiler,
    create_financial_dictionary,
    create_safety_dictionary,
)


# ═══════════════════════════════════════════════════════════════════════════════
# TYPED CONCEPT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTypedConcept:
    """Test that words become typed concepts."""

    def test_create_typed_concept(self):
        """Words can be given computational types."""
        concept = TypedConcept(
            word="overdraw",
            lemma="overdraw",
            semantic_type=SemanticType.ACTION,
            constraint_role=ConstraintRole.FORBIDDEN,
            domain="financial",
        )

        assert concept.word == "overdraw"
        assert concept.semantic_type == SemanticType.ACTION
        assert concept.constraint_role == ConstraintRole.FORBIDDEN

    def test_concept_has_unique_id(self):
        """Each typed concept has a unique ID."""
        concept1 = TypedConcept(
            word="overdraw",
            lemma="overdraw",
            semantic_type=SemanticType.ACTION,
            constraint_role=ConstraintRole.FORBIDDEN,
        )
        concept2 = TypedConcept(
            word="overdraft",
            lemma="overdraft",
            semantic_type=SemanticType.STATE,
            constraint_role=ConstraintRole.FORBIDDEN,
        )

        assert concept1.id != concept2.id
        assert concept1.id.startswith("TC_")

    def test_concept_with_predicate_template(self):
        """Concepts can have predicate templates that bind to constraints."""
        concept = TypedConcept(
            word="overdraw",
            lemma="overdraw",
            semantic_type=SemanticType.ACTION,
            constraint_role=ConstraintRole.FORBIDDEN,
            predicate_template="{withdrawal} / {balance} > 1.0",
            default_field="withdrawal",
            default_reference="balance",
        )

        # Predicate with defaults
        predicate = concept.to_predicate()
        assert predicate == "withdrawal / balance > 1.0"

        # Predicate with custom bindings
        predicate = concept.to_predicate(withdrawal="amount", balance="available")
        assert predicate == "amount / available > 1.0"

    def test_same_word_different_types_different_concepts(self):
        """The same word with different types is a different concept."""
        action = TypedConcept(
            word="limit",
            lemma="limit",
            semantic_type=SemanticType.ACTION,
            constraint_role=ConstraintRole.CONDITIONAL,
        )
        boundary = TypedConcept(
            word="limit",
            lemma="limit",
            semantic_type=SemanticType.BOUNDARY,
            constraint_role=ConstraintRole.REQUIRED,
        )

        # Same word, different computational meaning
        assert action.id != boundary.id


# ═══════════════════════════════════════════════════════════════════════════════
# SEMANTIC RELATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestSemanticRelation:
    """Test that relations have distance, not equality."""

    def test_synonym_has_distance(self):
        """Synonyms are related but NOT equal - they have distance."""
        safe = TypedConcept(
            word="safe",
            lemma="safe",
            semantic_type=SemanticType.INVARIANT,
            constraint_role=ConstraintRole.REQUIRED,
        )
        allowed = TypedConcept(
            word="allowed",
            lemma="allowed",
            semantic_type=SemanticType.CONDITION,
            constraint_role=ConstraintRole.CONDITIONAL,
        )

        relation = SemanticRelation(
            source=safe,
            target=allowed,
            relation_type=RelationType.SYNONYM,
            distance=0.4,  # Related but distinct
            symmetric=False,
        )

        assert relation.relation_type == RelationType.SYNONYM
        assert relation.distance == 0.4
        # NOT equal - they have different computational meanings
        assert safe.semantic_type != allowed.semantic_type

    def test_antonym_becomes_hard_constraint(self):
        """Antonyms compile to hard constraints (cannot both be true)."""
        solvent = TypedConcept(
            word="solvent",
            lemma="solvent",
            semantic_type=SemanticType.STATE,
            constraint_role=ConstraintRole.REQUIRED,
        )
        insolvent = TypedConcept(
            word="insolvent",
            lemma="insolvent",
            semantic_type=SemanticType.STATE,
            constraint_role=ConstraintRole.FORBIDDEN,
        )

        relation = SemanticRelation(
            source=solvent,
            target=insolvent,
            relation_type=RelationType.ANTONYM,
            distance=1.0,  # Maximum distance
            symmetric=True,
        )

        # Antonyms should compile to constraints
        constraint = relation.to_constraint()
        assert constraint is not None
        assert constraint["logic"] == "not"
        assert "cannot both be true" in constraint["message"]

    def test_implies_relation(self):
        """IMPLIES relation creates conditional constraint."""
        overdraw = TypedConcept(
            word="overdraw",
            lemma="overdraw",
            semantic_type=SemanticType.ACTION,
            constraint_role=ConstraintRole.FORBIDDEN,
        )
        overdraft = TypedConcept(
            word="overdraft",
            lemma="overdraft",
            semantic_type=SemanticType.STATE,
            constraint_role=ConstraintRole.FORBIDDEN,
        )

        relation = SemanticRelation(
            source=overdraw,
            target=overdraft,
            relation_type=RelationType.IMPLIES,
            implication="overdraw → overdraft",
        )

        constraint = relation.to_constraint()
        assert constraint is not None
        assert "if" in constraint
        assert "then" in constraint


# ═══════════════════════════════════════════════════════════════════════════════
# TYPED DICTIONARY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTypedDictionary:
    """Test the complete typed dictionary."""

    def test_define_and_lookup(self):
        """Words can be defined and looked up."""
        td = TypedDictionary(domain="test")

        concept = td.define(
            "overdraw",
            semantic_type=SemanticType.ACTION,
            constraint_role=ConstraintRole.FORBIDDEN,
        )

        retrieved = td.get("overdraw")
        assert retrieved is not None
        assert retrieved.word == "overdraw"
        assert retrieved == concept

    def test_case_insensitive_lookup(self):
        """Lookup is case-insensitive."""
        td = TypedDictionary()
        td.define("Overdraw", SemanticType.ACTION, ConstraintRole.FORBIDDEN)

        assert td.get("overdraw") is not None
        assert td.get("OVERDRAW") is not None
        assert td.get("OverDraw") is not None

    def test_define_relation(self):
        """Relations can be defined between concepts."""
        td = TypedDictionary()

        td.define("safe", SemanticType.INVARIANT, ConstraintRole.REQUIRED)
        td.define("allowed", SemanticType.CONDITION, ConstraintRole.CONDITIONAL)

        relation = td.relate(
            "safe", "allowed",
            relation_type=RelationType.SYNONYM,
            distance=0.4,
        )

        assert relation is not None
        assert relation.distance == 0.4

    def test_synonyms_with_distance(self):
        """Synonyms are tracked with distance information."""
        td = TypedDictionary()

        td.define("safe", SemanticType.INVARIANT, ConstraintRole.REQUIRED)
        td.define("allowed", SemanticType.CONDITION, ConstraintRole.CONDITIONAL)

        td.relate("safe", "allowed", RelationType.SYNONYM, distance=0.4, symmetric=True)

        assert "allowed" in td.synonyms("safe")
        assert "safe" in td.synonyms("allowed")

    def test_antonyms_tracked(self):
        """Antonyms are tracked separately."""
        td = TypedDictionary()

        td.define("safe", SemanticType.INVARIANT, ConstraintRole.REQUIRED)
        td.define("dangerous", SemanticType.STATE, ConstraintRole.FORBIDDEN)

        td.relate("safe", "dangerous", RelationType.ANTONYM, symmetric=True)

        assert "dangerous" in td.antonyms("safe")
        assert "safe" in td.antonyms("dangerous")

    def test_by_type_index(self):
        """Can query words by semantic type."""
        td = TypedDictionary()

        td.define("overdraw", SemanticType.ACTION, ConstraintRole.FORBIDDEN)
        td.define("withdraw", SemanticType.ACTION, ConstraintRole.CONDITIONAL)
        td.define("overdraft", SemanticType.STATE, ConstraintRole.FORBIDDEN)

        actions = td.by_type(SemanticType.ACTION)
        states = td.by_type(SemanticType.STATE)

        assert "overdraw" in actions
        assert "withdraw" in actions
        assert "overdraft" in states
        assert "overdraft" not in actions

    def test_by_role_index(self):
        """Can query words by constraint role."""
        td = TypedDictionary()

        td.define("overdraw", SemanticType.ACTION, ConstraintRole.FORBIDDEN)
        td.define("withdraw", SemanticType.ACTION, ConstraintRole.CONDITIONAL)
        td.define("solvent", SemanticType.STATE, ConstraintRole.REQUIRED)

        forbidden = td.by_role(ConstraintRole.FORBIDDEN)
        required = td.by_role(ConstraintRole.REQUIRED)

        assert "overdraw" in forbidden
        assert "solvent" in required


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT COMPILATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstraintCompilation:
    """Test the word → constraint compilation pipeline."""

    def test_compile_forbidden_action_to_ratio(self):
        """Forbidden actions compile to ratio constraints."""
        td = TypedDictionary()

        td.define(
            "overdraw",
            semantic_type=SemanticType.ACTION,
            constraint_role=ConstraintRole.FORBIDDEN,
            predicate="{withdrawal} / {balance} > 1.0",
            field="withdrawal",
            reference="balance",
            threshold=1.0,
        )

        constraint = td.compile("overdraw")

        assert constraint["type"] == "ratio"
        assert constraint["f_field"] == "withdrawal"
        assert constraint["g_field"] == "balance"
        assert constraint["operator"] == "ratio_le"
        assert constraint["threshold"] == 1.0

    def test_compile_forbidden_state(self):
        """Forbidden states compile to atomic constraints."""
        td = TypedDictionary()

        td.define(
            "overdraft",
            semantic_type=SemanticType.STATE,
            constraint_role=ConstraintRole.FORBIDDEN,
            field="is_overdraft",
        )

        constraint = td.compile("overdraft")

        assert constraint["type"] == "atomic"
        assert constraint["operator"] == "ne"
        assert constraint["value"] is True

    def test_compile_required_state(self):
        """Required states compile to existence constraints."""
        td = TypedDictionary()

        td.define(
            "authentication",
            semantic_type=SemanticType.STATE,
            constraint_role=ConstraintRole.REQUIRED,
            field="auth_token",
        )

        constraint = td.compile("authentication")

        assert constraint["type"] == "atomic"
        assert constraint["operator"] == "exists"

    def test_compile_to_tinytalk(self):
        """Concepts compile to TinyTalk law syntax."""
        td = TypedDictionary()

        td.define(
            "overdraw",
            semantic_type=SemanticType.ACTION,
            constraint_role=ConstraintRole.FORBIDDEN,
            predicate="{withdrawal} / {balance} > 1.0",
            field="withdrawal",
            reference="balance",
            definition="Prevents overdrawing the account",
        )

        tinytalk = td.to_tinytalk("overdraw")

        assert "@law" in tinytalk
        assert "def enforce_overdraw(self):" in tinytalk
        assert "when(" in tinytalk
        assert "finfr" in tinytalk

    def test_export_dictionary(self):
        """Dictionary can be exported as JSON-serializable dict."""
        td = TypedDictionary(domain="test")

        td.define("overdraw", SemanticType.ACTION, ConstraintRole.FORBIDDEN)
        td.define("overdraft", SemanticType.STATE, ConstraintRole.FORBIDDEN)
        td.relate("overdraw", "overdraft", RelationType.CAUSES)

        exported = td.export()

        assert exported["domain"] == "test"
        assert "overdraw" in exported["concepts"]
        assert len(exported["relations"]) == 1
        assert exported["relations"][0]["source"] == "overdraw"
        assert exported["relations"][0]["target"] == "overdraft"


# ═══════════════════════════════════════════════════════════════════════════════
# BUILT-IN DICTIONARY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestBuiltInDictionaries:
    """Test the built-in financial and safety dictionaries."""

    def test_financial_dictionary(self):
        """Financial dictionary has expected concepts."""
        fd = create_financial_dictionary()

        # Check concepts exist
        assert fd.get("overdraw") is not None
        assert fd.get("overdraft") is not None
        assert fd.get("solvent") is not None
        assert fd.get("insolvent") is not None

        # Check types
        assert fd.get("overdraw").semantic_type == SemanticType.ACTION
        assert fd.get("overdraft").semantic_type == SemanticType.STATE

        # Check relations
        assert "insolvent" in fd.antonyms("solvent")
        assert "overdraw" in fd.synonyms("withdraw")

    def test_safety_dictionary_synonym_distances(self):
        """Safety dictionary demonstrates synonyms with distance."""
        sd = create_safety_dictionary()

        # All these are "synonyms" in English but different computationally
        safe = sd.get("safe")
        allowed = sd.get("allowed")
        permitted = sd.get("permitted")

        assert safe is not None
        assert allowed is not None
        assert permitted is not None

        # They have DIFFERENT types (not equal!)
        assert safe.semantic_type == SemanticType.INVARIANT
        assert allowed.semantic_type == SemanticType.CONDITION
        assert permitted.semantic_type == SemanticType.CONDITION

        # They have DIFFERENT roles
        assert safe.constraint_role == ConstraintRole.REQUIRED
        assert allowed.constraint_role == ConstraintRole.CONDITIONAL

        # They are synonyms with distance
        assert "allowed" in sd.synonyms("safe")

    def test_financial_dictionary_compiles(self):
        """Financial dictionary concepts compile to constraints."""
        fd = create_financial_dictionary()

        # Compile overdraw - should be ratio constraint
        overdraw_constraint = fd.compile("overdraw")
        assert overdraw_constraint["type"] == "ratio"
        assert overdraw_constraint["threshold"] == 1.0

        # Compile with relations
        constraints = fd.compile_with_relations("overdraw")
        assert len(constraints) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# THE SYNTHESIS TEST
# ═══════════════════════════════════════════════════════════════════════════════

class TestTheSynthesis:
    """
    Test the complete pipeline:
    Word → Typed Concept → Predicate → Constraint

    "A dictionary gives you labels.
     A thesaurus gives you relations.
     Math turns them into constraints.
     Only then do you get code."
    """

    def test_word_to_constraint_pipeline(self):
        """The complete pipeline from word to executable constraint."""
        # Stage 1: Dictionary gives labels
        td = TypedDictionary(domain="financial")

        # Stage 2: Type the word (add math)
        td.define(
            "overdraw",
            semantic_type=SemanticType.ACTION,
            constraint_role=ConstraintRole.FORBIDDEN,
            predicate="{withdrawal} / {balance} > 1.0",
            field="withdrawal",
            reference="balance",
            threshold=1.0,
            definition="To withdraw more than available balance",
        )

        # Stage 3: Add relations (thesaurus with distance)
        td.define(
            "overdraft",
            semantic_type=SemanticType.STATE,
            constraint_role=ConstraintRole.FORBIDDEN,
            predicate="{balance} < 0",
            field="balance",
        )

        td.relate(
            "overdraw", "overdraft",
            relation_type=RelationType.CAUSES,
            implication="overdraw → overdraft",
        )

        # Stage 4: Compile to constraint (code)
        constraint = td.compile("overdraw")

        # Verify the pipeline worked
        assert constraint["source_word"] == "overdraw"
        assert constraint["type"] == "ratio"
        assert constraint["f_field"] == "withdrawal"
        assert constraint["g_field"] == "balance"
        assert constraint["operator"] == "ratio_le"
        assert constraint["threshold"] == 1.0

        # The word became code
        assert "finfr" in constraint["message"]

    def test_synonyms_not_collapsed(self):
        """
        Synonyms are not collapsed - they maintain distance.

        If you collapse them, you get bugs.
        If you type them, you get guarantees.
        """
        td = TypedDictionary()

        # Define "synonyms"
        td.define("safe", SemanticType.INVARIANT, ConstraintRole.REQUIRED)
        td.define("allowed", SemanticType.CONDITION, ConstraintRole.CONDITIONAL)
        td.define("permitted", SemanticType.CONDITION, ConstraintRole.CONDITIONAL)

        # Relate them WITH DISTANCE
        td.relate("safe", "allowed", RelationType.SYNONYM, distance=0.4)
        td.relate("allowed", "permitted", RelationType.SYNONYM, distance=0.2)

        # They should NOT be equal
        safe = td.get("safe")
        allowed = td.get("allowed")

        # Same synonymy, different types → different computation
        assert safe.semantic_type != allowed.semantic_type
        assert safe.constraint_role != allowed.constraint_role

        # They compile to different constraints
        safe_constraint = td.compile("safe")
        allowed_constraint = td.compile("allowed")

        assert safe_constraint["type"] != allowed_constraint["type"] or \
               safe_constraint.get("operator") != allowed_constraint.get("operator")

    def test_antonyms_become_hard_constraints(self):
        """
        Antonyms become hard constraints.
        If one is true, the other MUST be false.
        """
        td = TypedDictionary()

        td.define("solvent", SemanticType.STATE, ConstraintRole.REQUIRED)
        td.define("insolvent", SemanticType.STATE, ConstraintRole.FORBIDDEN)

        td.relate("solvent", "insolvent", RelationType.ANTONYM, symmetric=True)

        # Get the relation constraints
        constraints = td.compile_with_relations("solvent")

        # Should have constraint preventing both being true
        antonym_constraints = [c for c in constraints if "logic" in c and c.get("logic") == "not"]
        assert len(antonym_constraints) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
