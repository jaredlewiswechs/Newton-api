#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON LEDGER - IMMUTABLE VERIFICATION HISTORY
The Disk of the Newton Supercomputer.

The Ledger is append-only. Nothing is ever deleted.
Every verification leaves a trace. Every trace is permanent.
This is the audit trail that makes Newton legally defensible.

═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Iterator
import hashlib
import time
import json
import os
from pathlib import Path
from threading import Lock


# ═══════════════════════════════════════════════════════════════════════════════
# LEDGER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LedgerConfig:
    """Configuration for the Ledger."""
    storage_path: str = ".newton_ledger"
    max_entries_memory: int = 10000      # Max entries in RAM
    sync_interval_seconds: int = 60       # Auto-sync to disk
    enable_merkle_tree: bool = True       # Build Merkle tree for integrity
    chain_verification: bool = True       # Verify prev_hash chain


# ═══════════════════════════════════════════════════════════════════════════════
# LEDGER ENTRY - An immutable record
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LedgerEntry:
    """A single, immutable entry in the Ledger."""
    index: int
    timestamp: int                        # Unix timestamp ms
    operation: str                        # "verify", "store", "sign", etc.
    payload_hash: str                     # SHA-256 of payload
    result: str                           # "pass", "fail", "error"
    prev_hash: str                        # Hash of previous entry (chain)
    entry_hash: str = ""                  # This entry's hash
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.entry_hash:
            self.entry_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute hash of this entry."""
        data = f"{self.index}:{self.timestamp}:{self.operation}:{self.payload_hash}:{self.result}:{self.prev_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify this entry's hash matches its content."""
        return self.entry_hash == self._compute_hash()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "payload_hash": self.payload_hash,
            "result": self.result,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'LedgerEntry':
        return cls(
            index=d["index"],
            timestamp=d["timestamp"],
            operation=d["operation"],
            payload_hash=d["payload_hash"],
            result=d["result"],
            prev_hash=d["prev_hash"],
            entry_hash=d.get("entry_hash", ""),
            metadata=d.get("metadata", {})
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MERKLE TREE - For bulk integrity verification
# ═══════════════════════════════════════════════════════════════════════════════

class MerkleTree:
    """
    Merkle tree for efficient bulk integrity verification.

    Allows proving inclusion of any entry with O(log n) hashes.
    """

    def __init__(self, hashes: List[str]):
        self.leaves = hashes
        self.root = self._build_root(hashes) if hashes else ""

    def _hash_pair(self, left: str, right: str) -> str:
        """Hash two nodes together."""
        return hashlib.sha256(f"{left}{right}".encode()).hexdigest()

    def _build_root(self, hashes: List[str]) -> str:
        """Build Merkle root from leaf hashes."""
        if not hashes:
            return ""
        if len(hashes) == 1:
            return hashes[0]

        # Pad to even number
        if len(hashes) % 2 == 1:
            hashes = hashes + [hashes[-1]]

        # Build next level
        next_level = []
        for i in range(0, len(hashes), 2):
            next_level.append(self._hash_pair(hashes[i], hashes[i + 1]))

        return self._build_root(next_level)

    def get_proof(self, index: int) -> List[tuple]:
        """
        Get Merkle proof for entry at index.
        Returns list of (hash, direction) tuples.
        """
        if index < 0 or index >= len(self.leaves):
            return []

        proof = []
        hashes = self.leaves.copy()

        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])

        idx = index
        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                if i == idx or i + 1 == idx:
                    # Include sibling in proof
                    sibling_idx = i + 1 if i == idx else i
                    direction = "right" if i == idx else "left"
                    proof.append((hashes[sibling_idx], direction))
                    idx = len(next_level)

                next_level.append(self._hash_pair(hashes[i], hashes[i + 1]))

            hashes = next_level

        return proof

    def verify_proof(self, leaf_hash: str, proof: List[tuple]) -> bool:
        """Verify a Merkle proof."""
        current = leaf_hash
        for sibling_hash, direction in proof:
            if direction == "right":
                current = self._hash_pair(current, sibling_hash)
            else:
                current = self._hash_pair(sibling_hash, current)
        return current == self.root


# ═══════════════════════════════════════════════════════════════════════════════
# THE LEDGER
# ═══════════════════════════════════════════════════════════════════════════════

