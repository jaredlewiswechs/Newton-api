"""Neo standalone server.

Run:
    pip install -r requirements.txt
    uvicorn server:app --host 0.0.0.0 --port 8789
"""

from pathlib import Path
from html import unescape
from typing import Any, Dict, Optional
from urllib.parse import urlparse
import re

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

APP_DIR = Path(__file__).parent

app = FastAPI(title="Neo", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(APP_DIR)), name="neo-static")


class NeoAnalyzeRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None


def _strip_html(raw_html: str) -> str:
    cleaned = re.sub(r"<script[\s\S]*?</script>", " ", raw_html, flags=re.IGNORECASE)
    cleaned = re.sub(r"<style[\s\S]*?</style>", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = unescape(cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _fetch_article(url: str) -> Dict[str, str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "NeoStandalone/1.0"})
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {exc}")

    html = response.text
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    title = re.sub(r"\s+", " ", unescape(title_match.group(1))).strip() if title_match else "Untitled Article"

    text = _strip_html(html)
    if len(text) < 120:
        raise HTTPException(status_code=422, detail="Fetched page did not contain enough readable article text")

    return {"title": title, "text": text[:16000]}


def _summarize_text(title: str, text: str) -> Dict[str, Any]:
    sentence_candidates = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentence_candidates if len(s.strip()) > 45]
    if not sentences:
        sentences = [text[:280]]

    highlights = sentences[: min(3, len(sentences))]
    words = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text.lower())

    stop = {
        "the", "and", "for", "that", "with", "this", "from", "have", "were", "their", "about",
        "after", "into", "they", "will", "would", "there", "which", "when", "what", "where", "while",
        "your", "than", "just", "been", "being", "also", "said", "more", "over", "because", "could",
        "should", "between",
    }

    freq: Dict[str, int] = {}
    for word in words:
        if word in stop:
            continue
        freq[word] = freq.get(word, 0) + 1

    key_terms = [term for term, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:8]]

    sentiment_words = {
        "gain": 1, "growth": 1, "record": 1, "improve": 1, "success": 1, "win": 1,
        "risk": -1, "decline": -1, "loss": -1, "fall": -1, "crisis": -1, "warn": -1,
    }
    sentiment_score = sum(sentiment_words.get(word, 0) for word in words)
    tone = "mixed/neutral"
    if sentiment_score > 2:
        tone = "mostly positive"
    elif sentiment_score < -2:
        tone = "mostly negative"

    lead_terms = ", ".join(key_terms[:3]) if key_terms else "general update"

    return {
        "title": title,
        "summary": " ".join(highlights),
        "highlights": highlights,
        "key_terms": key_terms,
        "word_count": len(words),
        "tone": tone,
        "agent_response": f"Neo briefing: {title}. Key theme: {lead_terms}. Overall tone appears {tone}.",
    }


@app.get("/")
async def serve_index():
    return FileResponse(str(APP_DIR / "index.html"))


@app.get("/health")
async def health():
    return {"ok": True, "service": "neo"}


@app.post("/api/analyze")
async def analyze(request: NeoAnalyzeRequest) -> Dict[str, Any]:
    if not request.url and not request.text:
        raise HTTPException(status_code=400, detail="Provide either url or text")

    source_url = request.url
    title = "Direct Input"
    text = (request.text or "").strip()

    if request.url:
        article = _fetch_article(request.url)
        title = article["title"]
        text = article["text"]

    if len(text) < 120:
        raise HTTPException(status_code=422, detail="Need at least 120 characters of content to summarize")

    analysis = _summarize_text(title, text)
    return {**analysis, "source_url": source_url, "engine": "Neo Standalone 1.0"}
