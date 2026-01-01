#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
MERKLE PROOF TESTS
Tests for Merkle tree anchoring and proof verification.
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
import tempfile
import shutil
from core.merkle_anchor import (
    MerkleAnchorScheduler, MerkleAnchor, MerkleProof, verify_merkle_proof
)
from core.ledger import Ledger, LedgerConfig


class TestMerkleAnchor:
    """Test suite for Merkle anchoring."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def ledger(self, temp_storage):
        """Create a test ledger."""
        config = LedgerConfig(storage_path=os.path.join(temp_storage, "ledger"))
        ledger = Ledger(config)
        
        # Add some test entries
        for i in range(10):
            ledger.append(
                operation=f"test_{i}",
                payload={"index": i},
                result="pass"
            )
        
        return ledger
    
    def test_create_scheduler(self, ledger, temp_storage):
        """Test creating a Merkle anchor scheduler."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        assert scheduler is not None
        assert scheduler.ledger == ledger
        assert scheduler.interval_seconds == 300
    
    def test_create_anchor(self, ledger, temp_storage):
        """Test creating a Merkle anchor."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        anchor = scheduler.create_anchor()
        
        assert anchor is not None
        assert anchor.ledger_index == len(ledger) - 1
        assert anchor.entry_count == len(ledger)
        assert anchor.merkle_root == ledger.get_merkle_root()
        assert anchor.id in scheduler.anchors
    
    def test_create_anchor_no_new_entries(self, ledger, temp_storage):
        """Test that creating anchor with no new entries returns None."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        # Create first anchor
        anchor1 = scheduler.create_anchor()
        assert anchor1 is not None
        
        # Try to create another without new entries
        anchor2 = scheduler.create_anchor()
        assert anchor2 is None
    
    def test_get_anchor(self, ledger, temp_storage):
        """Test getting an anchor by ID."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        anchor = scheduler.create_anchor()
        
        retrieved = scheduler.get_anchor(anchor.id)
        assert retrieved is not None
        assert retrieved.id == anchor.id
        assert retrieved.merkle_root == anchor.merkle_root
    
    def test_get_latest_anchor(self, ledger, temp_storage):
        """Test getting the latest anchor."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        # No anchors yet
        latest = scheduler.get_latest_anchor()
        assert latest is None
        
        # Create anchor
        anchor1 = scheduler.create_anchor()
        
        # Add more entries
        ledger.append(operation="new_test", payload={"test": True}, result="pass")
        
        # Create another anchor
        time.sleep(0.1)  # Ensure different timestamp
        anchor2 = scheduler.create_anchor()
        
        # Get latest
        latest = scheduler.get_latest_anchor()
        assert latest is not None
        assert latest.id == anchor2.id
    
    def test_get_all_anchors(self, ledger, temp_storage):
        """Test getting all anchors."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        # Create multiple anchors
        anchor1 = scheduler.create_anchor()
        
        ledger.append(operation="test1", payload={}, result="pass")
        anchor2 = scheduler.create_anchor()
        
        ledger.append(operation="test2", payload={}, result="pass")
        anchor3 = scheduler.create_anchor()
        
        all_anchors = scheduler.get_all_anchors()
        assert len(all_anchors) == 3
        
        # Should be sorted by timestamp (newest first)
        assert all_anchors[0].timestamp >= all_anchors[1].timestamp
        assert all_anchors[1].timestamp >= all_anchors[2].timestamp
    
    def test_generate_proof(self, ledger, temp_storage):
        """Test generating a Merkle proof."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        # Create anchor
        scheduler.create_anchor()
        
        # Generate proof for entry 5
        proof = scheduler.generate_proof(5)
        
        assert proof is not None
        assert proof.entry_index == 5
        assert proof.verified is True
        assert len(proof.proof_path) > 0
        assert proof.merkle_root == ledger.get_merkle_root()
    
    def test_verify_proof(self, ledger, temp_storage):
        """Test verifying a Merkle proof."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        # Create anchor
        scheduler.create_anchor()
        
        # Generate proof
        proof = scheduler.generate_proof(3)
        
        # Verify proof
        valid = scheduler.verify_proof(proof)
        assert valid is True
    
    def test_standalone_verify_merkle_proof(self, ledger, temp_storage):
        """Test standalone proof verification function."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        # Generate proof
        proof = scheduler.generate_proof(2)
        
        # Verify using standalone function
        valid = verify_merkle_proof(
            proof.entry_hash,
            proof.proof_path,
            proof.merkle_root
        )
        assert valid is True
    
    def test_invalid_proof(self, ledger, temp_storage):
        """Test verification of invalid proof."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        # Generate proof
        proof = scheduler.generate_proof(1)
        
        # Tamper with the proof
        proof.entry_hash = "0" * 64
        
        # Verify should fail
        valid = scheduler.verify_proof(proof)
        assert valid is False
    
    def test_export_certificate(self, ledger, temp_storage):
        """Test exporting a verification certificate."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        # Generate proof
        proof = scheduler.generate_proof(4)
        
        # Export certificate
        certificate = proof.export_certificate()
        
        assert "certificate" in certificate
        assert "proof" in certificate
        assert certificate["certificate"]["type"] == "merkle_proof"
        assert certificate["certificate"]["entry_index"] == 4
        assert certificate["certificate"]["verified"] is True
    
    def test_scheduler_start_stop(self, ledger, temp_storage):
        """Test starting and stopping the scheduler."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, interval_seconds=1, storage_path=storage_path)
        
        assert scheduler._running is False
        
        # Start scheduler
        scheduler.start()
        assert scheduler._running is True
        
        # Stop scheduler
        scheduler.stop()
        assert scheduler._running is False
    
    def test_scheduler_stats(self, ledger, temp_storage):
        """Test scheduler statistics."""
        storage_path = os.path.join(temp_storage, "anchors")
        scheduler = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        # Create some anchors
        scheduler.create_anchor()
        ledger.append(operation="test", payload={}, result="pass")
        scheduler.create_anchor()
        
        stats = scheduler.stats()
        assert stats["total_anchors"] == 2
        assert stats["last_anchor_index"] >= 0
        assert "running" in stats
        assert "interval_seconds" in stats
        assert stats["latest_anchor"] is not None
    
    def test_anchor_persistence(self, ledger, temp_storage):
        """Test that anchors persist across scheduler instances."""
        storage_path = os.path.join(temp_storage, "anchors")
        
        # Create scheduler and anchor
        scheduler1 = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        anchor1 = scheduler1.create_anchor()
        anchor_id = anchor1.id
        
        # Create new scheduler instance
        scheduler2 = MerkleAnchorScheduler(ledger, storage_path=storage_path)
        
        # Should load existing anchor
        retrieved = scheduler2.get_anchor(anchor_id)
        assert retrieved is not None
        assert retrieved.id == anchor_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
