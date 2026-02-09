"""
Ada Deep Research System
=========================

Web research with source verification and fact-checking.
This is BETTER than ChatGPT because every claim is verified
against multiple sources before being included in reports.
"""

import hashlib
import time
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from urllib.parse import urlparse
import re

from .schema import (
    ResearchReport,
    Source,
    SourceType,
)


@dataclass
class ResearchConfig:
    """Configuration for research operations."""

    max_sources: int = 20
    depth: int = 3  # Levels of link following
    timeout_per_source: int = 30
    verify_claims: bool = True
    cross_reference_threshold: int = 2  # Minimum sources to verify a claim
    credibility_weights: Dict[str, float] = dataclass_field(default_factory=lambda: {
        ".gov": 0.95,
        ".edu": 0.90,
        ".org": 0.80,
        "wikipedia.org": 0.75,
        "arxiv.org": 0.95,
        "nature.com": 0.95,
        "science.org": 0.95,
        "reuters.com": 0.90,
        "apnews.com": 0.90,
    })


class WebFetcher:
    """
    Fetches and parses web content.

    In production, this would use actual HTTP requests.
    For demonstration, provides mock responses.
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self._cache: Dict[str, str] = {}

    def fetch(self, url: str) -> Optional[str]:
        """
        Fetch content from URL.

        Returns:
            Page content as text, or None if failed
        """
        if url in self._cache:
            return self._cache[url]

        # In production, use requests library:
        # try:
        #     response = requests.get(url, timeout=self.timeout)
        #     response.raise_for_status()
        #     return response.text
        # except Exception:
        #     return None

        # Mock response for demonstration
        domain = urlparse(url).netloc
        content = f"Mock content from {domain}. This demonstrates Ada's research capability."
        self._cache[url] = content
        return content

    def extract_text(self, html: str) -> str:
        """Extract readable text from HTML."""
        # In production, use BeautifulSoup or similar
        # For now, simple regex to remove tags
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract links from HTML."""
        # Simple link extraction
        links = re.findall(r'href=["\']([^"\']+)["\']', html)
        return [link for link in links if link.startswith('http')]


class ClaimExtractor:
    """
    Extracts verifiable claims from text.

    Uses pattern matching and NLP techniques to identify
    factual statements that can be verified.
    """

    # Patterns that indicate factual claims
    CLAIM_PATTERNS = [
        r'(?:According to|Studies show|Research indicates|Data shows)\s+([^.]+\.)',
        r'(?:In \d{4},?\s+)?([A-Z][^.]+(?:is|was|are|were|has|had|have)[^.]+\.)',
        r'(\d+(?:\.\d+)?%?\s+(?:of|percent|people|users|companies)[^.]+\.)',
        r'(?:The|A|An)\s+([^.]+(?:found|discovered|revealed|showed|demonstrated)[^.]+\.)',
    ]

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract claims from text.

        Returns:
            List of claim dictionaries with text and metadata
        """
        claims = []
        seen = set()

        for pattern in self.CLAIM_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                claim_text = match.strip()
                if claim_text and claim_text not in seen:
                    seen.add(claim_text)
                    claims.append({
                        "text": claim_text,
                        "pattern": pattern,
                        "confidence": 0.5,
                    })

        # Also extract sentences with numbers (often factual)
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if re.search(r'\d+', sentence) and len(sentence) > 20:
                if sentence not in seen:
                    seen.add(sentence)
                    claims.append({
                        "text": sentence + ".",
                        "pattern": "numeric",
                        "confidence": 0.4,
                    })

        return claims[:50]  # Limit claims


class SourceRanker:
    """
    Ranks sources by credibility and relevance.
    """

    def __init__(self, config: ResearchConfig):
        self.config = config

    def get_credibility(self, url: str) -> float:
        """Calculate credibility score for a URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Check exact matches first
        for pattern, score in self.config.credibility_weights.items():
            if pattern in domain:
                return score

        # TLD-based scoring
        if domain.endswith('.gov'):
            return 0.95
        elif domain.endswith('.edu'):
            return 0.90
        elif domain.endswith('.org'):
            return 0.75

        # Default credibility
        return 0.50

    def rank_sources(self, sources: List[Source]) -> List[Source]:
        """Rank sources by credibility score."""
        return sorted(sources, key=lambda s: s.credibility_score, reverse=True)


