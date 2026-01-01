#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEGOTIATOR - HUMAN-IN-THE-LOOP (HITL) VERIFICATION
Enable human oversight for critical verification operations.

Part of Glass Box activation - provides interfaces for human approval
of verification operations that require judgment.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import time
import hashlib
import uuid


class ApprovalStatus(Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class RequestPriority(Enum):
    """Priority level for approval requests."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ApprovalRequest:
    """A request for human approval."""
    id: str
    operation: str
    input_data: str
    input_hash: str
    reason: str
    priority: RequestPriority
    status: ApprovalStatus
    created_at: int
    expires_at: int
    approved_by: Optional[str] = None
    approved_at: Optional[int] = None
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "operation": self.operation,
            "input_hash": self.input_hash,
            "reason": self.reason,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
            "rejection_reason": self.rejection_reason,
            "metadata": self.metadata
        }


class Negotiator:
    """
    Negotiator for Human-in-the-Loop verification.
    
    Enables human oversight and approval for verification operations
    that require judgment or exceed automated policy thresholds.
    """
    
    def __init__(self, default_ttl_seconds: int = 3600):
        """
        Initialize Negotiator.
        
        Args:
            default_ttl_seconds: Default time-to-live for approval requests
        """
        self.default_ttl_seconds = default_ttl_seconds
        self.requests: Dict[str, ApprovalRequest] = {}
        self._total_requests = 0
        self._approved_count = 0
        self._rejected_count = 0
        self._expired_count = 0
    
    def request_approval(
        self,
        operation: str,
        input_data: str,
        reason: str,
        priority: RequestPriority = RequestPriority.MEDIUM,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ApprovalRequest:
        """
        Create a new approval request.
        
        Args:
            operation: Type of operation requiring approval
            input_data: Input data for the operation
            reason: Reason approval is required
            priority: Priority level
            ttl_seconds: Time-to-live for the request
            metadata: Additional metadata
        
        Returns:
            ApprovalRequest object
        """
        request_id = str(uuid.uuid4())
        input_hash = hashlib.sha256(input_data.encode()).hexdigest()[:16]
        current_time = int(time.time() * 1000)
        ttl = ttl_seconds or self.default_ttl_seconds
        
        request = ApprovalRequest(
            id=request_id,
            operation=operation,
            input_data=input_data,
            input_hash=input_hash,
            reason=reason,
            priority=priority,
            status=ApprovalStatus.PENDING,
            created_at=current_time,
            expires_at=current_time + (ttl * 1000),
            metadata=metadata or {}
        )
        
        self.requests[request_id] = request
        self._total_requests += 1
        
        return request
    
    def approve(
        self,
        request_id: str,
        approver: str,
        comments: Optional[str] = None
    ) -> bool:
        """
        Approve a pending request.
        
        Args:
            request_id: ID of the request to approve
            approver: Identity of the approver
            comments: Optional comments
        
        Returns:
            True if approved successfully, False otherwise
        """
        request = self.requests.get(request_id)
        if not request:
            return False
        
        if request.status != ApprovalStatus.PENDING:
            return False
        
        # Check if expired
        if int(time.time() * 1000) > request.expires_at:
            request.status = ApprovalStatus.EXPIRED
            self._expired_count += 1
            return False
        
        request.status = ApprovalStatus.APPROVED
        request.approved_by = approver
        request.approved_at = int(time.time() * 1000)
        if comments:
            request.metadata["approval_comments"] = comments
        
        self._approved_count += 1
        return True
    
    def reject(
        self,
        request_id: str,
        rejector: str,
        reason: str
    ) -> bool:
        """
        Reject a pending request.
        
        Args:
            request_id: ID of the request to reject
            rejector: Identity of the rejector
            reason: Reason for rejection
        
        Returns:
            True if rejected successfully, False otherwise
        """
        request = self.requests.get(request_id)
        if not request:
            return False
        
        if request.status != ApprovalStatus.PENDING:
            return False
        
        request.status = ApprovalStatus.REJECTED
        request.approved_by = rejector
        request.approved_at = int(time.time() * 1000)
        request.rejection_reason = reason
        
        self._rejected_count += 1
        return True
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """
        Get an approval request by ID.
        
        Args:
            request_id: ID of the request
        
        Returns:
            ApprovalRequest if found, None otherwise
        """
        request = self.requests.get(request_id)
        if request:
            # Update status if expired
            if (request.status == ApprovalStatus.PENDING and 
                int(time.time() * 1000) > request.expires_at):
                request.status = ApprovalStatus.EXPIRED
                self._expired_count += 1
        
        return request
    
    def get_pending_requests(
        self,
        priority: Optional[RequestPriority] = None,
        operation: Optional[str] = None
    ) -> List[ApprovalRequest]:
        """
        Get all pending approval requests.
        
        Args:
            priority: Optional filter by priority
            operation: Optional filter by operation type
        
        Returns:
            List of pending ApprovalRequests
        """
        current_time = int(time.time() * 1000)
        pending = []
        
        for request in self.requests.values():
            # Update expired requests
            if request.status == ApprovalStatus.PENDING and current_time > request.expires_at:
                request.status = ApprovalStatus.EXPIRED
                self._expired_count += 1
                continue
            
            if request.status != ApprovalStatus.PENDING:
                continue
            
            if priority and request.priority != priority:
                continue
            
            if operation and request.operation != operation:
                continue
            
            pending.append(request)
        
        # Sort by priority and creation time
        priority_order = {
            RequestPriority.CRITICAL: 0,
            RequestPriority.HIGH: 1,
            RequestPriority.MEDIUM: 2,
            RequestPriority.LOW: 3
        }
        
        pending.sort(key=lambda r: (priority_order[r.priority], r.created_at))
        return pending
    
    def wait_for_approval(
        self,
        request_id: str,
        timeout_seconds: Optional[int] = None,
        poll_interval: float = 1.0
    ) -> bool:
        """
        Wait for an approval request to be resolved.
        
        Args:
            request_id: ID of the request to wait for
            timeout_seconds: Maximum time to wait
            poll_interval: Polling interval in seconds
        
        Returns:
            True if approved, False if rejected or expired
        """
        import time as time_module
        
        request = self.requests.get(request_id)
        if not request:
            return False
        
        start_time = time_module.time()
        timeout = timeout_seconds or (request.expires_at - request.created_at) / 1000
        
        while time_module.time() - start_time < timeout:
            request = self.get_request(request_id)
            if not request:
                return False
            
            if request.status == ApprovalStatus.APPROVED:
                return True
            elif request.status in [ApprovalStatus.REJECTED, ApprovalStatus.EXPIRED]:
                return False
            
            time_module.sleep(poll_interval)
        
        return False
    
    def cleanup_old_requests(self, age_seconds: int = 86400) -> int:
        """
        Clean up old requests.
        
        Args:
            age_seconds: Remove requests older than this (default 24 hours)
        
        Returns:
            Number of requests removed
        """
        current_time = int(time.time() * 1000)
        cutoff_time = current_time - (age_seconds * 1000)
        
        to_remove = [
            req_id for req_id, req in self.requests.items()
            if req.created_at < cutoff_time
        ]
        
        for req_id in to_remove:
            del self.requests[req_id]
        
        return len(to_remove)
    
    def stats(self) -> Dict[str, Any]:
        """Get negotiator statistics."""
        return {
            "total_requests": self._total_requests,
            "pending": len(self.get_pending_requests()),
            "approved": self._approved_count,
            "rejected": self._rejected_count,
            "expired": self._expired_count,
            "approval_rate": round(self._approved_count / self._total_requests * 100, 2)
                if self._total_requests > 0 else 0
        }


# Global negotiator instance
_negotiator: Optional[Negotiator] = None


def get_negotiator(ttl_seconds: int = 3600) -> Negotiator:
    """Get the global Negotiator instance."""
    global _negotiator
    if _negotiator is None:
        _negotiator = Negotiator(default_ttl_seconds=ttl_seconds)
    return _negotiator
