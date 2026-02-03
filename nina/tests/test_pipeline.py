#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
PIPELINE TESTS
Test coverage for Paper Section 10.3
═══════════════════════════════════════════════════════════════════════════════
"""

import pytest
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from developer.forge.pipeline import (
    Pipeline, PipelineResult, PipelineStage, PipelineTrace,
    ExecutionBounds, BoundsReport, ProvenanceEntry,
    QueryShape, ParsedQuery
)
from developer.forge.regime import Regime, RegimeType
from developer.forge.trust import TrustLabel


class TestExecutionBounds:
    """Test execution bounds configuration."""
    
    def test_default_bounds(self):
        """Test default bounds values."""
        bounds = ExecutionBounds()
        
        assert bounds.max_iterations == 10000
        assert bounds.max_recursion_depth == 100
        assert bounds.max_operations == 1000000
        assert bounds.timeout_seconds == 30.0
    
    def test_bounds_hard_caps(self):
        """Test that bounds are hard-capped."""
        # Try to set unreasonably high values
        bounds = ExecutionBounds(
            max_iterations=999999999,
            max_recursion_depth=99999,
            max_operations=999999999999
        )
        
        # Should be capped
        assert bounds.max_iterations <= 1000000
        assert bounds.max_recursion_depth <= 1000


class TestPipelineTrace:
    """Test pipeline trace recording."""
    
    def test_add_stage(self):
        """Test adding stage to trace."""
        trace = PipelineTrace()
        
        trace.add(PipelineStage.PARSE, "OK", {"shape": "calculate"})
        
        stages = trace.to_list()
        assert len(stages) == 1
        assert stages[0]["name"] == "PARSE"
        assert stages[0]["status"] == "OK"
    
    def test_trace_records_order(self):
        """Test that trace records stages in order."""
        trace = PipelineTrace()
        
        trace.add(PipelineStage.INTENT_LOCK, "OK")
        trace.add(PipelineStage.PARSE, "OK")
        trace.add(PipelineStage.EXECUTE, "OK")
        
        stages = trace.to_list()
        assert stages[0]["name"] == "INTENT_LOCK"
        assert stages[1]["name"] == "PARSE"
        assert stages[2]["name"] == "EXECUTE"


class TestQueryParsing:
    """Test query parsing into typed shapes."""
    
    def test_parse_capital_query(self):
        """Test parsing capital-of query."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("What is the capital of France?")
        
        assert result.success
        assert result.value == "Paris"
    
    def test_parse_population_query(self):
        """Test parsing population-of query."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("What is the population of Germany?")
        
        assert result.success
        assert result.value == 83240000
    
    def test_parse_calculate_query(self):
        """Test parsing calculation query."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("Calculate 2 + 3 * 4")
        
        assert result.success
        assert result.value == 14  # 2 + (3 * 4)
    
    def test_parse_unknown_query(self):
        """Test parsing unknown query shape."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("Something completely unknown")
        
        # Should still succeed but with lower trust
        assert result.success or result.trust_label == TrustLabel.UNTRUSTED


class TestPipelineStages:
    """Test individual pipeline stages."""
    
    def test_all_stages_recorded(self):
        """Test that all 9 stages are recorded in trace."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("What is the capital of France?")
        
        stages = result.trace.to_list()
        stage_names = [s["name"] for s in stages]
        
        # All 9 stages should be present
        expected = [
            "INTENT_LOCK", "PARSE", "ABSTRACT_INTERPRET", "GEOMETRIC_CHECK",
            "VERIFY_UPGRADE", "EXECUTE", "LOG_PROVENANCE", "META_CHECK", "RETURN"
        ]
        assert stage_names == expected
    
    def test_intent_lock_uses_regime(self):
        """Test that intent lock stage uses the regime."""
        regime = Regime.from_type(RegimeType.MATHEMATICAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("Calculate 1 + 1")
        
        # Find intent lock stage
        intent_stage = next(s for s in result.trace.to_list() if s["name"] == "INTENT_LOCK")
        assert intent_stage["details"]["type"] == "mathematical"


class TestTrustLabeling:
    """Test trust label assignment."""
    
    def test_knowledge_base_is_trusted(self):
        """Test that knowledge base answers are trusted."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("What is the capital of France?")
        
        assert result.trust_label == TrustLabel.TRUSTED
    
    def test_computation_is_trusted(self):
        """Test that verified computation is trusted."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("Calculate 2 + 2")
        
        assert result.trust_label == TrustLabel.TRUSTED


class TestBoundsReporting:
    """Test bounds reporting."""
    
    def test_bounds_report_populated(self):
        """Test that bounds report is populated."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("Calculate 1 + 1")
        
        assert result.bounds_report.operations_count > 0
        assert result.bounds_report.time_elapsed_ms >= 0
        assert result.bounds_report.within_bounds
    
    def test_bounds_report_dict(self):
        """Test bounds report serialization."""
        report = BoundsReport(
            iterations_used=100,
            operations_count=500,
            time_elapsed_ms=12.5,
            within_bounds=True
        )
        
        d = report.to_dict()
        assert d["iterations"] == 100
        assert d["operations"] == 500
        assert d["time_ms"] == 12.5


class TestProvenanceLedger:
    """Test provenance ledger functionality."""
    
    def test_ledger_entry_created(self):
        """Test that ledger entry is created."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("What is the capital of France?")
        
        assert result.ledger_proof is not None
        assert len(result.ledger_proof.entry_hash) == 64  # SHA256
    
    def test_ledger_is_hash_chained(self):
        """Test that ledger entries are hash-chained."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        # Make multiple queries
        result1 = pipeline.process("What is the capital of France?")
        result2 = pipeline.process("What is the capital of Germany?")
        
        ledger = pipeline.get_ledger()
        assert len(ledger) >= 2
        
        # Second entry should reference first entry's hash
        assert ledger[1]["prev_hash"] == ledger[0]["hash"][:16]
    
    def test_provenance_entry_dict(self):
        """Test provenance entry serialization."""
        entry = ProvenanceEntry(
            index=0,
            timestamp="2026-02-03T12:00:00",
            operation="query",
            input_hash="abc123",
            output_hash="def456",
            prev_hash="000000",
            entry_hash="xyz789"
        )
        
        d = entry.to_dict()
        assert d["index"] == 0
        assert d["operation"] == "query"
        assert d["hash"] == "xyz789"


class TestPipelineResult:
    """Test PipelineResult structure."""
    
    def test_success_flag(self):
        """Test success flag based on error."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("What is the capital of France?")
        assert result.success
        assert result.error is None
    
    def test_result_to_dict(self):
        """Test result serialization."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("Calculate 2 + 2")
        d = result.to_dict()
        
        assert "value" in d
        assert "trace" in d
        assert "trust_label" in d
        assert "bounds_report" in d
        assert "ledger_proof" in d
        assert "success" in d


class TestErrorHandling:
    """Test pipeline error handling."""
    
    def test_invalid_calculation(self):
        """Test handling invalid calculation."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("Calculate abc + xyz")
        
        # Should handle gracefully
        assert result is not None
        # Value might be None or error result
    
    def test_not_found_query(self):
        """Test handling query with no answer."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("What is the capital of Narnia?")
        
        # Should handle gracefully with None value
        assert result is not None


class TestFactVerification:
    """Test fact verification functionality."""
    
    def test_verify_true_fact(self):
        """Test verifying a true fact."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("Verify: Paris is the capital of France")
        
        assert result.success
        assert result.value == True
    
    def test_verify_math_fact(self):
        """Test verifying a mathematical fact."""
        regime = Regime.from_type(RegimeType.FACTUAL)
        pipeline = Pipeline(regime)
        
        result = pipeline.process("Verify: 2 + 2 = 4")
        
        assert result.success
        assert result.value == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
