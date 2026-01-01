#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
MERKLE ANCHOR - MERKLE TREE ANCHORING AND PROOF EXPORT
Scheduled Merkle root anchoring and proof generation.

Part of Glass Box activation - provides periodic anchoring of ledger state
and export of cryptographic proofs for external verification.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import hashlib
import time
import json
import threading
from pathlib import Path


@dataclass
class MerkleAnchor:
    """A Merkle tree anchor point."""
    id: str
    merkle_root: str
    ledger_index: int
    timestamp: int
    entry_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "merkle_root": self.merkle_root,
            "ledger_index": self.ledger_index,
            "timestamp": self.timestamp,
            "entry_count": self.entry_count,
            "metadata": self.metadata
        }


@dataclass
class MerkleProof:
    """A Merkle proof for a specific entry."""
    entry_index: int
    entry_hash: str
    merkle_root: str
    proof_path: List[Dict[str, str]]
    verified: bool
    anchor_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_index": self.entry_index,
            "entry_hash": self.entry_hash,
            "merkle_root": self.merkle_root,
            "proof_path": self.proof_path,
            "verified": self.verified,
            "anchor_id": self.anchor_id
        }
    
    def export_certificate(self) -> Dict[str, Any]:
        """Export a verification certificate."""
        return {
            "certificate": {
                "version": "1.0",
                "type": "merkle_proof",
                "entry_index": self.entry_index,
                "entry_hash": self.entry_hash,
                "merkle_root": self.merkle_root,
                "verified": self.verified,
                "anchor_id": self.anchor_id,
                "generated_at": int(time.time() * 1000)
            },
            "proof": {
                "path": self.proof_path,
                "verification": "Use verify_merkle_proof() to verify this proof"
            }
        }


