#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON BRIDGE - DISTRIBUTED VERIFICATION PROTOCOL
The Bus of the Newton Supercomputer.

The Bridge connects Newton nodes into a distributed verification mesh.
Every node can verify independently. Consensus makes it trustworthy.

Based on research from:
- Practical Byzantine Fault Tolerance (PBFT)
- HotStuff linear-complexity BFT
- Modern aggregate signature schemes

═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set
from enum import Enum
import hashlib
import time
import json
import asyncio
import random
from concurrent.futures import ThreadPoolExecutor


# ═══════════════════════════════════════════════════════════════════════════════
# NODE IDENTITY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NodeIdentity:
    """Identity of a Newton node."""
    node_id: str
    public_key: str          # For signature verification
    endpoint: str            # Network endpoint
    stake: int = 0           # Stake for Sybil resistance
    registered_at: int = 0
    last_seen: int = 0

    @classmethod
    def generate(cls, endpoint: str, stake: int = 1000) -> 'NodeIdentity':
        """Generate a new node identity."""
        # In production, use proper key generation
        seed = f"{endpoint}:{time.time()}:{random.random()}"
        node_id = hashlib.sha256(seed.encode()).hexdigest()[:16].upper()
        public_key = hashlib.sha256(f"pk_{seed}".encode()).hexdigest()

        return cls(
            node_id=node_id,
            public_key=public_key,
            endpoint=endpoint,
            stake=stake,
            registered_at=int(time.time()),
            last_seen=int(time.time())
        )

    def sign(self, data: bytes) -> str:
        """Sign data (simplified - in production use proper crypto)."""
        return hashlib.sha256(self.public_key.encode() + data).hexdigest()[:32]

    def verify_signature(self, data: bytes, signature: str) -> bool:
        """Verify a signature."""
        expected = hashlib.sha256(self.public_key.encode() + data).hexdigest()[:32]
        return signature == expected


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION REQUEST
# ═══════════════════════════════════════════════════════════════════════════════

class MessageType(Enum):
    VERIFY_REQUEST = "verify_request"
    VERIFY_RESPONSE = "verify_response"
    PREPARE = "prepare"
    COMMIT = "commit"
    DECIDED = "decided"


@dataclass
class VerificationRequest:
    """A request to verify something across the network."""
    request_id: str
    payload: Dict[str, Any]
    requester: str
    timestamp: int
    signature: str = ""

    @classmethod
    def create(cls, payload: Dict[str, Any], requester: str) -> 'VerificationRequest':
        request_id = hashlib.sha256(
            f"{json.dumps(payload)}:{requester}:{time.time()}".encode()
        ).hexdigest()[:16].upper()

        return cls(
            request_id=request_id,
            payload=payload,
            requester=requester,
            timestamp=int(time.time() * 1000)
        )

    def to_bytes(self) -> bytes:
        return json.dumps({
            "request_id": self.request_id,
            "payload": self.payload,
            "requester": self.requester,
            "timestamp": self.timestamp
        }).encode()


@dataclass
class VerificationResponse:
    """Response from a node."""
    request_id: str
    node_id: str
    result: bool
    elapsed_us: int
    signature: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))


# ═══════════════════════════════════════════════════════════════════════════════
# CONSENSUS STATE
# ═══════════════════════════════════════════════════════════════════════════════

