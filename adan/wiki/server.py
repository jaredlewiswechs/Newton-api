#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
ADANPEDIA SERVER
Wikipedia-style interface for the Verified Knowledge Base

Import facts from Wikipedia, browse the KB like an encyclopedia.
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import httpx
import re
import sys
import os

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from adan.knowledge_base import (
    get_knowledge_base, 
    COUNTRY_CAPITALS, 
    COUNTRY_POPULATIONS,
    VerifiedFact
)
from adan.knowledge_store import get_knowledge_store, StoredFact

# ═══════════════════════════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Adanpedia",
    description="Wikipedia-style interface for the Verified Knowledge Base",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the shared knowledge store
knowledge_store = get_knowledge_store()


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class WikiImportRequest(BaseModel):
    query: str


class AddFactRequest(BaseModel):
    key: str
    fact: str
    category: str
    source: str
    source_url: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD KB FROM EXISTING DATA
# ═══════════════════════════════════════════════════════════════════════════════

def build_facts_list() -> List[Dict]:
    """Convert all KB data to a list of facts."""
    facts = []
    fact_id = 1
    
    # Country capitals (from static KB)
    for country, capital in COUNTRY_CAPITALS.items():
        facts.append({
            "id": fact_id,
            "key": f"Capital of {country.title()}",
            "fact": f"The capital of {country.title()} is {capital}.",
            "category": "Geography",
            "source": "CIA World Factbook",
            "source_url": "https://www.cia.gov/the-world-factbook/",
            "confidence": 1.0
        })
        fact_id += 1
    
    # Country populations (tuples: population, year)
    for country, pop_data in COUNTRY_POPULATIONS.items():
        if isinstance(pop_data, tuple):
            pop, year = pop_data
        else:
            pop, year = pop_data, 2024
        facts.append({
            "id": fact_id,
            "key": f"Population of {country.title()}",
            "fact": f"The population of {country.title()} is approximately {pop:,} (as of {year}).",
            "category": "Demographics",
            "source": "CIA World Factbook",
            "source_url": "https://www.cia.gov/the-world-factbook/",
            "confidence": 1.0
        })
        fact_id += 1
    
    # Add facts from shared knowledge store (Wikipedia imports, manual adds)
    for stored in knowledge_store.get_all():
        facts.append({
            "id": fact_id,
            "key": stored.key,
            "fact": stored.fact,
            "category": stored.category,
            "source": stored.source,
            "source_url": stored.source_url,
            "confidence": stored.confidence,
            "store_id": stored.id,
            "added_by": stored.added_by
        })
        fact_id += 1
    
    return facts