class MerkleAnchorScheduler:
    """
    Scheduler for periodic Merkle tree anchoring.
    
    Creates anchor points at regular intervals for the ledger,
    enabling efficient verification and external attestation.
    """
    
    def __init__(
        self,
        ledger,
        interval_seconds: int = 300,
        storage_path: str = ".newton_anchors"
    ):
        """
        Initialize MerkleAnchorScheduler.
        
        Args:
            ledger: Ledger instance to anchor
            interval_seconds: Interval between anchors (default 5 minutes)
            storage_path: Path to store anchor data
        """
        self.ledger = ledger
        self.interval_seconds = interval_seconds
        self.storage_path = Path(storage_path)
        self.anchors: Dict[str, MerkleAnchor] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_anchor_index = -1
        
        # Create storage directory
        self.storage_path.mkdir(exist_ok=True)
        
        # Load existing anchors
        self._load_anchors()
    
    def _load_anchors(self) -> None:
        """Load anchors from disk."""
        anchor_file = self.storage_path / "anchors.json"
        if anchor_file.exists():
            try:
                with open(anchor_file, 'r') as f:
                    data = json.load(f)
                    for anchor_data in data.get("anchors", []):
                        anchor = MerkleAnchor(**anchor_data)
                        self.anchors[anchor.id] = anchor
                        if anchor.ledger_index > self._last_anchor_index:
                            self._last_anchor_index = anchor.ledger_index
            except Exception:
                pass
    
    def _save_anchors(self) -> None:
        """Save anchors to disk."""
        anchor_file = self.storage_path / "anchors.json"
        try:
            data = {
                "anchors": [a.to_dict() for a in self.anchors.values()],
                "last_updated": int(time.time() * 1000)
            }
            with open(anchor_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def create_anchor(self) -> Optional[MerkleAnchor]:
        """
        Create a new anchor point.
        
        Returns:
            MerkleAnchor if created, None if no new entries
        """
        current_index = len(self.ledger) - 1
        
        # Check if there are new entries since last anchor
        if current_index <= self._last_anchor_index:
            return None
        
        # Get current Merkle root
        merkle_root = self.ledger.get_merkle_root()
        
        # Create anchor ID
        anchor_id = hashlib.sha256(
            f"{merkle_root}:{current_index}:{int(time.time())}".encode()
        ).hexdigest()[:16]
        
        anchor = MerkleAnchor(
            id=anchor_id,
            merkle_root=merkle_root,
            ledger_index=current_index,
            timestamp=int(time.time() * 1000),
            entry_count=current_index + 1,
            metadata={"auto_generated": True}
        )
        
        self.anchors[anchor_id] = anchor
        self._last_anchor_index = current_index
        self._save_anchors()
        
        return anchor
    
    def get_anchor(self, anchor_id: str) -> Optional[MerkleAnchor]:
        """Get an anchor by ID."""
        return self.anchors.get(anchor_id)
    
    def get_latest_anchor(self) -> Optional[MerkleAnchor]:
        """Get the most recent anchor."""
        if not self.anchors:
            return None
        
        return max(self.anchors.values(), key=lambda a: a.timestamp)
    
    def get_all_anchors(self) -> List[MerkleAnchor]:
        """Get all anchors sorted by timestamp."""
        return sorted(self.anchors.values(), key=lambda a: a.timestamp, reverse=True)
    
    def generate_proof(self, entry_index: int) -> Optional[MerkleProof]:
        """
        Generate a Merkle proof for a specific entry.
        
        Args:
            entry_index: Index of the entry in the ledger
        
        Returns:
            MerkleProof if successful, None otherwise
        """
        # Get Merkle proof from ledger
        proof_path = self.ledger.get_merkle_proof(entry_index)
        if not proof_path:
            return None
        
        # Get entry
        entry = self.ledger.get(entry_index)
        if not entry:
            return None
        
        # Get current Merkle root
        merkle_root = self.ledger.get_merkle_root()
        
        # Verify the proof
        verified = self.ledger.verify_entry(entry_index)
        
        # Find associated anchor
        anchor_id = None
        for anchor in self.anchors.values():
            if anchor.ledger_index >= entry_index:
                anchor_id = anchor.id
                break
        
        return MerkleProof(
            entry_index=entry_index,
            entry_hash=entry.entry_hash,
            merkle_root=merkle_root,
            proof_path=proof_path,
            verified=verified,
            anchor_id=anchor_id
        )
    
    def verify_proof(self, proof: MerkleProof) -> bool:
        """
        Verify a Merkle proof.
        
        Args:
            proof: MerkleProof to verify
        
        Returns:
            True if proof is valid
        """
        # Reconstruct Merkle root from proof
        current_hash = proof.entry_hash
        
        for step in proof.proof_path:
            sibling = step.get("hash", "")
            direction = step.get("direction", "left")
            
            if direction == "left":
                combined = sibling + current_hash
            else:
                combined = current_hash + sibling
            
            current_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        return current_hash == proof.merkle_root
    
    def start(self) -> None:
        """Start the anchor scheduler."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the anchor scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
    
    def _run(self) -> None:
        """Run the scheduler loop."""
        while self._running:
            try:
                self.create_anchor()
            except Exception:
                pass
            
            # Sleep in small intervals to allow for quick shutdown
            for _ in range(self.interval_seconds):
                if not self._running:
                    break
                time.sleep(1)
    
    def stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        return {
            "total_anchors": len(self.anchors),
            "last_anchor_index": self._last_anchor_index,
            "running": self._running,
            "interval_seconds": self.interval_seconds,
            "latest_anchor": self.get_latest_anchor().to_dict() if self.get_latest_anchor() else None
        }


def verify_merkle_proof(
    entry_hash: str,
    proof_path: List[Dict[str, str]],
    merkle_root: str
) -> bool:
    """
    Standalone function to verify a Merkle proof.
    
    Args:
        entry_hash: Hash of the entry
        proof_path: Path from entry to root
        merkle_root: Expected Merkle root
    
    Returns:
        True if proof is valid
    """
    current_hash = entry_hash
    
    for step in proof_path:
        sibling = step.get("hash", "")
        direction = step.get("direction", "left")
        
        if direction == "left":
            combined = sibling + current_hash
        else:
            combined = current_hash + sibling
        
        current_hash = hashlib.sha256(combined.encode()).hexdigest()
    
    return current_hash == merkle_root