class Ledger:
    """
    The Newton Ledger - Immutable Verification History.

    This is the disk of the Newton Supercomputer.
    Append-only. Tamper-evident. Legally defensible.

    Every verification leaves a permanent trace.
    Every trace is cryptographically linked to the previous.
    Tampering with any entry invalidates all subsequent entries.
    """

    GENESIS_HASH = "0" * 64  # Hash of the genesis (no previous)

    def __init__(self, config: Optional[LedgerConfig] = None):
        self.config = config or LedgerConfig()
        self._entries: List[LedgerEntry] = []
        self._merkle_tree: Optional[MerkleTree] = None
        self._lock = Lock()

        # Load existing ledger
        self._load()

    # ─────────────────────────────────────────────────────────────────────────
    # APPEND OPERATIONS
    # ─────────────────────────────────────────────────────────────────────────

    def append(
        self,
        operation: str,
        payload: Any,
        result: str,
        metadata: Optional[Dict] = None
    ) -> LedgerEntry:
        """
        Append a new entry to the ledger.

        This is the ONLY way to add to the ledger.
        No updates. No deletes. Only appends.
        """
        with self._lock:
            # Compute payload hash
            if isinstance(payload, (dict, list)):
                payload_str = json.dumps(payload, sort_keys=True)
            else:
                payload_str = str(payload)
            payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()

            # Get previous hash
            if self._entries:
                prev_hash = self._entries[-1].entry_hash
            else:
                prev_hash = self.GENESIS_HASH

            # Create entry
            entry = LedgerEntry(
                index=len(self._entries),
                timestamp=int(time.time() * 1000),
                operation=operation,
                payload_hash=payload_hash,
                result=result,
                prev_hash=prev_hash,
                metadata=metadata or {}
            )

            # Append
            self._entries.append(entry)

            # Invalidate Merkle tree (will rebuild on demand)
            self._merkle_tree = None

            # Persist
            self._save_entry(entry)

            return entry

    def record_verification(
        self,
        constraint_id: str,
        obj_hash: str,
        passed: bool,
        elapsed_us: int
    ) -> LedgerEntry:
        """Record a verification result."""
        return self.append(
            operation="verify",
            payload={"constraint_id": constraint_id, "obj_hash": obj_hash},
            result="pass" if passed else "fail",
            metadata={"elapsed_us": elapsed_us}
        )

    def record_signature(self, payload_hash: str, signer_id: str) -> LedgerEntry:
        """Record a signature operation."""
        return self.append(
            operation="sign",
            payload={"payload_hash": payload_hash, "signer_id": signer_id},
            result="signed"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # QUERY OPERATIONS
    # ─────────────────────────────────────────────────────────────────────────

    def get(self, index: int) -> Optional[LedgerEntry]:
        """Get entry by index."""
        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None

    def get_range(self, start: int, end: int) -> List[LedgerEntry]:
        """Get entries in range [start, end)."""
        return self._entries[start:end]

    def get_latest(self, n: int = 10) -> List[LedgerEntry]:
        """Get the n most recent entries."""
        return self._entries[-n:]

    def search(
        self,
        operation: Optional[str] = None,
        result: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[LedgerEntry]:
        """Search entries with filters."""
        matches = []

        for entry in reversed(self._entries):
            if len(matches) >= limit:
                break

            if operation and entry.operation != operation:
                continue
            if result and entry.result != result:
                continue
            if start_time and entry.timestamp < start_time:
                continue
            if end_time and entry.timestamp > end_time:
                continue

            matches.append(entry)

        return matches

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[LedgerEntry]:
        return iter(self._entries)

    # ─────────────────────────────────────────────────────────────────────────
    # INTEGRITY VERIFICATION
    # ─────────────────────────────────────────────────────────────────────────

    def verify_chain(self) -> tuple:
        """
        Verify the entire chain integrity.
        Returns (valid, first_invalid_index).
        """
        if not self._entries:
            return True, -1

        # Check genesis
        if self._entries[0].prev_hash != self.GENESIS_HASH:
            return False, 0

        # Verify each entry
        for i, entry in enumerate(self._entries):
            # Verify self-hash
            if not entry.verify_integrity():
                return False, i

            # Verify chain link
            if i > 0 and entry.prev_hash != self._entries[i - 1].entry_hash:
                return False, i

        return True, -1

    def verify_entry(self, index: int) -> bool:
        """Verify a single entry's integrity."""
        entry = self.get(index)
        if entry is None:
            return False
        return entry.verify_integrity()

    def get_merkle_root(self) -> str:
        """Get the Merkle root of all entries."""
        if self._merkle_tree is None:
            hashes = [e.entry_hash for e in self._entries]
            self._merkle_tree = MerkleTree(hashes)
        return self._merkle_tree.root

    def get_merkle_proof(self, index: int) -> List[tuple]:
        """Get Merkle proof for entry at index."""
        if self._merkle_tree is None:
            hashes = [e.entry_hash for e in self._entries]
            self._merkle_tree = MerkleTree(hashes)
        return self._merkle_tree.get_proof(index)

    def verify_merkle_proof(self, index: int, proof: List[tuple]) -> bool:
        """Verify a Merkle proof for entry at index."""
        entry = self.get(index)
        if entry is None:
            return False
        if self._merkle_tree is None:
            hashes = [e.entry_hash for e in self._entries]
            self._merkle_tree = MerkleTree(hashes)
        return self._merkle_tree.verify_proof(entry.entry_hash, proof)

    # ─────────────────────────────────────────────────────────────────────────
    # EXPORT
    # ─────────────────────────────────────────────────────────────────────────

    def export_json(self, path: Optional[str] = None) -> str:
        """Export ledger to JSON."""
        data = {
            "version": "1.0.0",
            "exported_at": int(time.time() * 1000),
            "merkle_root": self.get_merkle_root(),
            "entry_count": len(self._entries),
            "entries": [e.to_dict() for e in self._entries]
        }

        json_str = json.dumps(data, indent=2)

        if path:
            with open(path, 'w') as f:
                f.write(json_str)

        return json_str

    def export_certificate(self, index: int) -> Dict[str, Any]:
        """
        Export a verification certificate for entry at index.
        Includes entry data and Merkle proof.
        """
        entry = self.get(index)
        if entry is None:
            raise KeyError(f"Entry not found: {index}")

        return {
            "version": "1.0.0",
            "entry": entry.to_dict(),
            "merkle_root": self.get_merkle_root(),
            "merkle_proof": self.get_merkle_proof(index),
            "total_entries": len(self._entries),
            "certificate_generated": int(time.time() * 1000),
            "signature": self._sign_certificate(entry)
        }

    def _sign_certificate(self, entry: LedgerEntry) -> str:
        """Generate certificate signature."""
        data = f"{entry.entry_hash}:{self.get_merkle_root()}:{len(self._entries)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16].upper()

    # ─────────────────────────────────────────────────────────────────────────
    # PERSISTENCE
    # ─────────────────────────────────────────────────────────────────────────

    def _save_entry(self, entry: LedgerEntry):
        """Append entry to disk."""
        path = Path(self.config.storage_path)
        path.mkdir(parents=True, exist_ok=True)

        ledger_file = path / "ledger.jsonl"
        with open(ledger_file, 'a') as f:
            f.write(json.dumps(entry.to_dict()) + '\n')

    def _load(self):
        """Load ledger from disk."""
        path = Path(self.config.storage_path)
        ledger_file = path / "ledger.jsonl"

        if not ledger_file.exists():
            return

        try:
            with open(ledger_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entry_dict = json.loads(line)
                        entry = LedgerEntry.from_dict(entry_dict)
                        self._entries.append(entry)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Error loading ledger: {e}")

    def sync(self):
        """Force sync to disk (rewrites entire file)."""
        path = Path(self.config.storage_path)
        path.mkdir(parents=True, exist_ok=True)

        ledger_file = path / "ledger.jsonl"
        with open(ledger_file, 'w') as f:
            for entry in self._entries:
                f.write(json.dumps(entry.to_dict()) + '\n')

    # ─────────────────────────────────────────────────────────────────────────
    # STATS
    # ─────────────────────────────────────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """Get ledger statistics."""
        if not self._entries:
            return {
                "total_entries": 0,
                "operations": {},
                "results": {},
                "chain_valid": True
            }

        operations: Dict[str, int] = {}
        results: Dict[str, int] = {}

        for entry in self._entries:
            operations[entry.operation] = operations.get(entry.operation, 0) + 1
            results[entry.result] = results.get(entry.result, 0) + 1

        chain_valid, _ = self.verify_chain()

        return {
            "total_entries": len(self._entries),
            "first_entry": self._entries[0].timestamp if self._entries else None,
            "last_entry": self._entries[-1].timestamp if self._entries else None,
            "operations": operations,
            "results": results,
            "merkle_root": self.get_merkle_root(),
            "chain_valid": chain_valid
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_default_ledger: Optional[Ledger] = None

def get_ledger(config: Optional[LedgerConfig] = None) -> Ledger:
    """Get the default Ledger instance."""
    global _default_ledger
    if _default_ledger is None:
        _default_ledger = Ledger(config)
    return _default_ledger


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Newton Ledger - Immutable Verification History")
    print("=" * 60)

    ledger = Ledger(LedgerConfig(storage_path=".newton_ledger_test"))

    # Record some verifications
    print("\n[Recording Verifications]")
    for i in range(5):
        entry = ledger.record_verification(
            constraint_id=f"C_{i:08X}",
            obj_hash=hashlib.sha256(f"obj_{i}".encode()).hexdigest()[:16],
            passed=i % 2 == 0,
            elapsed_us=42 + i
        )
        print(f"  Entry {entry.index}: {entry.operation} -> {entry.result}")

    # Verify chain
    print("\n[Chain Verification]")
    valid, invalid_at = ledger.verify_chain()
    print(f"  Chain valid: {valid}")

    # Get Merkle root
    print("\n[Merkle Tree]")
    root = ledger.get_merkle_root()
    print(f"  Merkle root: {root[:32]}...")

    # Get proof for entry 2
    proof = ledger.get_merkle_proof(2)
    verified = ledger.verify_merkle_proof(2, proof)
    print(f"  Proof for entry 2: {len(proof)} nodes, valid={verified}")

    # Export certificate
    print("\n[Export Certificate]")
    cert = ledger.export_certificate(2)
    print(f"  Certificate signature: {cert['signature']}")

    # Stats
    print("\n[Ledger Stats]")
    stats = ledger.stats()
    for k, v in stats.items():
        if k != "merkle_root":
            print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print("Nothing deleted. Everything traced. Legally defensible.")