def get_categories(facts: List[Dict]) -> Dict[str, int]:
    """Count facts per category."""
    cats = {}
    for f in facts:
        cat = f.get("category", "Other")
        cats[cat] = cats.get(cat, 0) + 1
    return dict(sorted(cats.items()))


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the wiki UI."""
    ui_path = Path(__file__).parent / "index.html"
    if ui_path.exists():
        return HTMLResponse(content=ui_path.read_text(encoding='utf-8'))
    return HTMLResponse("<h1>Adanpedia</h1><p>UI not found.</p>")


@app.get("/api/facts")
async def get_facts():
    """Get all facts in the knowledge base."""
    facts = build_facts_list()
    return {
        "facts": facts,
        "categories": get_categories(facts),
        "total": len(facts),
        "store_count": knowledge_store.count()
    }


@app.post("/api/facts")
async def add_fact(request: AddFactRequest):
    """Add a new fact manually to the shared knowledge store."""
    stored = knowledge_store.add(
        key=request.key,
        fact=request.fact,
        category=request.category,
        source=request.source,
        source_url=request.source_url or "#",
        confidence=0.9,
        added_by="manual"
    )
    return {"success": True, "message": "Fact added", "id": stored.id}


@app.post("/api/import/wikipedia")
async def import_from_wikipedia(request: WikiImportRequest):
    """
    Import facts from a Wikipedia article.
    Uses Wikipedia's Action API (more reliable than REST API).
    """
    query = request.query.strip()
    if not query:
        return {"success": False, "error": "No query provided"}
    
    # Use Wikipedia's Action API - more reliable
    # https://en.wikipedia.org/w/api.php
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": query,
        "prop": "extracts|info",
        "exintro": True,
        "explaintext": True,
        "inprop": "url",
        "format": "json",
        "redirects": 1
    }
    
    headers = {
        "User-Agent": "Adanpedia/1.0 (https://github.com/adacomputing/newton; contact@adacomputing.com)"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return {"success": False, "error": f"Article '{query}' not found"}
            
            # Get the first (only) page
            page_id = list(pages.keys())[0]
            if page_id == "-1":
                return {"success": False, "error": f"Article '{query}' not found on Wikipedia"}
            
            page = pages[page_id]
            article_title = page.get("title", query)
            extract = page.get("extract", "")
            page_url = page.get("fullurl", f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}")
            
            if not extract:
                return {"success": False, "error": f"No content found for '{query}'"}
            
            # Determine category
            category = categorize_article(extract, article_title)
            
            # Create facts from the extract
            facts_added = []
            
            # Main summary fact - add to shared store
            if extract:
                knowledge_store.add(
                    key=article_title,
                    fact=extract[:500] + ("..." if len(extract) > 500 else ""),
                    category=category,
                    source="Wikipedia",
                    source_url=page_url,
                    confidence=0.85,
                    added_by="wikipedia"
                )
                facts_added.append(article_title)
            
            # Try to extract specific facts from the summary
            extracted = extract_facts_from_text(article_title, extract, category, page_url)
            for ef in extracted:
                knowledge_store.add(
                    key=ef["key"],
                    fact=ef["fact"],
                    category=ef["category"],
                    source=ef["source"],
                    source_url=ef["source_url"],
                    confidence=ef.get("confidence", 0.85),
                    added_by="wikipedia"
                )
                facts_added.append(ef["key"])
            
            return {
                "success": True,
                "title": article_title,
                "facts_added": len(facts_added),
                "facts": facts_added
            }
            
    except httpx.HTTPError as e:
        return {"success": False, "error": f"HTTP error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def categorize_article(description: str, title: str) -> str:
    """Guess category from Wikipedia description."""
    desc_lower = (description or "").lower()
    title_lower = title.lower()
    
    if any(w in desc_lower for w in ["country", "nation", "city", "capital", "island", "continent"]):
        return "Geography"
    if any(w in desc_lower for w in ["physicist", "physics", "particle", "quantum"]):
        return "Physics"
    if any(w in desc_lower for w in ["mathematician", "mathematics", "theorem", "equation"]):
        return "Mathematics"
    if any(w in desc_lower for w in ["programming", "software", "computer", "language", "developer"]):
        return "Programming"
    if any(w in desc_lower for w in ["scientist", "biologist", "chemistry", "chemical"]):
        return "Science"
    if any(w in desc_lower for w in ["politician", "president", "prime minister", "leader"]):
        return "Politics"
    if any(w in desc_lower for w in ["artist", "musician", "actor", "singer", "composer"]):
        return "Arts"
    if any(w in desc_lower for w in ["company", "corporation", "business", "entrepreneur"]):
        return "Business"
    if any(w in desc_lower for w in ["athlete", "player", "sport", "team", "championship"]):
        return "Sports"
    if any(w in desc_lower for w in ["writer", "author", "poet", "novelist"]):
        return "Literature"
    
    return "General"


def extract_facts_from_text(title: str, text: str, category: str, url: str) -> List[Dict]:
    """Extract structured facts from text."""
    facts = []
    
    # Look for birth/death dates
    birth_match = re.search(r"born\s+(\d{1,2}\s+\w+\s+\d{4}|\w+\s+\d{1,2},?\s+\d{4}|\d{4})", text, re.IGNORECASE)
    if birth_match:
        facts.append({
            "key": f"Birth date of {title}",
            "fact": f"{title} was born on {birth_match.group(1)}.",
            "category": category,
            "source": "Wikipedia",
            "source_url": url,
            "confidence": 0.85
        })
    
    death_match = re.search(r"died\s+(\d{1,2}\s+\w+\s+\d{4}|\w+\s+\d{1,2},?\s+\d{4}|\d{4})", text, re.IGNORECASE)
    if death_match:
        facts.append({
            "key": f"Death date of {title}",
            "fact": f"{title} died on {death_match.group(1)}.",
            "category": category,
            "source": "Wikipedia",
            "source_url": url,
            "confidence": 0.85
        })
    
    # Look for "is a/an" definitions
    is_a_match = re.search(rf"{re.escape(title)}\s+(?:is|was)\s+(?:a|an|the)\s+([^.]+)", text, re.IGNORECASE)
    if is_a_match:
        definition = is_a_match.group(1).strip()
        if len(definition) > 10 and len(definition) < 200:
            facts.append({
                "key": f"What is {title}",
                "fact": f"{title} is {definition}.",
                "category": category,
                "source": "Wikipedia",
                "source_url": url,
                "confidence": 0.85
            })
    
    return facts


@app.get("/health")
async def health():
    """Health check."""
    facts = build_facts_list()
    return {
        "status": "healthy",
        "service": "Adanpedia",
        "facts_count": len(facts),
        "categories_count": len(get_categories(facts))
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    port = 8085
    
    print(f"""
═══════════════════════════════════════════════════════════════════════════════
ADANPEDIA
The Verified Encyclopedia

Browse the knowledge base like Wikipedia.
Import facts from Wikipedia with source attribution.

Starting on http://localhost:{port}
═══════════════════════════════════════════════════════════════════════════════
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=port)
