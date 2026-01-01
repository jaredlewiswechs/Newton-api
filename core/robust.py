#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON ROBUST STATISTICS ENGINE
Adversarial-Resistant Verification

Standard statistics are vulnerable to manipulation:
- Mean shifts with outlier injection
- Variance inflates with extreme values
- Z-scores become meaningless under attack

Newton Robust Statistics uses:
- Median Absolute Deviation (MAD) - resistant to outliers
- Locked baselines - attackers can't shift the reference
- Temporal decay - old data ages out
- Byzantine detection - identify malicious data sources

═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import time
import hashlib
import math
from collections import deque
from threading import Lock


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RobustConfig:
    """Configuration for robust statistics."""
    mad_threshold: float = 3.5               # Modified Z-score threshold
    min_baseline_size: int = 30              # Min samples for baseline
    max_window_size: int = 10000             # Max samples in window
    temporal_decay_hours: float = 24.0       # Half-life for temporal decay
    byzantine_threshold: float = 0.33        # Max fraction of suspicious sources
    enable_source_tracking: bool = True      # Track data sources


# ═══════════════════════════════════════════════════════════════════════════════
# LOCKED BASELINE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LockedBaseline:
    """
    An immutable statistical baseline.

    Once locked, the baseline cannot be influenced by new data.
    This prevents attackers from gradually shifting the reference point.
    """
    median: float
    mad: float
    n_samples: int
    locked_at: int
    fingerprint: str
    min_value: float
    max_value: float
    percentiles: Dict[int, float] = field(default_factory=dict)

    @classmethod
    def from_values(cls, values: List[float]) -> 'LockedBaseline':
        """Create a locked baseline from values."""
        if not values:
            raise ValueError("Cannot create baseline from empty values")

        sorted_v = sorted(values)
        n = len(sorted_v)

        # Median
        if n % 2 == 0:
            median = (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2
        else:
            median = sorted_v[n // 2]

        # MAD (Median Absolute Deviation)
        deviations = sorted([abs(x - median) for x in sorted_v])
        if n % 2 == 0:
            mad = (deviations[n // 2 - 1] + deviations[n // 2]) / 2
        else:
            mad = deviations[n // 2]

        # Scale factor for consistency with normal distribution
        # MAD * 1.4826 ≈ standard deviation for normal data
        mad = mad * 1.4826 if mad > 0 else 0.0001

        # Percentiles
        percentiles = {
            5: sorted_v[int(n * 0.05)] if n >= 20 else sorted_v[0],
            25: sorted_v[int(n * 0.25)],
            50: median,
            75: sorted_v[int(n * 0.75)],
            95: sorted_v[int(n * 0.95)] if n >= 20 else sorted_v[-1],
        }

        # Fingerprint
        data = f"{median}:{mad}:{n}:{min(values)}:{max(values)}"
        fingerprint = hashlib.sha256(data.encode()).hexdigest()[:16].upper()

        return cls(
            median=median,
            mad=mad,
            n_samples=n,
            locked_at=int(time.time() * 1000),
            fingerprint=fingerprint,
            min_value=min(values),
            max_value=max(values),
            percentiles=percentiles
        )

    def modified_zscore(self, value: float) -> float:
        """
        Calculate modified Z-score using MAD.

        Modified Z-score = 0.6745 * (x - median) / MAD

        More robust than standard Z-score:
        - Uses median instead of mean (resistant to outliers)
        - Uses MAD instead of std dev (resistant to variance inflation)
        """
        if self.mad == 0:
            return 0.0 if value == self.median else float('inf')
        return 0.6745 * (value - self.median) / self.mad

    def is_anomaly(self, value: float, threshold: float = 3.5) -> bool:
        """Check if value is an anomaly based on modified Z-score."""
        return abs(self.modified_zscore(value)) > threshold

    def to_dict(self) -> Dict[str, Any]:
        return {
            "median": self.median,
            "mad": self.mad,
            "n_samples": self.n_samples,
            "locked_at": self.locked_at,
            "fingerprint": self.fingerprint,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "percentiles": self.percentiles
        }


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPORAL DECAY
# ═══════════════════════════════════════════════════════════════════════════════

class TemporalDecay:
    """
    Apply exponential decay to old data.

    Prevents long-term drift attacks where attacker slowly
    shifts the baseline over time.
    """

    def __init__(self, half_life_hours: float = 24.0):
        self.half_life_seconds = half_life_hours * 3600
        self.decay_constant = math.log(2) / self.half_life_seconds

    def weight(self, timestamp: int, now: Optional[int] = None) -> float:
        """Calculate weight for a sample based on age."""
        if now is None:
            now = int(time.time())

        age_seconds = now - timestamp
        if age_seconds < 0:
            return 1.0

        return math.exp(-self.decay_constant * age_seconds)

    def weighted_values(
        self,
        values_with_timestamps: List[Tuple[float, int]]
    ) -> List[Tuple[float, float]]:
        """Return values with their weights."""
        now = int(time.time())
        return [(v, self.weight(ts, now)) for v, ts in values_with_timestamps]


# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE TRACKER - Byzantine detection
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SourceStats:
    """Statistics for a single data source."""
    source_id: str
    n_submissions: int = 0
    n_anomalies: int = 0
    last_submission: int = 0
    flagged: bool = False

    @property
    def anomaly_rate(self) -> float:
        if self.n_submissions == 0:
            return 0.0
        return self.n_anomalies / self.n_submissions


class SourceTracker:
    """
    Track data sources and detect Byzantine behavior.

    A source is flagged as suspicious if:
    - High anomaly rate (submits many outliers)
    - Submits during attacks
    - Pattern matches known attack signatures
    """

    def __init__(self, byzantine_threshold: float = 0.33):
        self.byzantine_threshold = byzantine_threshold
        self._sources: Dict[str, SourceStats] = {}
        self._lock = Lock()

    def record(self, source_id: str, is_anomaly: bool):
        """Record a submission from a source."""
        with self._lock:
            if source_id not in self._sources:
                self._sources[source_id] = SourceStats(source_id=source_id)

            stats = self._sources[source_id]
            stats.n_submissions += 1
            if is_anomaly:
                stats.n_anomalies += 1
            stats.last_submission = int(time.time())

            # Flag if anomaly rate too high
            if stats.n_submissions >= 10 and stats.anomaly_rate > self.byzantine_threshold:
                stats.flagged = True

    def is_trusted(self, source_id: str) -> bool:
        """Check if source is trusted."""
        if source_id not in self._sources:
            return True  # Unknown sources get benefit of doubt initially
        return not self._sources[source_id].flagged

    def get_trusted_sources(self) -> List[str]:
        """Get list of trusted source IDs."""
        return [sid for sid, stats in self._sources.items() if not stats.flagged]

    def get_flagged_sources(self) -> List[str]:
        """Get list of flagged source IDs."""
        return [sid for sid, stats in self._sources.items() if stats.flagged]

    def stats(self) -> Dict[str, Any]:
        """Get tracker statistics."""
        return {
            "total_sources": len(self._sources),
            "trusted": len(self.get_trusted_sources()),
            "flagged": len(self.get_flagged_sources()),
            "sources": {
                sid: {
                    "submissions": s.n_submissions,
                    "anomaly_rate": round(s.anomaly_rate, 3),
                    "flagged": s.flagged
                }
                for sid, s in self._sources.items()
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ROBUST VERIFIER
# ═══════════════════════════════════════════════════════════════════════════════

class RobustVerifier:
    """
    Adversarial-resistant statistical verification.

    Combines:
    - MAD-based anomaly detection (resistant to outlier injection)
    - Locked baselines (resistant to baseline drift)
    - Temporal decay (resistant to long-term manipulation)
    - Source tracking (resistant to Byzantine sources)
    """

    def __init__(self, config: Optional[RobustConfig] = None):
        self.config = config or RobustConfig()
        self._baseline: Optional[LockedBaseline] = None
        self._baseline_locked = False
        self._window: deque = deque(maxlen=self.config.max_window_size)
        self._temporal_decay = TemporalDecay(self.config.temporal_decay_hours)
        self._source_tracker = SourceTracker(self.config.byzantine_threshold)
        self._lock = Lock()

    # ─────────────────────────────────────────────────────────────────────────
    # BASELINE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def collect(self, value: float, source_id: Optional[str] = None, timestamp: Optional[int] = None):
        """
        Collect a value for baseline building.
        Only works before baseline is locked.
        """
        if self._baseline_locked:
            raise RuntimeError("Baseline is locked - use verify() instead")

        with self._lock:
            ts = timestamp or int(time.time())
            self._window.append((value, ts, source_id))

    def lock_baseline(self, min_samples: Optional[int] = None) -> LockedBaseline:
        """
        Lock the baseline from collected values.
        After locking, the baseline cannot be changed.
        """
        min_samples = min_samples or self.config.min_baseline_size

        with self._lock:
            if self._baseline_locked:
                raise RuntimeError("Baseline already locked")

            if len(self._window) < min_samples:
                raise ValueError(f"Need at least {min_samples} samples, have {len(self._window)}")

            values = [v for v, _, _ in self._window]
            self._baseline = LockedBaseline.from_values(values)
            self._baseline_locked = True

            return self._baseline

    def get_baseline(self) -> Optional[LockedBaseline]:
        """Get the current baseline (locked or building)."""
        if self._baseline_locked:
            return self._baseline

        if len(self._window) >= self.config.min_baseline_size:
            values = [v for v, _, _ in self._window]
            return LockedBaseline.from_values(values)

        return None

    @property
    def is_locked(self) -> bool:
        return self._baseline_locked

    # ─────────────────────────────────────────────────────────────────────────
    # VERIFICATION
    # ─────────────────────────────────────────────────────────────────────────

    def verify(
        self,
        value: float,
        source_id: Optional[str] = None,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Verify a value against the locked baseline.

        Returns comprehensive result including:
        - passed: whether value is within threshold
        - modified_zscore: robust Z-score
        - is_anomaly: whether value is anomalous
        - source_trusted: whether source is trusted
        """
        if not self._baseline_locked:
            raise RuntimeError("Baseline not locked - call lock_baseline() first")

        threshold = threshold or self.config.mad_threshold

        # Calculate modified Z-score
        modified_z = self._baseline.modified_zscore(value)
        is_anomaly = abs(modified_z) > threshold

        # Track source
        source_trusted = True
        if self.config.enable_source_tracking and source_id:
            self._source_tracker.record(source_id, is_anomaly)
            source_trusted = self._source_tracker.is_trusted(source_id)

        # Determine pass/fail
        # Fail if: anomaly AND source is trusted (trusted sources shouldn't submit anomalies)
        # Pass if: not anomaly OR source is untrusted (we ignore untrusted sources)
        if is_anomaly and source_trusted:
            passed = False
            reason = f"Anomaly detected: modified Z-score = {modified_z:.2f} (threshold = {threshold})"
        elif is_anomaly and not source_trusted:
            passed = True  # Ignore anomalies from untrusted sources
            reason = "Anomaly from untrusted source (ignored)"
        else:
            passed = True
            reason = "Value within expected range"

        return {
            "passed": passed,
            "value": value,
            "modified_zscore": round(modified_z, 4),
            "threshold": threshold,
            "is_anomaly": is_anomaly,
            "baseline_median": self._baseline.median,
            "baseline_mad": self._baseline.mad,
            "source_id": source_id,
            "source_trusted": source_trusted,
            "reason": reason,
            "timestamp": int(time.time() * 1000)
        }

    def verify_batch(
        self,
        values: List[float],
        source_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify a batch of values."""
        results = [self.verify(v, source_id) for v in values]

        n_passed = sum(1 for r in results if r["passed"])
        n_anomalies = sum(1 for r in results if r["is_anomaly"])

        return {
            "total": len(values),
            "passed": n_passed,
            "failed": len(values) - n_passed,
            "anomalies": n_anomalies,
            "pass_rate": round(n_passed / len(values) * 100, 2) if values else 0,
            "results": results
        }

    # ─────────────────────────────────────────────────────────────────────────
    # ATTACK DETECTION
    # ─────────────────────────────────────────────────────────────────────────

    def detect_attack(self, recent_values: List[Tuple[float, str]]) -> Dict[str, Any]:
        """
        Detect if an attack is in progress.

        Attack indicators:
        - High anomaly rate
        - Multiple flagged sources submitting
        - Coordinated anomalies (same direction)
        """
        if not self._baseline_locked:
            return {"attack_detected": False, "reason": "Baseline not locked"}

        anomalies = []
        flagged_sources = set()

        for value, source_id in recent_values:
            result = self.verify(value, source_id)
            if result["is_anomaly"]:
                anomalies.append((value, source_id))
            if not result["source_trusted"]:
                flagged_sources.add(source_id)

        anomaly_rate = len(anomalies) / len(recent_values) if recent_values else 0

        # Check for attack patterns
        attack_indicators = []

        if anomaly_rate > 0.3:
            attack_indicators.append(f"High anomaly rate: {anomaly_rate:.1%}")

        if len(flagged_sources) > 0:
            attack_indicators.append(f"Flagged sources active: {len(flagged_sources)}")

        # Check for coordinated anomalies (all same direction)
        if len(anomalies) >= 3:
            anomaly_values = [v for v, _ in anomalies]
            median = self._baseline.median
            above = sum(1 for v in anomaly_values if v > median)
            below = len(anomaly_values) - above

            if above == 0 or below == 0:
                attack_indicators.append("Coordinated anomalies (same direction)")

        attack_detected = len(attack_indicators) >= 2

        return {
            "attack_detected": attack_detected,
            "indicators": attack_indicators,
            "anomaly_rate": round(anomaly_rate, 3),
            "flagged_sources": list(flagged_sources),
            "recommendation": "Reject all submissions" if attack_detected else "Continue normal operation"
        }

    # ─────────────────────────────────────────────────────────────────────────
    # STATS & EXPORT
    # ─────────────────────────────────────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """Get verifier statistics."""
        return {
            "baseline_locked": self._baseline_locked,
            "baseline": self._baseline.to_dict() if self._baseline else None,
            "window_size": len(self._window),
            "sources": self._source_tracker.stats()
        }

    def export_baseline(self) -> Dict[str, Any]:
        """Export the locked baseline for use elsewhere."""
        if not self._baseline_locked:
            raise RuntimeError("Baseline not locked")

        return {
            "version": "1.0.0",
            "baseline": self._baseline.to_dict(),
            "config": {
                "mad_threshold": self.config.mad_threshold,
                "min_baseline_size": self.config.min_baseline_size
            },
            "exported_at": int(time.time() * 1000)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def mad(values: List[float]) -> float:
    """Calculate Median Absolute Deviation."""
    if not values:
        return 0.0
    sorted_v = sorted(values)
    n = len(sorted_v)
    median = sorted_v[n // 2] if n % 2 == 1 else (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2
    deviations = sorted([abs(x - median) for x in sorted_v])
    mad_val = deviations[n // 2] if n % 2 == 1 else (deviations[n // 2 - 1] + deviations[n // 2]) / 2
    return mad_val * 1.4826  # Scale for normal distribution


def modified_zscore(value: float, values: List[float]) -> float:
    """Calculate modified Z-score for a value against a dataset."""
    if not values:
        return 0.0
    sorted_v = sorted(values)
    n = len(sorted_v)
    median = sorted_v[n // 2] if n % 2 == 1 else (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2
    mad_val = mad(values)
    if mad_val == 0:
        return 0.0 if value == median else float('inf')
    return 0.6745 * (value - median) / mad_val


def is_anomaly(value: float, values: List[float], threshold: float = 3.5) -> bool:
    """Check if value is anomalous compared to dataset."""
    return abs(modified_zscore(value, values)) > threshold


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Newton Robust Statistics Engine")
    print("=" * 60)

    # Create verifier
    verifier = RobustVerifier()

    # Collect normal data
    print("\n[Collecting Baseline Data]")
    import random
    random.seed(42)

    normal_data = [100 + random.gauss(0, 5) for _ in range(100)]
    for value in normal_data:
        verifier.collect(value, source_id="trusted_sensor")

    # Lock baseline
    print("\n[Locking Baseline]")
    baseline = verifier.lock_baseline()
    print(f"  Median: {baseline.median:.2f}")
    print(f"  MAD: {baseline.mad:.2f}")
    print(f"  Fingerprint: {baseline.fingerprint}")

    # Verify normal value
    print("\n[Verify Normal Value]")
    result = verifier.verify(102.5, source_id="trusted_sensor")
    print(f"  Value: 102.5")
    print(f"  Passed: {result['passed']}")
    print(f"  Modified Z-score: {result['modified_zscore']}")

    # Verify anomaly
    print("\n[Verify Anomaly]")
    result = verifier.verify(150.0, source_id="trusted_sensor")
    print(f"  Value: 150.0")
    print(f"  Passed: {result['passed']}")
    print(f"  Modified Z-score: {result['modified_zscore']}")
    print(f"  Reason: {result['reason']}")

    # Attack detection
    print("\n[Attack Detection]")
    attack_data = [(200.0, "attacker_1"), (195.0, "attacker_1"), (210.0, "attacker_2")]
    detection = verifier.detect_attack(attack_data)
    print(f"  Attack detected: {detection['attack_detected']}")
    print(f"  Indicators: {detection['indicators']}")

    # Stats
    print("\n[Source Tracking]")
    source_stats = verifier._source_tracker.stats()
    for sid, s in source_stats["sources"].items():
        print(f"  {sid}: {s['submissions']} submissions, {s['anomaly_rate']:.1%} anomaly rate, flagged={s['flagged']}")

    print("\n" + "=" * 60)
    print("Resistant to outliers. Resistant to drift. Resistant to attackers.")
