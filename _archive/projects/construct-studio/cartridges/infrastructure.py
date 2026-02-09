"""
Infrastructure Cartridge for Construct Studio
=============================================

No rollback needed. No outage caused.
No "who approved this?" meeting.

This cartridge provides constraint-first governance for:
- Cloud resource quotas
- Deployment limits
- Cluster capacity
- Resource allocation

The invalid deployment cannot exist.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

try:
    from ..core import Matter, Floor, Construct, Force, attempt, ConstructError
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core import Matter, Floor, Construct, Force, attempt, ConstructError


# ============================================================================
# FLOOR DEFINITIONS
# ============================================================================

class DeploymentQuota(Floor):
    """
    Cloud deployment quotas.

    These are hard limits - the deployment that exceeds them
    simply cannot be created.

    Usage:
        quota = DeploymentQuota()
        cpu_request = Matter(128, "vCPU")
        cpu_request >> quota._capacities["cpu"]  # Dies if > 64
    """
    cpu = Matter(64, "vCPU")
    memory = Matter(256, "GB")
    storage = Matter(1000, "GB")
    pods = Matter(100, "pods")


class ResourcePool(Floor):
    """
    A shared resource pool for a team/namespace.

    Multiple services draw from the same pool.
    First come, first served - but constrained.
    """
    cpu = Matter(128, "vCPU")
    memory = Matter(512, "GB")
    gpu = Matter(4, "GPU")


class ClusterLimits(Floor):
    """
    Cluster-wide hard limits.

    These protect the cluster from resource exhaustion.
    """
    total_cpu = Matter(1000, "vCPU")
    total_memory = Matter(4000, "GB")
    total_pods = Matter(5000, "pods")
    namespaces = Matter(100, "namespaces")


class NetworkQuota(Floor):
    """
    Network resource quotas.
    """
    load_balancers = Matter(10, "lb")
    ingresses = Matter(50, "ingress")
    services = Matter(200, "services")
    bandwidth = Matter(10, "Gbps")


# ============================================================================
# MATTER FACTORIES
# ============================================================================

def vcpu(count: float, label: Optional[str] = None) -> Matter:
    """Create vCPU Matter."""
    return Matter(count, "vCPU", label)


def memory_gb(amount: float, label: Optional[str] = None) -> Matter:
    """Create memory Matter in GB."""
    return Matter(amount, "GB", label)


def storage_gb(amount: float, label: Optional[str] = None) -> Matter:
    """Create storage Matter in GB."""
    return Matter(amount, "GB", label)


def pods(count: int, label: Optional[str] = None) -> Matter:
    """Create pods Matter."""
    return Matter(float(count), "pods", label)


def gpus(count: int, label: Optional[str] = None) -> Matter:
    """Create GPU Matter."""
    return Matter(float(count), "GPU", label)


# ============================================================================
# CONSTRUCT FUNCTIONS
# ============================================================================

@dataclass
class DeploymentSpec:
    """Specification for a deployment."""
    name: str
    cpu: float
    memory: float
    replicas: int = 1
    gpu: float = 0
    storage: float = 0

    @property
    def total_cpu(self) -> float:
        return self.cpu * self.replicas

    @property
    def total_memory(self) -> float:
        return self.memory * self.replicas


@Construct(floor=DeploymentQuota, strict=True)
def deploy(spec: DeploymentSpec) -> Dict[str, Any]:
    """
    Deploy a service to the cluster.

    The deployment either fits completely or doesn't exist.
    There is no partial deployment. There is no "pending" state.

    Args:
        spec: The deployment specification

    Returns:
        Dict with deployment details if successful

    Raises:
        OntologicalDeath: If deployment exceeds quotas
    """
    quota = DeploymentQuota._instances.get("DeploymentQuota")
    if quota is None:
        quota = DeploymentQuota()

    # Apply force for each resource
    cpu_request = Matter(spec.total_cpu, "vCPU", f"{spec.name}_cpu")
    cpu_request >> quota._capacities["cpu"]

    mem_request = Matter(spec.total_memory, "GB", f"{spec.name}_memory")
    mem_request >> quota._capacities["memory"]

    pod_request = Matter(float(spec.replicas), "pods", f"{spec.name}_pods")
    pod_request >> quota._capacities["pods"]

    if spec.storage > 0:
        storage_request = Matter(spec.storage, "GB", f"{spec.name}_storage")
        storage_request >> quota._capacities["storage"]

    return {
        "status": "deployed",
        "name": spec.name,
        "resources": {
            "cpu": spec.total_cpu,
            "memory": spec.total_memory,
            "replicas": spec.replicas,
        },
        "remaining": {
            "cpu": quota._capacities["cpu"].remaining.value,
            "memory": quota._capacities["memory"].remaining.value,
            "pods": quota._capacities["pods"].remaining.value,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


def allocate(
    cpu: float = 0,
    memory: float = 0,
    storage: float = 0,
    floor: Optional[Floor] = None,
    label: str = ""
) -> Dict[str, Any]:
    """
    Allocate resources from a pool.

    This is the general-purpose allocation function.
    """
    if floor is None:
        floor = DeploymentQuota._instances.get("DeploymentQuota") or DeploymentQuota()

    results = {"allocated": {}, "remaining": {}}

    with attempt() as ctx:
        if cpu > 0 and "cpu" in floor._capacities:
            cpu_matter = Matter(cpu, "vCPU", label)
            result = cpu_matter >> floor._capacities["cpu"]
            if result.success:
                results["allocated"]["cpu"] = cpu
                results["remaining"]["cpu"] = floor._capacities["cpu"].remaining.value
            else:
                raise ConstructError(
                    f"CPU allocation failed: {cpu} vCPU exceeds remaining {floor._capacities['cpu'].remaining.value}",
                    matter=cpu_matter
                )

        if memory > 0 and "memory" in floor._capacities:
            mem_matter = Matter(memory, "GB", label)
            result = mem_matter >> floor._capacities["memory"]
            if result.success:
                results["allocated"]["memory"] = memory
                results["remaining"]["memory"] = floor._capacities["memory"].remaining.value
            else:
                raise ConstructError(
                    f"Memory allocation failed: {memory} GB exceeds remaining",
                    matter=mem_matter
                )

        if storage > 0 and "storage" in floor._capacities:
            store_matter = Matter(storage, "GB", label)
            result = store_matter >> floor._capacities["storage"]
            if result.success:
                results["allocated"]["storage"] = storage
                results["remaining"]["storage"] = floor._capacities["storage"].remaining.value
            else:
                raise ConstructError(
                    f"Storage allocation failed: {storage} GB exceeds remaining",
                    matter=store_matter
                )

    results["status"] = "allocated"
    results["timestamp"] = datetime.utcnow().isoformat()

    return results


# ============================================================================
# SIMULATION HELPERS
# ============================================================================

def simulate_deployments(specs: List[DeploymentSpec]) -> Dict[str, Any]:
    """
    Simulate a series of deployments.

    Returns which would succeed and which would die.
    """
    try:
        from ..ledger import Ledger
    except ImportError:
        from ledger import Ledger

    ledger = Ledger("deploy_simulation")
    quota = DeploymentQuota()  # Fresh quota

    results = {
        "deployments": [],
        "deployed": 0,
        "rejected": 0,
        "total_cpu_used": 0,
        "total_memory_used": 0,
        "remaining": {},
    }

    for spec in specs:
        with attempt():
            # Check each resource
            cpu_ok = spec.total_cpu <= quota._capacities["cpu"].remaining.value
            mem_ok = spec.total_memory <= quota._capacities["memory"].remaining.value
            pods_ok = spec.replicas <= quota._capacities["pods"].remaining.value

            if cpu_ok and mem_ok and pods_ok:
                # Apply forces
                Matter(spec.total_cpu, "vCPU") >> quota._capacities["cpu"]
                Matter(spec.total_memory, "GB") >> quota._capacities["memory"]
                Matter(float(spec.replicas), "pods") >> quota._capacities["pods"]

                results["deployments"].append({
                    "name": spec.name,
                    "status": "deployed",
                    "cpu": spec.total_cpu,
                    "memory": spec.total_memory,
                    "replicas": spec.replicas,
                })
                results["deployed"] += 1
                results["total_cpu_used"] += spec.total_cpu
                results["total_memory_used"] += spec.total_memory
            else:
                reasons = []
                if not cpu_ok:
                    reasons.append(f"CPU: need {spec.total_cpu}, have {quota._capacities['cpu'].remaining.value}")
                if not mem_ok:
                    reasons.append(f"Memory: need {spec.total_memory}, have {quota._capacities['memory'].remaining.value}")
                if not pods_ok:
                    reasons.append(f"Pods: need {spec.replicas}, have {quota._capacities['pods'].remaining.value}")

                results["deployments"].append({
                    "name": spec.name,
                    "status": "rejected",
                    "reasons": reasons,
                })
                results["rejected"] += 1

    results["remaining"] = {
        "cpu": quota._capacities["cpu"].remaining.value,
        "memory": quota._capacities["memory"].remaining.value,
        "pods": quota._capacities["pods"].remaining.value,
    }

    return results


def check_deployment(spec: DeploymentSpec, floor: Optional[Floor] = None) -> Dict[str, Any]:
    """
    Check if a deployment would fit without actually deploying.
    """
    if floor is None:
        floor = DeploymentQuota._instances.get("DeploymentQuota") or DeploymentQuota()

    checks = {}

    for resource, (needed, capacity_name) in [
        ("cpu", (spec.total_cpu, "cpu")),
        ("memory", (spec.total_memory, "memory")),
        ("pods", (float(spec.replicas), "pods")),
    ]:
        if capacity_name in floor._capacities:
            remaining = floor._capacities[capacity_name].remaining.value
            checks[resource] = {
                "needed": needed,
                "remaining": remaining,
                "fits": needed <= remaining,
                "utilization_after": (floor._capacities[capacity_name].current.value + needed) / floor._capacities[capacity_name].maximum.value if needed <= remaining else None,
            }

    all_fit = all(c["fits"] for c in checks.values())

    return {
        "name": spec.name,
        "would_succeed": all_fit,
        "resources": checks,
    }


# ============================================================================
# PRESET SCENARIOS
# ============================================================================

class InfraScenarios:
    """Pre-built scenarios for demos and testing."""

    @staticmethod
    def small_cluster() -> DeploymentQuota:
        """Small development cluster."""
        class SmallCluster(Floor):
            cpu = Matter(16, "vCPU")
            memory = Matter(64, "GB")
            storage = Matter(200, "GB")
            pods = Matter(50, "pods")
        return SmallCluster()

    @staticmethod
    def production_cluster() -> DeploymentQuota:
        """Production cluster with larger limits."""
        class ProdCluster(Floor):
            cpu = Matter(256, "vCPU")
            memory = Matter(1024, "GB")
            storage = Matter(5000, "GB")
            pods = Matter(500, "pods")
        return ProdCluster()

    @staticmethod
    def gpu_cluster() -> ResourcePool:
        """GPU-enabled cluster for ML workloads."""
        class GPUCluster(Floor):
            cpu = Matter(64, "vCPU")
            memory = Matter(512, "GB")
            gpu = Matter(8, "GPU")
        return GPUCluster()

    @staticmethod
    def sample_deployments() -> List[DeploymentSpec]:
        """Sample deployment specs for testing."""
        return [
            DeploymentSpec("api-server", cpu=2, memory=4, replicas=3),
            DeploymentSpec("worker", cpu=4, memory=8, replicas=5),
            DeploymentSpec("cache", cpu=1, memory=16, replicas=2),
            DeploymentSpec("database", cpu=8, memory=32, replicas=1, storage=100),
            DeploymentSpec("ml-model", cpu=16, memory=64, replicas=2, gpu=1),
        ]
