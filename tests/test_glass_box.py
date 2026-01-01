#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
GLASS BOX INTEGRATION TESTS
End-to-end tests for the Glass Box activation.
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import tempfile
import shutil
from core.forge import Forge, ForgeConfig
from core.vault import Vault, VaultConfig
from core.vault_client import VaultClient
from core.policy_engine import PolicyEngine, Policy, PolicyType, PolicyAction
from core.negotiator import Negotiator, RequestPriority
from core.ledger import Ledger, LedgerConfig
from core.merkle_anchor import MerkleAnchorScheduler


class TestGlassBoxIntegration:
    """Integration tests for Glass Box functionality."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def components(self, temp_storage):
        """Set up Glass Box components."""
        vault_config = VaultConfig(storage_path=os.path.join(temp_storage, "vault"))
        vault = Vault(vault_config)
        vault_client = VaultClient(vault)
        
        policy_engine = PolicyEngine()
        negotiator = Negotiator()
        
        ledger_config = LedgerConfig(storage_path=os.path.join(temp_storage, "ledger"))
        ledger = Ledger(ledger_config)
        
        merkle_scheduler = MerkleAnchorScheduler(
            ledger,
            storage_path=os.path.join(temp_storage, "anchors")
        )
        
        forge_config = ForgeConfig(enable_metrics=True)
        forge = Forge(forge_config)
        forge.enable_glass_box(
            vault_client=vault_client,
            policy_engine=policy_engine,
            negotiator=negotiator
        )
        
        return {
            "forge": forge,
            "vault": vault,
            "vault_client": vault_client,
            "policy_engine": policy_engine,
            "negotiator": negotiator,
            "ledger": ledger,
            "merkle_scheduler": merkle_scheduler
        }
    
    def test_glass_box_enabled(self, components):
        """Test that Glass Box mode is enabled."""
        forge = components["forge"]
        assert forge._glass_box_enabled is True
        assert forge._vault_client is not None
        assert forge._policy_engine is not None
        assert forge._negotiator is not None
    
    def test_verify_with_glass_box_success(self, components):
        """Test successful verification with Glass Box."""
        forge = components["forge"]
        
        constraint = {"field": "amount", "operator": "lt", "value": 1000}
        obj = {"amount": 500}
        
        result = forge.verify_with_glass_box(constraint, obj, operation="test_verify")
        
        assert result is not None
        assert result.passed is True
    
    def test_verify_with_policy_enforcement(self, components):
        """Test verification with policy enforcement."""
        forge = components["forge"]
        policy_engine = components["policy_engine"]
        
        # Add a size limit policy
        policy = Policy(
            id="test_size_limit",
            name="Test Size Limit",
            type=PolicyType.SIZE_LIMIT,
            action=PolicyAction.DENY,
            condition={"max_size": 10}
        )
        policy_engine.add_policy(policy)
        
        constraint = {"field": "data", "operator": "exists", "value": True}
        obj = {"data": "x" * 100}  # Too large
        
        result = forge.verify_with_glass_box(constraint, obj, operation="test_verify")
        
        # Should be blocked by policy
        assert result.passed is False
        assert "policy" in result.message.lower() or "size" in result.message.lower()
    
    def test_provenance_logging(self, components):
        """Test that verifications are logged to vault."""
        forge = components["forge"]
        vault_client = components["vault_client"]
        
        constraint = {"field": "test", "operator": "exists", "value": True}
        obj = {"test": "value"}
        
        initial_stats = vault_client.stats()
        initial_count = initial_stats.get("total_entries", 0)
        
        # Perform verification
        forge.verify_with_glass_box(constraint, obj, operation="test_provenance")
        
        # Check that entry was logged
        updated_stats = vault_client.stats()
        updated_count = updated_stats.get("total_entries", 0)
        
        assert updated_count > initial_count
    
    def test_merkle_anchor_creation(self, components):
        """Test creating Merkle anchors from ledger."""
        ledger = components["ledger"]
        merkle_scheduler = components["merkle_scheduler"]
        
        # Add some entries
        for i in range(5):
            ledger.append(
                operation=f"test_{i}",
                payload={"index": i},
                result="pass"
            )
        
        # Create anchor
        anchor = merkle_scheduler.create_anchor()
        
        assert anchor is not None
        assert anchor.entry_count == len(ledger)
        assert anchor.merkle_root == ledger.get_merkle_root()
    
    def test_merkle_proof_generation_and_verification(self, components):
        """Test generating and verifying Merkle proofs."""
        ledger = components["ledger"]
        merkle_scheduler = components["merkle_scheduler"]
        
        # Add entries
        for i in range(10):
            ledger.append(
                operation=f"test_{i}",
                payload={"data": i},
                result="pass"
            )
        
        # Create anchor
        merkle_scheduler.create_anchor()
        
        # Generate proof for entry 5
        proof = merkle_scheduler.generate_proof(5)
        
        assert proof is not None
        assert proof.entry_index == 5
        assert proof.verified is True
        
        # Verify the proof
        valid = merkle_scheduler.verify_proof(proof)
        assert valid is True
    
    def test_approval_request_flow(self, components):
        """Test human approval request flow."""
        negotiator = components["negotiator"]
        
        # Create approval request
        request = negotiator.request_approval(
            operation="sensitive_operation",
            input_data="critical data",
            reason="Requires human oversight",
            priority=RequestPriority.HIGH
        )
        
        assert request is not None
        assert request.id in negotiator.requests
        
        # Check pending requests
        pending = negotiator.get_pending_requests()
        assert len(pending) > 0
        assert request.id in [r.id for r in pending]
        
        # Approve request
        success = negotiator.approve(request.id, "admin_user", "Approved after review")
        assert success is True
        
        # Verify approval
        approved_request = negotiator.get_request(request.id)
        assert approved_request.approved_by == "admin_user"
    
    def test_policy_input_validation(self, components):
        """Test input validation policies."""
        policy_engine = components["policy_engine"]
        
        # Add input validation policy
        policy = Policy(
            id="required_fields",
            name="Required Fields",
            type=PolicyType.INPUT_VALIDATION,
            action=PolicyAction.DENY,
            condition={"required_fields": ["user_id", "action"]}
        )
        policy_engine.add_policy(policy)
        
        # Test with missing fields
        results = policy_engine.evaluate_input({"user_id": "123"}, "test")
        assert any(not r.passed for r in results)
        
        # Test with all fields
        results = policy_engine.evaluate_input(
            {"user_id": "123", "action": "read"},
            "test"
        )
        assert all(r.passed for r in results)
    
    def test_content_filter_policy(self, components):
        """Test content filtering policies."""
        policy_engine = components["policy_engine"]
        
        # Remove default policies to avoid interference
        for policy_id in list(policy_engine.policies.keys()):
            policy_engine.remove_policy(policy_id)
        
        # Add content filter
        policy = Policy(
            id="sensitive_content",
            name="Sensitive Content Filter",
            type=PolicyType.CONTENT_FILTER,
            action=PolicyAction.WARN,
            condition={"blacklist": ["confidential", "topsecret"]}
        )
        policy_engine.add_policy(policy)
        
        # Test with safe content
        results = policy_engine.evaluate_input("This is normal text", "test")
        content_results = [r for r in results if r.policy_id == "sensitive_content"]
        assert len(content_results) > 0
        assert content_results[0].passed is True
        
        # Test with blacklisted term
        results = policy_engine.evaluate_input("This contains confidential data", "test")
        content_results = [r for r in results if r.policy_id == "sensitive_content"]
        assert len(content_results) > 0
        assert content_results[0].passed is False
    
    def test_full_glass_box_pipeline(self, components):
        """Test complete Glass Box verification pipeline."""
        forge = components["forge"]
        policy_engine = components["policy_engine"]
        ledger = components["ledger"]
        merkle_scheduler = components["merkle_scheduler"]
        
        # Add a policy
        policy = Policy(
            id="test_policy",
            name="Test Policy",
            type=PolicyType.SIZE_LIMIT,
            action=PolicyAction.DENY,
            condition={"max_size": 1000}
        )
        policy_engine.add_policy(policy)
        
        # Add some ledger entries
        for i in range(5):
            ledger.append(
                operation=f"setup_{i}",
                payload={"index": i},
                result="pass"
            )
        
        # Perform verification with Glass Box
        constraint = {"field": "value", "operator": "exists", "value": True}
        obj = {"value": "test data"}
        
        result = forge.verify_with_glass_box(constraint, obj, operation="full_pipeline")
        
        assert result is not None
        assert result.passed is True
        
        # Create Merkle anchor
        anchor = merkle_scheduler.create_anchor()
        assert anchor is not None
        
        # Generate proof for last entry
        last_index = len(ledger) - 1
        proof = merkle_scheduler.generate_proof(last_index)
        
        assert proof is not None
        assert proof.verified is True
        
        # Export certificate
        certificate = proof.export_certificate()
        assert "certificate" in certificate
        assert "proof" in certificate
    
    def test_metrics_collection(self, components):
        """Test that Glass Box components collect metrics."""
        forge = components["forge"]
        policy_engine = components["policy_engine"]
        negotiator = components["negotiator"]
        merkle_scheduler = components["merkle_scheduler"]
        
        # Perform some operations
        constraint = {"field": "test", "operator": "exists", "value": True}
        obj = {"test": "value"}
        
        forge.verify_with_glass_box(constraint, obj)
        
        # Create approval request
        negotiator.request_approval(
            operation="test",
            input_data="data",
            reason="test",
            priority=RequestPriority.MEDIUM
        )
        
        # Get stats
        forge_metrics = forge.get_metrics()
        policy_stats = policy_engine.stats()
        negotiator_stats = negotiator.stats()
        merkle_stats = merkle_scheduler.stats()
        
        assert forge_metrics["total_evaluations"] > 0
        assert "total_policies" in policy_stats
        assert "total_requests" in negotiator_stats
        assert "total_anchors" in merkle_stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