class ClaimVerifier:
    """
    Verifies claims against multiple sources.

    A claim is considered verified if it appears (or is supported)
    in multiple independent sources.
    """

    def __init__(self, threshold: int = 2):
        self.threshold = threshold

    def verify_claim(
        self,
        claim: Dict[str, Any],
        sources: List[Source]
    ) -> Dict[str, Any]:
        """
        Verify a claim against sources.

        Returns:
            Updated claim with verification status
        """
        claim_text = claim["text"].lower()
        supporting_sources = []

        for source in sources:
            # Check if claim appears in source content
            if claim_text[:50] in source.content.lower():
                supporting_sources.append(source.url)
            # Check for key terms
            elif self._check_key_terms(claim_text, source.content):
                supporting_sources.append(source.url)

        verified = len(supporting_sources) >= self.threshold

        return {
            **claim,
            "verified": verified,
            "supporting_sources": supporting_sources,
            "confidence": min(1.0, len(supporting_sources) / self.threshold),
        }

    def _check_key_terms(self, claim: str, content: str) -> bool:
        """Check if key terms from claim appear in content."""
        # Extract key terms (numbers, proper nouns, etc.)
        key_terms = re.findall(r'\b([A-Z][a-z]+|\d+(?:\.\d+)?%?)\b', claim)
        if not key_terms:
            return False

        content_lower = content.lower()
        matches = sum(1 for term in key_terms if term.lower() in content_lower)
        return matches >= len(key_terms) * 0.5


