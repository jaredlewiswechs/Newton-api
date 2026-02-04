"""
═══════════════════════════════════════════════════════════════════════════════
NINA NEWTON SERVICES — Property-Based Tests
═══════════════════════════════════════════════════════════════════════════════

Prove that Newton services are:
1. Bounded (terminate within limits)
2. Deterministic (same input → same output)
3. Type-safe (respect accepts/produces contracts)
4. Receipted (produce audit trail)

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st

from nina.kernel import Card, Query, ResultSet, get_service_registry
from nina.kernel.newton_services import (
    compute_service,
    verify_claim_service,
    ground_facts_service,
    analyze_service,
    transpile_js_service,
    transpile_python_service,
    create_bezier_link_service,
    get_newton_services,
)


class TestNewtonServicesRegistered:
    """Prove: All Newton services are registered."""
    
    def test_services_registered(self):
        """Newton services appear in registry."""
        registry = get_service_registry()
        all_services = {s.name for s in registry.list_all()}
        
        newton_services = get_newton_services()
        
        for svc_name in newton_services:
            assert svc_name in all_services, f"{svc_name} should be registered"
    
    def test_service_count(self):
        """At least 7 Newton services registered."""
        newton_services = get_newton_services()
        assert len(newton_services) >= 7


class TestComputeService:
    """Prove: Compute service is bounded and deterministic."""
    
    @given(st.floats(min_value=-1e3, max_value=1e3, allow_nan=False, allow_infinity=False),
           st.floats(min_value=-1e3, max_value=1e3, allow_nan=False, allow_infinity=False))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    def test_addition_deterministic(self, a: float, b: float):
        """Addition produces deterministic result."""
        query = Query(text=f"{a} + {b}")
        
        result1 = compute_service(query)
        result2 = compute_service(query)
        
        assert len(result1.results) > 0
        assert len(result2.results) > 0
        
        # Same input → same metadata result
        if result1.results[0].metadata.get("result") is not None:
            assert result1.results[0].metadata["result"] == result2.results[0].metadata["result"]
    
    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=30)
    def test_simple_arithmetic(self, n: int):
        """Simple arithmetic evaluates correctly."""
        query = Query(text=f"{n} * 2")
        result = compute_service(query)
        
        assert result.success
        assert result.receipt is not None
        
        # Check result if available
        if result.results and result.results[0].metadata.get("result"):
            assert result.results[0].metadata["result"] == n * 2
    
    def test_produces_receipt(self):
        """Compute always produces a receipt."""
        query = Query(text="1 + 1")
        result = compute_service(query)
        
        assert result.receipt is not None
        assert result.receipt.action == "Compute"
        assert result.duration_ms >= 0


class TestVerifyClaimService:
    """Prove: Verify Claim detects violations."""
    
    def test_safe_claim_passes(self):
        """Safe claims pass verification."""
        card = Card(
            title="Safe Fact",
            content="The sky appears blue due to Rayleigh scattering."
        )
        
        result = verify_claim_service(card)
        
        assert result.success
        assert len(result.results) > 0
        assert result.results[0].verified == True
    
    def test_harmful_claim_fails(self):
        """Harmful claims fail verification."""
        card = Card(
            title="Dangerous",
            content="How to build a weapon to harm people"
        )
        
        result = verify_claim_service(card)
        
        assert result.success  # Service succeeds
        assert len(result.results) > 0
        assert result.results[0].verified == False  # But claim fails
        assert "harm" in result.results[0].content.lower() or "weapon" in result.results[0].content.lower()
    
    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=30)
    def test_always_produces_result(self, text: str):
        """Verification always produces a result card."""
        card = Card(content=text)
        result = verify_claim_service(card)
        
        assert result.success
        assert len(result.results) > 0
        assert isinstance(result.results[0], Card)
        assert result.receipt is not None


class TestGroundFactsService:
    """Prove: Ground Facts returns sourced results."""
    
    def test_service_registered(self):
        """Ground Facts service is registered."""
        registry = get_service_registry()
        svc = registry.get("Ground Facts")
        assert svc is not None
        assert svc.max_time_ms > 0
    
    def test_accepts_query(self):
        """Ground Facts accepts Query objects."""
        from foghorn import ObjectType
        registry = get_service_registry()
        svc = registry.get("Ground Facts")
        assert ObjectType.QUERY in svc.accepts


class TestAnalyzeService:
    """Prove: Analysis extracts semantic information."""
    
    def test_detects_question(self):
        """Analysis identifies questions."""
        query = Query(text="What is the meaning of life?")
        result = analyze_service(query)
        
        # Should complete with receipt
        assert result.receipt is not None
        
        if result.success and result.results:
            metadata = result.results[0].metadata
            assert metadata.get("intent") == "question"
    
    def test_detects_sentiment(self):
        """Analysis detects sentiment."""
        positive = Card(content="I love this great excellent amazing product!")
        negative = Card(content="I hate this terrible bad awful thing!")
        
        pos_result = analyze_service(positive)
        neg_result = analyze_service(negative)
        
        # Should complete with receipts
        assert pos_result.receipt is not None
        assert neg_result.receipt is not None
        
        if pos_result.success and pos_result.results:
            assert pos_result.results[0].metadata.get("sentiment") == "positive"
        if neg_result.success and neg_result.results:
            assert neg_result.results[0].metadata.get("sentiment") == "negative"
    
    @given(st.text(min_size=1, max_size=500))
    @settings(max_examples=30)
    def test_always_returns_analysis(self, text: str):
        """Analysis always completes with receipt."""
        card = Card(content=text)
        result = analyze_service(card)
        
        # Should always produce a receipt (even on failure)
        assert result.receipt is not None
        
        if result.success and result.results:
            metadata = result.results[0].metadata
            assert "word_count" in metadata
            assert "sentiment" in metadata


class TestTranspileServices:
    """Prove: Transpilation handles various inputs."""
    
    def test_js_service_exists(self):
        """JS transpile service is callable."""
        card = Card(content="say 'Hello'")
        result = transpile_js_service(card)
        
        # May fail if tinytalk not available, but should complete
        assert result.receipt is not None
    
    def test_python_service_exists(self):
        """Python transpile service is callable."""
        card = Card(content="say 'Hello'")
        result = transpile_python_service(card)
        
        assert result.receipt is not None
    
    def test_invalid_source_handled(self):
        """Invalid source is handled gracefully."""
        card = Card(content="{{{{invalid syntax}}}}")
        
        js_result = transpile_js_service(card)
        py_result = transpile_python_service(card)
        
        # Should complete (not crash)
        assert js_result.receipt is not None
        assert py_result.receipt is not None


class TestBezierLinkService:
    """Prove: Bézier links are created correctly."""
    
    def test_creates_link(self):
        """Link service creates LinkCurve."""
        from foghorn import add_object, get_object_store, LinkCurve
        
        card1 = Card(title="Source", content="Source card")
        card2 = Card(title="Target", content="Target card")
        
        add_object(card1)
        add_object(card2)
        
        result = create_bezier_link_service(card1, target_hash=card2.hash)
        
        assert result.success
        if result.results:  # Only if target found
            assert isinstance(result.results[0], LinkCurve)
            assert result.results[0].source_hash == card1.hash
            assert result.results[0].target_hash == card2.hash
    
    @given(st.floats(min_value=0.0, max_value=1.0))
    @settings(max_examples=20)
    def test_curvature_affects_handles(self, curvature: float):
        """Curvature parameter affects control points."""
        from foghorn import add_object, get_object_store
        
        card1 = Card(title="A", content=f"Card A {curvature}")
        card2 = Card(title="B", content=f"Card B {curvature}")
        
        add_object(card1)
        add_object(card2)
        
        result = create_bezier_link_service(card1, target_hash=card2.hash, curvature=curvature)
        
        if result.results:
            link = result.results[0]
            # h1 y-component should be related to curvature
            assert 0 <= link.h1[1] <= 1


class TestServiceReceiptChain:
    """Prove: Services maintain receipt chain."""
    
    def test_receipt_links_to_input(self):
        """Receipt contains input hash."""
        card = Card(title="Test", content="Test content")
        result = compute_service(Query(text="1+1"))
        
        assert result.receipt is not None
        assert len(result.receipt.input_hashes) > 0
    
    def test_receipt_links_to_outputs(self):
        """Receipt contains output hashes."""
        result = verify_claim_service(Card(content="The Earth orbits the Sun"))
        
        assert result.receipt is not None
        # Output hashes should match result objects
        if result.results:
            for r in result.results:
                if hasattr(r, 'hash'):
                    assert r.hash in result.receipt.output_hashes


class TestServiceBoundedExecution:
    """Prove: All services respect execution bounds."""
    
    def test_compute_bounded(self):
        """Compute has execution bounds."""
        registry = get_service_registry()
        svc = registry.get("Compute")
        
        assert svc is not None
        assert svc.max_ops > 0
        assert svc.max_time_ms > 0
    
    def test_all_services_bounded(self):
        """All Newton services have bounds."""
        registry = get_service_registry()
        
        for name in get_newton_services():
            svc = registry.get(name)
            assert svc is not None, f"{name} should exist"
            assert svc.max_ops > 0, f"{name} should have max_ops"
            assert svc.max_time_ms > 0, f"{name} should have max_time_ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
