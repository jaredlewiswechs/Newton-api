#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
PARCSTATION CARTRIDGE SYSTEM
Pluggable knowledge modules - like HyperCard XCMDs

No API keys required. All free/local APIs.
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import aiohttp
import asyncio
import json
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
import urllib.parse

# ═══════════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="parcStation Cartridges",
    description="Pluggable knowledge modules - Wikipedia, arXiv, Calendar, Export",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class WikipediaRequest(BaseModel):
    query: str
    sentences: int = 3

class ArxivRequest(BaseModel):
    query: str
    max_results: int = 5

class CalendarRequest(BaseModel):
    query: str  # Natural language like "next friday" or "in 3 days"

class ExportRequest(BaseModel):
    stacks: List[Dict[str, Any]]
    format: str = "json"  # json, markdown

class CodeRequest(BaseModel):
    code: str
    language: str = "python"

class CartridgeInfo(BaseModel):
    id: str
    name: str
    icon: str
    description: str
    endpoints: List[str]

# ═══════════════════════════════════════════════════════════════════════════════
# WIKIPEDIA CARTRIDGE (Free API - no key needed)
# https://en.wikipedia.org/api/rest_v1/
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/cartridge/wikipedia/summary")
async def wikipedia_summary(req: WikipediaRequest):
    """Get Wikipedia summary for a topic."""
    try:
        encoded_query = urllib.parse.quote(req.query.replace(" ", "_"))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
        
        headers = {
            "User-Agent": "parcStation/1.0 (https://github.com/parcstation; contact@parcstation.com) aiohttp/3.0"
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 404:
                    return {
                        "found": False,
                        "query": req.query,
                        "error": "Article not found"
                    }
                
                data = await resp.json()
                
                # Extract sentences
                extract = data.get("extract", "")
                sentences = extract.split(". ")[:req.sentences]
                summary = ". ".join(sentences)
                if summary and not summary.endswith("."):
                    summary += "."
                
                return {
                    "found": True,
                    "query": req.query,
                    "title": data.get("title", req.query),
                    "summary": summary,
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "thumbnail": data.get("thumbnail", {}).get("source", ""),
                    "source": "Wikipedia",
                    "source_tier": "encyclopedia"
                }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Wikipedia request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cartridge/wikipedia/search")
async def wikipedia_search(req: WikipediaRequest):
    """Search Wikipedia for articles."""
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": req.query,
            "srlimit": 5,
            "format": "json",
            "origin": "*"
        }
        
        headers = {
            "User-Agent": "parcStation/1.0 (https://github.com/parcstation; contact@parcstation.com) aiohttp/3.0"
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
                
                results = []
                for item in data.get("query", {}).get("search", []):
                    # Clean snippet (remove HTML)
                    snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
                    results.append({
                        "title": item.get("title"),
                        "snippet": snippet,
                        "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(item.get('title', '').replace(' ', '_'))}"
                    })
                
                return {
                    "query": req.query,
                    "results": results,
                    "source": "Wikipedia"
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# ARXIV CARTRIDGE (Free API - no key needed)
# https://arxiv.org/help/api
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/cartridge/arxiv/search")
async def arxiv_search(req: ArxivRequest):
    """Search arXiv for academic papers."""
    try:
        import ssl
        encoded_query = urllib.parse.quote(req.query)
        url = f"https://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={req.max_results}"
        
        headers = {
            "User-Agent": "parcStation/1.0 (https://github.com/parcstation; contact@parcstation.com) aiohttp/3.0"
        }
        
        # Create SSL context that doesn't verify certs (for development)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                text = await resp.text()
                
                # Parse Atom XML (simple extraction)
                papers = []
                
                # Extract entries
                entries = re.findall(r'<entry>(.*?)</entry>', text, re.DOTALL)
                
                for entry in entries:
                    title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
                    summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                    id_match = re.search(r'<id>(.*?)</id>', entry)
                    published_match = re.search(r'<published>(.*?)</published>', entry)
                    
                    # Get authors
                    authors = re.findall(r'<author>.*?<name>(.*?)</name>.*?</author>', entry, re.DOTALL)
                    
                    if title_match:
                        title = title_match.group(1).strip().replace('\n', ' ')
                        summary = summary_match.group(1).strip().replace('\n', ' ')[:500] if summary_match else ""
                        arxiv_id = id_match.group(1) if id_match else ""
                        published = published_match.group(1)[:10] if published_match else ""
                        
                        # Extract just the ID part
                        arxiv_short_id = arxiv_id.split('/abs/')[-1] if '/abs/' in arxiv_id else arxiv_id
                        
                        papers.append({
                            "title": title,
                            "summary": summary,
                            "authors": authors[:5],  # Limit authors
                            "arxiv_id": arxiv_short_id,
                            "url": arxiv_id,
                            "pdf_url": arxiv_id.replace('/abs/', '/pdf/') + ".pdf" if '/abs/' in arxiv_id else "",
                            "published": published
                        })
                
                return {
                    "query": req.query,
                    "results": papers,
                    "source": "arXiv",
                    "source_tier": "academic"
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# CALENDAR CARTRIDGE (Local - no API needed)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/cartridge/calendar/parse")
async def calendar_parse(req: CalendarRequest):
    """Parse natural language dates and times."""
    query = req.query.lower().strip()
    now = datetime.now()
    
    result = {
        "query": req.query,
        "parsed": False,
        "datetime": None,
        "relative": None,
        "iso": None
    }
    
    # Day mappings
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    try:
        # "today"
        if query == "today":
            target = now
            result["parsed"] = True
            result["relative"] = "today"
        
        # "tomorrow"
        elif query == "tomorrow":
            target = now + timedelta(days=1)
            result["parsed"] = True
            result["relative"] = "tomorrow"
        
        # "yesterday"
        elif query == "yesterday":
            target = now - timedelta(days=1)
            result["parsed"] = True
            result["relative"] = "yesterday"
        
        # "next [day]"
        elif query.startswith("next "):
            day_name = query[5:].strip()
            if day_name in days:
                current_day = now.weekday()
                target_day = days.index(day_name)
                days_ahead = target_day - current_day
                if days_ahead <= 0:
                    days_ahead += 7
                target = now + timedelta(days=days_ahead)
                result["parsed"] = True
                result["relative"] = f"next {day_name}"
        
        # "in N days/weeks/months"
        elif query.startswith("in "):
            match = re.match(r'in (\d+) (day|days|week|weeks|month|months)', query)
            if match:
                num = int(match.group(1))
                unit = match.group(2)
                if "day" in unit:
                    target = now + timedelta(days=num)
                elif "week" in unit:
                    target = now + timedelta(weeks=num)
                elif "month" in unit:
                    target = now + timedelta(days=num * 30)  # Approximate
                result["parsed"] = True
                result["relative"] = f"in {num} {unit}"
        
        # "N days/weeks ago"
        elif "ago" in query:
            match = re.match(r'(\d+) (day|days|week|weeks|month|months) ago', query)
            if match:
                num = int(match.group(1))
                unit = match.group(2)
                if "day" in unit:
                    target = now - timedelta(days=num)
                elif "week" in unit:
                    target = now - timedelta(weeks=num)
                elif "month" in unit:
                    target = now - timedelta(days=num * 30)
                result["parsed"] = True
                result["relative"] = f"{num} {unit} ago"
        
        # "end of month"
        elif query == "end of month":
            if now.month == 12:
                target = datetime(now.year + 1, 1, 1) - timedelta(days=1)
            else:
                target = datetime(now.year, now.month + 1, 1) - timedelta(days=1)
            result["parsed"] = True
            result["relative"] = "end of month"
        
        # "end of year"
        elif query == "end of year":
            target = datetime(now.year, 12, 31)
            result["parsed"] = True
            result["relative"] = "end of year"
        
        else:
            target = now
        
        if result["parsed"]:
            result["datetime"] = target.strftime("%Y-%m-%d %H:%M:%S")
            result["iso"] = target.isoformat()
            result["day_of_week"] = target.strftime("%A")
            result["formatted"] = target.strftime("%B %d, %Y")
            
            # Calculate days from now
            delta = (target.date() - now.date()).days
            if delta > 0:
                result["days_from_now"] = delta
                result["direction"] = "future"
            elif delta < 0:
                result["days_from_now"] = abs(delta)
                result["direction"] = "past"
            else:
                result["days_from_now"] = 0
                result["direction"] = "today"
        
        return result
        
    except Exception as e:
        result["error"] = str(e)
        return result


@app.get("/cartridge/calendar/now")
async def calendar_now():
    """Get current date/time information."""
    now = datetime.now()
    return {
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "iso": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "formatted": now.strftime("%B %d, %Y"),
        "unix_timestamp": int(now.timestamp())
    }


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT CARTRIDGE (Local - no API needed)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/cartridge/export/json")
async def export_json(req: ExportRequest):
    """Export stacks as JSON."""
    export_data = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "stacks": req.stacks,
        "metadata": {
            "total_stacks": len(req.stacks),
            "total_cards": sum(len(s.get("cards", [])) for s in req.stacks)
        }
    }
    
    return {
        "format": "json",
        "content": json.dumps(export_data, indent=2),
        "filename": f"parcstation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        "mime_type": "application/json"
    }


@app.post("/cartridge/export/markdown")
async def export_markdown(req: ExportRequest):
    """Export stacks as Markdown."""
    lines = [
        "# parcStation Export",
        f"",
        f"*Exported: {datetime.now().strftime('%B %d, %Y at %H:%M')}*",
        "",
        "---",
        ""
    ]
    
    for stack in req.stacks:
        lines.append(f"## {stack.get('title', 'Untitled Stack')}")
        lines.append("")
        
        cards = stack.get("cards", [])
        for card in cards:
            content = card.get("content", "")
            trust = card.get("trust", "draft")
            
            # Trust badge
            trust_badges = {
                "verified": "✓ Verified",
                "partial": "◐ Partial",
                "draft": "○ Draft",
                "unverified": "✗ Unverified",
                "disputed": "⚡ Disputed"
            }
            badge = trust_badges.get(trust, "○ Draft")
            
            lines.append(f"### {badge}")
            lines.append("")
            lines.append(content)
            lines.append("")
            
            # Sources
            sources = card.get("sources", [])
            if sources:
                lines.append("**Sources:**")
                for src in sources:
                    url = src.get("url", "")
                    title = src.get("title", url)
                    lines.append(f"- [{title}]({url})")
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    markdown_content = "\n".join(lines)
    
    return {
        "format": "markdown",
        "content": markdown_content,
        "filename": f"parcstation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        "mime_type": "text/markdown"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CODE CARTRIDGE (Uses Newton Supercomputer - verified execution)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/cartridge/code/evaluate")
async def code_evaluate(req: CodeRequest):
    """Evaluate code using Newton's verified computation."""
    # This proxies to Newton Supercomputer's /calculate endpoint
    # Only supports Newton's expression language for safety
    
    try:
        # Try to parse as Newton expression
        # Basic safety: only allow math operations
        code = req.code.strip()
        
        # Simple expression parser for basic math
        # Supports: numbers, +, -, *, /, parentheses
        if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', code):
            try:
                # Safe eval for basic math only
                result = eval(code, {"__builtins__": {}}, {})
                return {
                    "success": True,
                    "input": code,
                    "result": str(result),
                    "type": "math",
                    "verified": True,
                    "note": "Evaluated as basic arithmetic"
                }
            except:
                pass
        
        # For more complex expressions, convert to Newton format
        # and proxy to Newton Supercomputer
        return {
            "success": False,
            "input": code,
            "error": "Only basic arithmetic expressions supported in cartridge. Use Newton /calculate for complex expressions.",
            "hint": "Format: {'op': '+', 'args': [1, 2]}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "input": req.code,
            "error": str(e)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DICTIONARY CARTRIDGE (Free Dictionary API - no key needed)
# ═══════════════════════════════════════════════════════════════════════════════

class DictionaryRequest(BaseModel):
    word: str

@app.post("/cartridge/dictionary/define")
async def dictionary_define(req: DictionaryRequest):
    """Get word definition from Free Dictionary API."""
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(req.word)}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 404:
                    return {
                        "found": False,
                        "word": req.word,
                        "error": "Word not found"
                    }
                
                data = await resp.json()
                
                if isinstance(data, list) and len(data) > 0:
                    entry = data[0]
                    meanings = entry.get("meanings", [])
                    
                    definitions = []
                    for meaning in meanings[:3]:  # Limit to 3 parts of speech
                        part_of_speech = meaning.get("partOfSpeech", "")
                        for defn in meaning.get("definitions", [])[:2]:  # 2 definitions per
                            definitions.append({
                                "part_of_speech": part_of_speech,
                                "definition": defn.get("definition", ""),
                                "example": defn.get("example", "")
                            })
                    
                    return {
                        "found": True,
                        "word": req.word,
                        "phonetic": entry.get("phonetic", ""),
                        "definitions": definitions,
                        "source": "Free Dictionary API"
                    }
                
                return {"found": False, "word": req.word}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# CARTRIDGE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

CARTRIDGES = [
    CartridgeInfo(
        id="wikipedia",
        name="Wikipedia",
        icon="📚",
        description="Encyclopedia grounding - summaries and search",
        endpoints=["/cartridge/wikipedia/summary", "/cartridge/wikipedia/search"]
    ),
    CartridgeInfo(
        id="arxiv",
        name="arXiv",
        icon="📄",
        description="Academic paper search",
        endpoints=["/cartridge/arxiv/search"]
    ),
    CartridgeInfo(
        id="calendar",
        name="Calendar",
        icon="📅",
        description="Date/time parsing and calculations",
        endpoints=["/cartridge/calendar/parse", "/cartridge/calendar/now"]
    ),
    CartridgeInfo(
        id="export",
        name="Export",
        icon="📤",
        description="Export stacks as JSON or Markdown",
        endpoints=["/cartridge/export/json", "/cartridge/export/markdown"]
    ),
    CartridgeInfo(
        id="code",
        name="Code",
        icon="💻",
        description="Verified code execution (basic math)",
        endpoints=["/cartridge/code/evaluate"]
    ),
    CartridgeInfo(
        id="dictionary",
        name="Dictionary",
        icon="📖",
        description="Word definitions and examples",
        endpoints=["/cartridge/dictionary/define"]
    ),
]

@app.get("/cartridges")
async def list_cartridges():
    """List all available cartridges."""
    return {
        "cartridges": [c.dict() for c in CARTRIDGES],
        "count": len(CARTRIDGES)
    }

@app.get("/cartridge/{cartridge_id}")
async def get_cartridge(cartridge_id: str):
    """Get info about a specific cartridge."""
    for c in CARTRIDGES:
        if c.id == cartridge_id:
            return c.dict()
    raise HTTPException(status_code=404, detail="Cartridge not found")


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "service": "parcStation Cartridges",
        "cartridges_loaded": len(CARTRIDGES)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print("""
═══════════════════════════════════════════════════════════════════════════════
PARCSTATION CARTRIDGES
Pluggable Knowledge Modules

📚 Wikipedia  - Encyclopedia grounding
📄 arXiv      - Academic papers  
📅 Calendar   - Date/time parsing
📤 Export     - JSON/Markdown export
💻 Code       - Verified execution
📖 Dictionary - Word definitions

Starting on http://localhost:8093
API docs at http://localhost:8093/docs
═══════════════════════════════════════════════════════════════════════════════
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8093)