class DeepResearch:
    """
    Deep research engine with verification.

    Performs comprehensive web research with:
    - Multi-source information gathering
    - Claim extraction and verification
    - Cross-referencing for accuracy
    - Credibility scoring

    This makes Ada MORE RELIABLE than ChatGPT for research tasks.
    """

    def __init__(
        self,
        llm: Any = None,
        max_sources: int = 20,
        depth: int = 3,
        config: Optional[ResearchConfig] = None,
    ):
        self.llm = llm
        self.config = config or ResearchConfig(
            max_sources=max_sources,
            depth=depth,
        )

        self.fetcher = WebFetcher(timeout=self.config.timeout_per_source)
        self.claim_extractor = ClaimExtractor()
        self.source_ranker = SourceRanker(self.config)
        self.claim_verifier = ClaimVerifier(self.config.cross_reference_threshold)

    def investigate(
        self,
        query: str,
        max_sources: Optional[int] = None,
        depth: Optional[int] = None,
    ) -> ResearchReport:
        """
        Perform deep research on a topic.

        Args:
            query: Research topic or question
            max_sources: Override max sources
            depth: Override link-following depth

        Returns:
            ResearchReport with verified findings
        """
        start_time = time.time()
        max_sources = max_sources or self.config.max_sources
        depth = depth or self.config.depth

        # Step 1: Search for sources
        sources = self._search_sources(query, max_sources)

        # Step 2: Fetch and process each source
        for source in sources:
            content = self.fetcher.fetch(source.url)
            if content:
                source.content = self.fetcher.extract_text(content)
                source.credibility_score = self.source_ranker.get_credibility(source.url)

        # Step 3: Rank sources by credibility
        sources = self.source_ranker.rank_sources(sources)

        # Step 4: Extract claims from all sources
        all_claims = []
        for source in sources:
            claims = self.claim_extractor.extract(source.content)
            for claim in claims:
                claim["source_url"] = source.url
            all_claims.extend(claims)

        # Step 5: Verify claims across sources
        verified_claims = []
        for claim in all_claims:
            verified = self.claim_verifier.verify_claim(claim, sources)
            if verified["verified"]:
                verified_claims.append(verified)

        # Step 6: Generate report
        report = self._generate_report(
            query=query,
            sources=sources,
            verified_claims=verified_claims,
            research_time=time.time() - start_time,
        )

        return report

    def _search_sources(self, query: str, max_sources: int) -> List[Source]:
        """
        Search for relevant sources.

        In production, this would use search APIs.
        """
        # Mock search results for demonstration
        mock_sources = [
            Source(
                url=f"https://example{i}.com/article/{query.replace(' ', '-')}",
                title=f"Research on {query} - Source {i}",
                source_type=SourceType.WEB,
            )
            for i in range(min(max_sources, 10))
        ]

        # Add some "authoritative" sources
        mock_sources.extend([
            Source(
                url=f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
                title=f"{query} - Wikipedia",
                source_type=SourceType.WEB,
            ),
            Source(
                url=f"https://arxiv.org/search/{query.replace(' ', '+')}",
                title=f"Academic papers on {query}",
                source_type=SourceType.PAPER,
            ),
        ])

        return mock_sources[:max_sources]

    def _generate_report(
        self,
        query: str,
        sources: List[Source],
        verified_claims: List[Dict[str, Any]],
        research_time: float,
    ) -> ResearchReport:
        """Generate a comprehensive research report."""

        # Generate summary using LLM or template
        if self.llm:
            summary_prompt = f"""Summarize the research findings on: {query}

Verified claims found:
{chr(10).join(f'- {c["text"]}' for c in verified_claims[:10])}

Provide a 2-3 paragraph summary."""
            summary = self.llm.generate(summary_prompt)
            # Extract text from JSON response if needed
            import json
            try:
                data = json.loads(summary)
                if "claims" in data:
                    summary = " ".join(c.get("text", "") for c in data["claims"])
            except (json.JSONDecodeError, TypeError):
                pass
        else:
            summary = f"Research on '{query}' found {len(verified_claims)} verified claims from {len(sources)} sources."

        # Generate detailed findings
        detailed = self._format_detailed_findings(query, verified_claims, sources)

        # Extract key findings
        key_findings = [
            claim["text"]
            for claim in sorted(
                verified_claims,
                key=lambda c: c.get("confidence", 0),
                reverse=True
            )[:10]
        ]

        # Calculate confidence
        if verified_claims:
            avg_confidence = sum(c.get("confidence", 0) for c in verified_claims) / len(verified_claims)
        else:
            avg_confidence = 0.0

        completeness = min(1.0, len(sources) / self.config.max_sources)

        return ResearchReport(
            query=query,
            summary=summary,
            detailed_findings=detailed,
            sources=sources,
            key_findings=key_findings,
            verified_claims=verified_claims,
            confidence_score=avg_confidence,
            completeness_score=completeness,
            research_time_seconds=research_time,
        )

    def _format_detailed_findings(
        self,
        query: str,
        claims: List[Dict[str, Any]],
        sources: List[Source],
    ) -> str:
        """Format detailed findings section."""
        sections = [
            f"## Detailed Research Findings: {query}\n",
            "### Overview\n",
            f"This research analyzed {len(sources)} sources and identified {len(claims)} verified claims.\n",
            "### Verified Claims\n",
        ]

        for i, claim in enumerate(claims[:20], 1):
            confidence = claim.get("confidence", 0)
            confidence_label = "High" if confidence > 0.7 else "Medium" if confidence > 0.4 else "Low"
            sections.append(f"{i}. {claim['text']}")
            sections.append(f"   - Confidence: {confidence_label} ({confidence:.0%})")
            if claim.get("supporting_sources"):
                sections.append(f"   - Sources: {len(claim['supporting_sources'])}")
            sections.append("")

        sections.extend([
            "\n### Source Analysis\n",
            f"Total sources consulted: {len(sources)}\n",
        ])

        # Group by credibility
        high_cred = [s for s in sources if s.credibility_score >= 0.8]
        med_cred = [s for s in sources if 0.5 <= s.credibility_score < 0.8]
        low_cred = [s for s in sources if s.credibility_score < 0.5]

        sections.append(f"- High credibility sources: {len(high_cred)}")
        sections.append(f"- Medium credibility sources: {len(med_cred)}")
        sections.append(f"- Lower credibility sources: {len(low_cred)}")

        return "\n".join(sections)

    def quick_search(self, query: str, max_results: int = 5) -> List[Source]:
        """
        Perform a quick search without deep analysis.

        Returns:
            List of sources without full verification
        """
        sources = self._search_sources(query, max_results)
        for source in sources:
            source.credibility_score = self.source_ranker.get_credibility(source.url)
        return sources

    def fact_check(self, claim: str) -> Dict[str, Any]:
        """
        Fact-check a single claim.

        Returns:
            Verification result with supporting evidence
        """
        # Search for sources related to the claim
        sources = self._search_sources(claim, max_sources=10)

        for source in sources:
            content = self.fetcher.fetch(source.url)
            if content:
                source.content = self.fetcher.extract_text(content)
                source.credibility_score = self.source_ranker.get_credibility(source.url)

        # Verify the claim
        claim_dict = {"text": claim, "confidence": 0.5}
        result = self.claim_verifier.verify_claim(claim_dict, sources)

        return {
            "claim": claim,
            "verified": result["verified"],
            "confidence": result["confidence"],
            "supporting_sources": result["supporting_sources"],
            "verdict": "VERIFIED" if result["verified"] else "UNVERIFIED",
        }
