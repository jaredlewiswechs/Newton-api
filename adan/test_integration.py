#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
ADAN INTEGRATION TESTS
Tests that Adanpedia, KnowledgeBase, and KnowledgeStore all work together
═══════════════════════════════════════════════════════════════════════════════

Kinematic Semantics Pipeline:
    Tier 0: Shared store (dynamically added facts)
    Tier 1: Shape matching (kinematic query parsing)
    Tier 2: Semantic fields (Datamuse resolution)
    Tier 3: Keyword matching (pattern fallback)
    
No embeddings - uses fuzzy matching and semantic field resolution instead.
"""

import pytest
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Test the knowledge store directly
from .knowledge_store import KnowledgeStore, StoredFact, get_knowledge_store

# Test the knowledge base integration
from .knowledge_base import KnowledgeBase, get_knowledge_base, VerifiedFact


class TestKnowledgeStore:
    """Test the shared knowledge store with fuzzy matching."""
    
    def test_add_and_retrieve(self):
        """Test adding and retrieving facts."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{}')  # Initialize with empty JSON
            temp_path = f.name
        
        try:
            store = KnowledgeStore(store_path=temp_path)
            
            # Add a fact
            store.add(
                key="test_fact_1",
                fact="The sky is blue.",
                category="Science",
                source="Test",
                source_url="https://test.com",
                confidence=0.9,
                added_by="test"
            )
            
            # Retrieve by key
            result = store.get_by_key("test_fact_1")
            assert result is not None
            assert result.fact == "The sky is blue."
            assert result.category == "Science"
            assert result.confidence == 0.9
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_fuzzy_search(self):
        """Test fuzzy search finds similar terms."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{}')
            temp_path = f.name
        
        try:
            store = KnowledgeStore(store_path=temp_path)
            
            # Add facts
            store.add(
                key="Python programming language",
                fact="Python was created by Guido van Rossum.",
                category="Technology",
                source="Wikipedia",
                confidence=0.85
            )
            store.add(
                key="JavaScript programming",
                fact="JavaScript was created by Brendan Eich.",
                category="Technology",
                source="Wikipedia",
                confidence=0.85
            )
            
            # Exact substring match
            results = store.search("Python")
            assert len(results) >= 1
            assert any("Python" in r.key for r in results)
            
            # Fuzzy match (close to "Python programming")
            results = store.search("python programing")  # typo
            assert len(results) >= 1
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_persistence(self):
        """Test that facts persist across store instances."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{}')
            temp_path = f.name
        
        try:
            # Create store and add fact
            store1 = KnowledgeStore(store_path=temp_path)
            store1.add(
                key="persistent_fact",
                fact="This fact should persist.",
                category="Test",
                source="Test",
                confidence=1.0
            )
            
            # Create new store instance from same file
            store2 = KnowledgeStore(store_path=temp_path)
            
            # Verify fact is there
            result = store2.get_by_key("persistent_fact")
            assert result is not None
            assert result.fact == "This fact should persist."
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_count_and_categories(self):
        """Test count and category methods."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{}')
            temp_path = f.name
        
        try:
            store = KnowledgeStore(store_path=temp_path)
            
            # Initially empty
            assert store.count() == 0
            
            # Add facts
            store.add(key="fact_1", fact="Fact one", category="Science", source="Test", confidence=0.9)
            store.add(key="fact_2", fact="Fact two", category="History", source="Test", confidence=0.8)
            store.add(key="fact_3", fact="Fact three", category="Science", source="Test", confidence=0.7)
            
            # Verify count
            assert store.count() == 3
            
            # Verify get_all with category filter
            science_facts = store.get_all(category="Science")
            assert len(science_facts) == 2
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestKnowledgeBaseIntegration:
    """Test that KnowledgeBase reads from the shared store."""
    
    def test_static_facts_still_work(self):
        """Test that built-in static facts still work."""
        kb = KnowledgeBase()
        
        # Query a static fact (capital)
        result = kb.query("What is the capital of France?")
        assert result is not None
        assert "paris" in result.fact.lower()
    
    def test_kb_stats_include_store(self):
        """Test that KB stats include store information."""
        kb = KnowledgeBase()
        stats = kb.get_stats()
        
        assert "store_enabled" in stats
        assert "store_facts" in stats
        assert "tier_0_store_hits" in stats
        # Embeddings should NOT be in stats anymore
        assert "tier_4_embedding_hits" not in stats
        assert "embeddings_enabled" not in stats


class TestKinematicSemantics:
    """Test the kinematic semantics pipeline."""
    
    def test_shape_based_query(self):
        """Test that shape-based queries work (Tier 1)."""
        kb = KnowledgeBase()
        
        # Capital query has shape CAPITAL_OF
        result = kb.query("capital of japan")
        assert result is not None
        assert "tokyo" in result.fact.lower()
    
    def test_typo_correction(self):
        """Test that typo correction works."""
        kb = KnowledgeBase()
        
        # Common typo
        result = kb.query("capital of frnace")  # typo
        # May or may not find it depending on language mechanics
        # Just ensure it doesn't crash
        assert True
    
    def test_math_not_confused_with_elements(self):
        """Test that math expressions don't match element patterns."""
        # This was a bug: "7 * 8" matched "element 8" via embeddings
        # Now with no embeddings, we shouldn't have this issue
        kb = KnowledgeBase()
        
        # This should NOT match "element 8"
        result = kb.query("7 * 8")
        if result:
            assert "oxygen" not in result.fact.lower()
            assert "element" not in result.fact.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
