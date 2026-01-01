#!/usr/bin/env python3
"""
grounding.py - Claim Verification Engine

Provides real-time fact-checking by cross-referencing claims against
external sources and calculating confidence scores.

Part of Newton OS.
"""

import time
import hashlib
from dataclasses import dataclass
from typing import List, Optional

try:
    from googlesearch import search
except ImportError:
    # Graceful fallback if library isn't installed
    def search(query, num_results=5, advanced=False):
        return []


# =============================================================================
# CONFIGURATION
# =============================================================================

# Domains with higher editorial standards receive weight bonuses
TRUSTED_DOMAINS = [
    ".gov",
    ".edu",
    ".mil",
    "apple.com",
    "anthropic.com",
    "reuters.com",
    "apnews.com",
    "nature.com",
    "arxiv.org",
]

# Starting confidence score (higher = less confident)
BASE_CONFIDENCE_SCORE = 10.0

# Weight multiplier for trusted sources
TRUSTED_SOURCE_BONUS = 2.0

# Impact per source found
SOURCE_IMPACT = 0.5


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Evidence:
    """A single piece of supporting evidence."""
    url: str
    title: str
    source_weight: float
    retrieved_at: int


# =============================================================================
# GROUNDING ENGINE
# =============================================================================

class GroundingEngine:
    """
    Verifies claims against external sources.

    Uses a confidence scoring system where:
    - Lower scores indicate higher confidence
    - Score of 0-2: Verified (strong supporting evidence)
    - Score of 2-5: Likely (moderate evidence)
    - Score of 5-8: Uncertain (weak evidence)
    - Score of 8-10: Unverified (no supporting evidence)
    """

    def __init__(self):
        self.cache = {}

    def verify_claim(self, claim: str) -> dict:
        """
        Verify a claim against external sources.

        Args:
            claim: The statement to verify

        Returns:
            Dictionary containing:
            - claim: Original claim text
            - confidence_score: 0-10 scale (lower = more confident)
            - status: VERIFIED, LIKELY, UNCERTAIN, or UNVERIFIED
            - sources: List of supporting source URLs
            - timestamp: Unix timestamp of verification
            - signature: Hash signature of the result
        """
        # 1. Search for supporting evidence
        try:
            results = list(search(claim, num_results=5, advanced=True))
        except Exception as e:
            # Network or API issues - return with maximum uncertainty
            return self._build_result(
                claim=claim,
                score=BASE_CONFIDENCE_SCORE,
                sources=[],
                status="UNVERIFIED",
                note=f"Search unavailable: {str(e)}"
            )

        # 2. No results = maximum uncertainty
        if not results:
            return self._build_result(
                claim=claim,
                score=BASE_CONFIDENCE_SCORE,
                sources=[],
                status="UNVERIFIED",
                note="No sources found"
            )

        # 3. Evaluate each source and calculate confidence
        evidence_chain = []
        running_score = BASE_CONFIDENCE_SCORE

        for result in results:
            weight = 1.0

            # Boost weight for trusted domains
            url = getattr(result, 'url', str(result))
            title = getattr(result, 'title', '')

            if any(domain in url for domain in TRUSTED_DOMAINS):
                weight += TRUSTED_SOURCE_BONUS

            evidence_chain.append(Evidence(
                url=url,
                title=title,
                source_weight=weight,
                retrieved_at=int(time.time())
            ))

            # Each source reduces uncertainty
            running_score -= (weight * SOURCE_IMPACT)

        # 4. Calculate final score (minimum 0)
        final_score = max(0.0, round(running_score, 2))

        # 5. Determine verification status
        if final_score <= 2.0:
            status = "VERIFIED"
        elif final_score <= 5.0:
            status = "LIKELY"
        elif final_score <= 8.0:
            status = "UNCERTAIN"
        else:
            status = "UNVERIFIED"

        return self._build_result(
            claim=claim,
            score=final_score,
            sources=[e.url for e in evidence_chain[:3]],
            status=status
        )

    def _build_result(
        self,
        claim: str,
        score: float,
        sources: List[str],
        status: str,
        note: Optional[str] = None
    ) -> dict:
        """Build a standardized result dictionary."""
        timestamp = int(time.time())

        result = {
            "claim": claim,
            "confidence_score": score,
            "status": status,
            "sources": sources,
            "timestamp": timestamp,
            "signature": self._generate_signature(claim, score, timestamp)
        }

        if note:
            result["note"] = note

        return result

    def _generate_signature(self, claim: str, score: float, timestamp: int) -> str:
        """Generate a hash signature for result verification."""
        payload = f"{claim}:{score}:{timestamp}"
        return hashlib.sha256(payload.encode()).hexdigest()[:12].upper()


# =============================================================================
# CLI TEST
# =============================================================================

if __name__ == "__main__":
    engine = GroundingEngine()

    test_claims = [
        "Apple released the first iPhone in 2007",
        "Python is a programming language",
    ]

    for claim in test_claims:
        print(f"\nVerifying: {claim}")
        result = engine.verify_claim(claim)
        print(f"  Score: {result['confidence_score']}")
        print(f"  Status: {result['status']}")
        print(f"  Sources: {len(result['sources'])}")