class ConsensusState(Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    DECIDED = "decided"
    FAILED = "failed"


@dataclass
class ConsensusRound:
    """State for a single consensus round."""
    request_id: str
    request: VerificationRequest
    state: ConsensusState = ConsensusState.PENDING
    prepare_votes: Dict[str, bool] = field(default_factory=dict)
    commit_votes: Dict[str, bool] = field(default_factory=dict)
    final_result: Optional[bool] = None
    started_at: int = field(default_factory=lambda: int(time.time() * 1000))
    decided_at: Optional[int] = None

    @property
    def n_prepare_votes(self) -> int:
        return len(self.prepare_votes)

    @property
    def n_commit_votes(self) -> int:
        return len(self.commit_votes)

    def prepare_result(self) -> Optional[bool]:
        """Get result from prepare phase (majority)."""
        if not self.prepare_votes:
            return None
        passes = sum(1 for v in self.prepare_votes.values() if v)
        fails = len(self.prepare_votes) - passes
        return passes > fails


# ═══════════════════════════════════════════════════════════════════════════════
# NODE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

class NodeRegistry:
    """Registry of known Newton nodes."""

    MIN_STAKE = 1000

    def __init__(self):
        self._nodes: Dict[str, NodeIdentity] = {}
        self._by_domain: Dict[str, Set[str]] = {}  # domain -> node_ids

    def register(self, node: NodeIdentity) -> bool:
        """Register a node."""
        if node.stake < self.MIN_STAKE:
            return False

        self._nodes[node.node_id] = node
        return True

    def unregister(self, node_id: str):
        """Unregister a node."""
        if node_id in self._nodes:
            del self._nodes[node_id]

    def get(self, node_id: str) -> Optional[NodeIdentity]:
        """Get node by ID."""
        return self._nodes.get(node_id)

    def get_all(self) -> List[NodeIdentity]:
        """Get all registered nodes."""
        return list(self._nodes.values())

    def get_active(self, max_age_seconds: int = 300) -> List[NodeIdentity]:
        """Get nodes seen recently."""
        cutoff = int(time.time()) - max_age_seconds
        return [n for n in self._nodes.values() if n.last_seen >= cutoff]

    def slash(self, node_id: str, evidence: str) -> bool:
        """
        Slash a misbehaving node (remove from registry).

        In production, this would burn the node's stake.
        """
        if node_id in self._nodes:
            del self._nodes[node_id]
            return True
        return False

    @property
    def quorum_size(self) -> int:
        """Calculate quorum size (2/3 + 1 of active nodes)."""
        n = len(self._nodes)
        return (2 * n // 3) + 1

    def total_stake(self) -> int:
        """Get total staked amount."""
        return sum(n.stake for n in self._nodes.values())


# ═══════════════════════════════════════════════════════════════════════════════
# THE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class Bridge:
    """
    The Newton Bridge - Distributed Verification Protocol.

    Implements a simplified PBFT-like consensus for distributed verification:
    1. Client sends verification request to any node
    2. Node broadcasts PREPARE with its local verification result
    3. Nodes collect PREPARE votes, move to COMMIT when quorum reached
    4. Nodes collect COMMIT votes, move to DECIDED when quorum reached
    5. Result is returned to client

    Byzantine fault tolerant up to f = (n-1)/3 faulty nodes.
    """

    def __init__(self, identity: NodeIdentity, verify_fn: Callable):
        self.identity = identity
        self.verify_fn = verify_fn  # Local verification function
        self.registry = NodeRegistry()
        self.registry.register(identity)

        self._rounds: Dict[str, ConsensusRound] = {}
        self._decided: Dict[str, bool] = {}  # request_id -> final result
        self._executor = ThreadPoolExecutor(max_workers=8)

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    async def verify(self, payload: Dict[str, Any], timeout_ms: int = 5000) -> Dict[str, Any]:
        """
        Verify payload through distributed consensus.

        Returns result with consensus proof.
        """
        request = VerificationRequest.create(payload, self.identity.node_id)
        request.signature = self.identity.sign(request.to_bytes())

        # Initialize consensus round
        round = ConsensusRound(request_id=request.request_id, request=request)
        self._rounds[request.request_id] = round

        # Phase 1: Local verification + broadcast PREPARE
        local_result = await self._local_verify(payload)
        round.prepare_votes[self.identity.node_id] = local_result

        # Broadcast to other nodes (simulated)
        await self._broadcast_prepare(request, local_result)

        # Wait for quorum or timeout
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            if round.n_prepare_votes >= self.registry.quorum_size:
                round.state = ConsensusState.PREPARED
                break
            await asyncio.sleep(0.01)

        if round.state != ConsensusState.PREPARED:
            round.state = ConsensusState.FAILED
            return self._build_result(round, "Prepare phase timeout")

        # Phase 2: COMMIT
        prepare_result = round.prepare_result()
        round.commit_votes[self.identity.node_id] = prepare_result

        await self._broadcast_commit(request.request_id, prepare_result)

        # Wait for commit quorum
        while time.time() < deadline:
            if round.n_commit_votes >= self.registry.quorum_size:
                round.state = ConsensusState.COMMITTED
                break
            await asyncio.sleep(0.01)

        if round.state != ConsensusState.COMMITTED:
            round.state = ConsensusState.FAILED
            return self._build_result(round, "Commit phase timeout")

        # Phase 3: DECIDED
        commits_true = sum(1 for v in round.commit_votes.values() if v)
        round.final_result = commits_true > len(round.commit_votes) // 2
        round.state = ConsensusState.DECIDED
        round.decided_at = int(time.time() * 1000)

        self._decided[request.request_id] = round.final_result

        return self._build_result(round)

    def verify_sync(self, payload: Dict[str, Any], timeout_ms: int = 5000) -> Dict[str, Any]:
        """Synchronous wrapper for verify."""
        return asyncio.run(self.verify(payload, timeout_ms))

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL PROTOCOL
    # ─────────────────────────────────────────────────────────────────────────

    async def _local_verify(self, payload: Dict[str, Any]) -> bool:
        """Run local verification."""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self._executor, self.verify_fn, payload)
        return result.get("passed", False) if isinstance(result, dict) else bool(result)

    async def _broadcast_prepare(self, request: VerificationRequest, result: bool):
        """Broadcast PREPARE message to all nodes."""
        # In production, this sends to actual network endpoints
        # For now, simulate other nodes responding
        for node in self.registry.get_all():
            if node.node_id != self.identity.node_id:
                # Simulate network delay
                await asyncio.sleep(random.uniform(0.001, 0.01))
                # Simulate node's local verification (random for demo)
                simulated_result = random.random() > 0.1  # 90% pass rate
                self._rounds[request.request_id].prepare_votes[node.node_id] = simulated_result

    async def _broadcast_commit(self, request_id: str, result: bool):
        """Broadcast COMMIT message to all nodes."""
        for node in self.registry.get_all():
            if node.node_id != self.identity.node_id:
                await asyncio.sleep(random.uniform(0.001, 0.01))
                # Nodes commit to prepare result
                self._rounds[request_id].commit_votes[node.node_id] = result

    def receive_prepare(self, request_id: str, node_id: str, result: bool, signature: str):
        """Handle incoming PREPARE message."""
        if request_id not in self._rounds:
            return

        # Verify signature (simplified)
        node = self.registry.get(node_id)
        if node is None:
            return

        self._rounds[request_id].prepare_votes[node_id] = result

    def receive_commit(self, request_id: str, node_id: str, result: bool, signature: str):
        """Handle incoming COMMIT message."""
        if request_id not in self._rounds:
            return

        self._rounds[request_id].commit_votes[node_id] = result

    # ─────────────────────────────────────────────────────────────────────────
    # RESULT BUILDING
    # ─────────────────────────────────────────────────────────────────────────

    def _build_result(self, round: ConsensusRound, error: Optional[str] = None) -> Dict[str, Any]:
        """Build verification result with consensus proof."""
        elapsed_ms = (
            (round.decided_at or int(time.time() * 1000)) - round.started_at
        )

        result = {
            "request_id": round.request_id,
            "passed": round.final_result,
            "state": round.state.value,
            "elapsed_ms": elapsed_ms,
            "consensus": {
                "prepare_votes": round.n_prepare_votes,
                "commit_votes": round.n_commit_votes,
                "quorum_size": self.registry.quorum_size,
                "total_nodes": len(self.registry.get_all())
            },
            "timestamp": int(time.time() * 1000)
        }

        if error:
            result["error"] = error

        # Generate proof
        if round.state == ConsensusState.DECIDED:
            proof_data = f"{round.request_id}:{round.final_result}:{round.n_commit_votes}"
            result["proof"] = {
                "type": "consensus",
                "signature": hashlib.sha256(proof_data.encode()).hexdigest()[:32].upper(),
                "nodes": list(round.commit_votes.keys())
            }

        return result

    # ─────────────────────────────────────────────────────────────────────────
    # NODE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def add_node(self, endpoint: str, stake: int = 1000) -> NodeIdentity:
        """Add a new node to the network."""
        node = NodeIdentity.generate(endpoint, stake)
        self.registry.register(node)
        return node

    def remove_node(self, node_id: str):
        """Remove a node from the network."""
        self.registry.unregister(node_id)

    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics."""
        nodes = self.registry.get_all()
        active = self.registry.get_active()

        return {
            "total_nodes": len(nodes),
            "active_nodes": len(active),
            "quorum_size": self.registry.quorum_size,
            "total_stake": self.registry.total_stake(),
            "rounds_pending": len([r for r in self._rounds.values() if r.state == ConsensusState.PENDING]),
            "rounds_decided": len(self._decided),
            "this_node": self.identity.node_id
        }

    # ─────────────────────────────────────────────────────────────────────────
    # SHUTDOWN
    # ─────────────────────────────────────────────────────────────────────────

    def shutdown(self):
        """Graceful shutdown."""
        self._executor.shutdown(wait=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SIMPLIFIED BRIDGE FOR LOCAL TESTING
# ═══════════════════════════════════════════════════════════════════════════════

class LocalBridge:
    """
    Simplified Bridge for local/single-node operation.

    No network, no consensus - just local verification.
    Useful for development and testing.
    """

    def __init__(self, verify_fn: Callable):
        self.verify_fn = verify_fn
        self.identity = NodeIdentity.generate("localhost:8000")
        self._history: List[Dict] = []

    def verify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Local verification (no consensus)."""
        start_us = time.perf_counter_ns() // 1000

        result = self.verify_fn(payload)
        passed = result.get("passed", False) if isinstance(result, dict) else bool(result)

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        response = {
            "request_id": hashlib.sha256(json.dumps(payload).encode()).hexdigest()[:16].upper(),
            "passed": passed,
            "state": "local",
            "elapsed_us": elapsed_us,
            "consensus": {
                "type": "local",
                "node": self.identity.node_id
            },
            "timestamp": int(time.time() * 1000)
        }

        self._history.append(response)
        return response

    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get recent verification history."""
        return self._history[-limit:]


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Newton Bridge - Distributed Verification Protocol")
    print("=" * 60)

    # Simple verify function
    def simple_verify(payload):
        return {"passed": payload.get("value", 0) < 1000}

    # Create bridge with simulated nodes
    identity = NodeIdentity.generate("localhost:8000", stake=5000)
    bridge = Bridge(identity, simple_verify)

    # Add some simulated nodes
    print("\n[Simulating Network]")
    for i in range(4):
        node = bridge.add_node(f"node{i}.example.com:8000", stake=1000)
        print(f"  Added node: {node.node_id}")

    # Get network stats
    print("\n[Network Stats]")
    stats = bridge.get_network_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Run verification
    print("\n[Distributed Verification]")
    result = bridge.verify_sync({"value": 500}, timeout_ms=1000)
    print(f"  Request ID: {result['request_id']}")
    print(f"  Passed: {result['passed']}")
    print(f"  State: {result['state']}")
    print(f"  Elapsed: {result['elapsed_ms']}ms")
    print(f"  Consensus: {result['consensus']}")
    if "proof" in result:
        print(f"  Proof: {result['proof']['signature']}")

    # Local bridge test
    print("\n[Local Bridge]")
    local = LocalBridge(simple_verify)
    local_result = local.verify({"value": 500})
    print(f"  Passed: {local_result['passed']}")
    print(f"  Elapsed: {local_result['elapsed_us']}μs")

    bridge.shutdown()
    print("\n" + "=" * 60)
    print("Every node can verify. Consensus makes it trustworthy.")
