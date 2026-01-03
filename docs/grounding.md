# Claim Grounding

**January 3, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Newton's claim grounding engine verifies factual claims against external sources.

## Overview

The `/ground` endpoint:

1. Searches for evidence using Google Search
2. Evaluates source credibility
3. Calculates a confidence score
4. Returns verification status with sources

## How It Works

```
Claim → Search → Evaluate Sources → Calculate Score → Return Status
```

### Confidence Scoring

Newton starts with a base score of 10 (maximum uncertainty) and reduces it based on:

- **Number of sources found** - More sources = lower score
- **Source credibility** - Trusted domains get bonus weight
- **Evidence strength** - Matching content reduces uncertainty

### Trusted Domains

These domains receive higher weight in scoring:

| Domain Type | Examples |
|-------------|----------|
| Government | `.gov`, `.mil` |
| Academic | `.edu` |
| Authoritative | `apple.com`, `anthropic.com` |
| Wire Services | `reuters.com`, `apnews.com` |
| Scientific | `nature.com`, `arxiv.org` |

---

## API Reference

### Request

**POST** `/ground`

```json
{
  "query": "The first iPhone was released on June 29, 2007"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | The claim to verify |

### Response

```json
{
  "query": "The first iPhone was released on June 29, 2007",
  "result": {
    "claim": "The first iPhone was released on June 29, 2007",
    "confidence_score": 0.5,
    "status": "VERIFIED",
    "sources": [
      "https://www.apple.com/newsroom/...",
      "https://en.wikipedia.org/wiki/IPhone_(1st_generation)",
      "https://www.reuters.com/..."
    ],
    "timestamp": 1735689600,
    "signature": "A7B3C8F2E1D4"
  },
  "verified": true
}
```

---

## Confidence Score Scale

| Score | Status | Interpretation |
|-------|--------|----------------|
| 0-2 | **VERIFIED** | Strong supporting evidence from multiple trusted sources |
| 2-5 | **LIKELY** | Moderate evidence; claim appears accurate |
| 5-8 | **UNCERTAIN** | Weak or conflicting evidence |
| 8-10 | **UNVERIFIED** | No supporting evidence found |

---

## Examples

### Verified Claim

```bash
curl -X POST https://api.parcri.net/ground \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "Python was created by Guido van Rossum"}'
```

```json
{
  "query": "Python was created by Guido van Rossum",
  "result": {
    "claim": "Python was created by Guido van Rossum",
    "confidence_score": 0.5,
    "status": "VERIFIED",
    "sources": [
      "https://www.python.org/...",
      "https://en.wikipedia.org/wiki/Guido_van_Rossum"
    ],
    "timestamp": 1735689600,
    "signature": "B8C4D1E2F5A9"
  },
  "verified": true
}
```

### Uncertain Claim

```bash
curl -X POST https://api.parcri.net/ground \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "The average lifespan of a dragon is 500 years"}'
```

```json
{
  "query": "The average lifespan of a dragon is 500 years",
  "result": {
    "claim": "The average lifespan of a dragon is 500 years",
    "confidence_score": 10.0,
    "status": "UNVERIFIED",
    "sources": [],
    "timestamp": 1735689600,
    "signature": "C9D5E2F6A8B0",
    "note": "No sources found"
  },
  "verified": false
}
```

---

## Use Cases

### Fact-Checking AI Outputs

```python
import requests

def verify_ai_claim(claim: str) -> bool:
    """Verify a claim made by an AI model."""
    response = requests.post(
        "https://api.parcri.net/ground",
        json={"query": claim},
        headers={"X-API-Key": "your-api-key"}
    )
    result = response.json()
    return result["result"]["status"] in ["VERIFIED", "LIKELY"]

# Example usage
claim = "The Great Wall of China is visible from space"
if not verify_ai_claim(claim):
    print("Warning: This claim could not be verified")
```

### Content Moderation

```python
def moderate_content(text: str) -> dict:
    """Check content for unverified claims."""
    # Extract claims (simplified)
    claims = extract_claims(text)

    results = []
    for claim in claims:
        response = requests.post(
            "https://api.parcri.net/ground",
            json={"query": claim},
            headers={"X-API-Key": "your-api-key"}
        )
        result = response.json()
        results.append({
            "claim": claim,
            "status": result["result"]["status"],
            "score": result["result"]["confidence_score"]
        })

    return {
        "claims_checked": len(results),
        "verified": sum(1 for r in results if r["status"] == "VERIFIED"),
        "unverified": sum(1 for r in results if r["status"] == "UNVERIFIED"),
        "details": results
    }
```

### News Verification

```python
def verify_news_article(headline: str, key_claims: list) -> dict:
    """Verify claims in a news article."""
    results = {
        "headline": headline,
        "claims": []
    }

    for claim in key_claims:
        response = requests.post(
            "https://api.parcri.net/ground",
            json={"query": claim},
            headers={"X-API-Key": "your-api-key"}
        )
        data = response.json()
        results["claims"].append({
            "text": claim,
            "status": data["result"]["status"],
            "sources": data["result"]["sources"]
        })

    return results
```

---

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Original claim submitted |
| `result.claim` | string | Claim that was verified |
| `result.confidence_score` | float | Score from 0-10 (lower = more confident) |
| `result.status` | string | VERIFIED, LIKELY, UNCERTAIN, or UNVERIFIED |
| `result.sources` | array | URLs of supporting sources (max 3) |
| `result.timestamp` | int | Unix timestamp of verification |
| `result.signature` | string | Cryptographic signature |
| `result.note` | string | Optional note (e.g., error message) |
| `verified` | bool | `true` if status is VERIFIED |

---

## Limitations

1. **Search Availability** - Requires Google Search access
2. **Real-time Data** - Cannot verify claims about events in progress
3. **Subjective Claims** - Cannot verify opinions or predictions
4. **Language** - Best results with English language claims
5. **Rate Limits** - Subject to Google Search rate limits

---

## Error Handling

### Search Unavailable

```json
{
  "query": "Some claim",
  "result": {
    "claim": "Some claim",
    "confidence_score": 10.0,
    "status": "UNVERIFIED",
    "sources": [],
    "timestamp": 1735689600,
    "signature": "D0E6F2A8B4C0",
    "note": "Search unavailable: Connection timeout"
  },
  "verified": false
}
```

When search is unavailable, Newton returns:
- Maximum confidence score (10.0)
- Status: UNVERIFIED
- Note explaining the issue
