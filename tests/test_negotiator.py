#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEGOTIATOR TESTS
Tests for the Human-in-the-Loop (HITL) negotiator.
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
from core.negotiator import (
    Negotiator, ApprovalRequest, ApprovalStatus, RequestPriority
)


class TestNegotiator:
    """Test suite for Negotiator."""
    
    def test_create_negotiator(self):
        """Test creating a negotiator."""
        negotiator = Negotiator()
        assert negotiator is not None
        assert negotiator.default_ttl_seconds == 3600
    
    def test_request_approval(self):
        """Test creating an approval request."""
        negotiator = Negotiator()
        
        request = negotiator.request_approval(
            operation="verify",
            input_data="test data",
            reason="Testing approval flow",
            priority=RequestPriority.MEDIUM
        )
        
        assert request is not None
        assert request.operation == "verify"
        assert request.status == ApprovalStatus.PENDING
        assert request.priority == RequestPriority.MEDIUM
        assert request.id in negotiator.requests
    
    def test_approve_request(self):
        """Test approving a request."""
        negotiator = Negotiator()
        
        request = negotiator.request_approval(
            operation="verify",
            input_data="test data",
            reason="Testing",
            priority=RequestPriority.MEDIUM
        )
        
        # Approve the request
        success = negotiator.approve(
            request.id,
            approver="test_user",
            comments="Looks good"
        )
        
        assert success is True
        approved_request = negotiator.get_request(request.id)
        assert approved_request.status == ApprovalStatus.APPROVED
        assert approved_request.approved_by == "test_user"
        assert approved_request.metadata.get("approval_comments") == "Looks good"
    
    def test_reject_request(self):
        """Test rejecting a request."""
        negotiator = Negotiator()
        
        request = negotiator.request_approval(
            operation="verify",
            input_data="test data",
            reason="Testing",
            priority=RequestPriority.MEDIUM
        )
        
        # Reject the request
        success = negotiator.reject(
            request.id,
            rejector="test_user",
            reason="Invalid input"
        )
        
        assert success is True
        rejected_request = negotiator.get_request(request.id)
        assert rejected_request.status == ApprovalStatus.REJECTED
        assert rejected_request.approved_by == "test_user"
        assert rejected_request.rejection_reason == "Invalid input"
    
    def test_approve_nonexistent_request(self):
        """Test approving non-existent request."""
        negotiator = Negotiator()
        
        success = negotiator.approve("non_existent_id", "test_user")
        assert success is False
    
    def test_approve_already_approved(self):
        """Test approving already approved request."""
        negotiator = Negotiator()
        
        request = negotiator.request_approval(
            operation="verify",
            input_data="test data",
            reason="Testing",
            priority=RequestPriority.MEDIUM
        )
        
        # First approval
        negotiator.approve(request.id, "user1")
        
        # Try to approve again
        success = negotiator.approve(request.id, "user2")
        assert success is False
    
    def test_expired_request(self):
        """Test request expiration."""
        negotiator = Negotiator(default_ttl_seconds=1)
        
        request = negotiator.request_approval(
            operation="verify",
            input_data="test data",
            reason="Testing expiration",
            priority=RequestPriority.MEDIUM,
            ttl_seconds=1
        )
        
        assert request.status == ApprovalStatus.PENDING
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Try to approve expired request
        success = negotiator.approve(request.id, "test_user")
        assert success is False
        
        # Check status is expired
        expired_request = negotiator.get_request(request.id)
        assert expired_request.status == ApprovalStatus.EXPIRED
    
    def test_get_pending_requests(self):
        """Test getting pending requests."""
        negotiator = Negotiator()
        
        # Create requests with different priorities
        negotiator.request_approval(
            operation="verify",
            input_data="data1",
            reason="Test 1",
            priority=RequestPriority.LOW
        )
        
        negotiator.request_approval(
            operation="calculate",
            input_data="data2",
            reason="Test 2",
            priority=RequestPriority.HIGH
        )
        
        negotiator.request_approval(
            operation="verify",
            input_data="data3",
            reason="Test 3",
            priority=RequestPriority.CRITICAL
        )
        
        # Get all pending
        all_pending = negotiator.get_pending_requests()
        assert len(all_pending) == 3
        
        # Check they're sorted by priority
        assert all_pending[0].priority == RequestPriority.CRITICAL
        assert all_pending[1].priority == RequestPriority.HIGH
        assert all_pending[2].priority == RequestPriority.LOW
        
        # Filter by priority
        high_pending = negotiator.get_pending_requests(priority=RequestPriority.HIGH)
        assert len(high_pending) == 1
        assert high_pending[0].priority == RequestPriority.HIGH
        
        # Filter by operation
        verify_pending = negotiator.get_pending_requests(operation="verify")
        assert len(verify_pending) == 2
    
    def test_cleanup_old_requests(self):
        """Test cleaning up old requests."""
        negotiator = Negotiator()
        
        # Create a request
        request = negotiator.request_approval(
            operation="verify",
            input_data="test data",
            reason="Test cleanup",
            priority=RequestPriority.MEDIUM
        )
        
        # Manually set creation time to old
        request.created_at = int((time.time() - 100000) * 1000)
        
        # Clean up old requests
        removed = negotiator.cleanup_old_requests(age_seconds=86400)
        assert removed == 1
        assert request.id not in negotiator.requests
    
    def test_negotiator_stats(self):
        """Test negotiator statistics."""
        negotiator = Negotiator()
        
        # Create and process some requests
        req1 = negotiator.request_approval(
            operation="verify",
            input_data="data1",
            reason="Test",
            priority=RequestPriority.MEDIUM
        )
        
        req2 = negotiator.request_approval(
            operation="verify",
            input_data="data2",
            reason="Test",
            priority=RequestPriority.MEDIUM
        )
        
        req3 = negotiator.request_approval(
            operation="verify",
            input_data="data3",
            reason="Test",
            priority=RequestPriority.MEDIUM
        )
        
        negotiator.approve(req1.id, "user1")
        negotiator.reject(req2.id, "user1", "rejected")
        
        stats = negotiator.stats()
        assert stats["total_requests"] == 3
        assert stats["pending"] == 1
        assert stats["approved"] == 1
        assert stats["rejected"] == 1
        assert "approval_rate" in stats
    
    def test_request_with_metadata(self):
        """Test request with custom metadata."""
        negotiator = Negotiator()
        
        metadata = {
            "source": "api",
            "user_id": "12345",
            "timestamp": int(time.time())
        }
        
        request = negotiator.request_approval(
            operation="verify",
            input_data="test data",
            reason="Testing metadata",
            priority=RequestPriority.MEDIUM,
            metadata=metadata
        )
        
        assert request.metadata == metadata
        assert request.metadata["source"] == "api"
    
    def test_to_dict(self):
        """Test serialization to dict."""
        negotiator = Negotiator()
        
        request = negotiator.request_approval(
            operation="verify",
            input_data="test data",
            reason="Testing",
            priority=RequestPriority.HIGH
        )
        
        request_dict = request.to_dict()
        assert request_dict["operation"] == "verify"
        assert request_dict["priority"] == "high"
        assert request_dict["status"] == "pending"
        assert "id" in request_dict
        assert "created_at" in request_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
