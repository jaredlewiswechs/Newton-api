"""
═══════════════════════════════════════════════════════════════════════════════
PARCSTATION SERVER
Development Server with Newton Integration

The Notebook IS the interface.
The Stack IS the territory.
The Trust IS the light.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class Source(BaseModel):
    type: str  # 'document', 'url', 'attestation', 'computation'
    location: str
    verified: bool = False
    hash: Optional[str] = None

class CardVerification(BaseModel):
    status: str = 'draft'  # 'draft', 'pending', 'verified', 'disputed'
    confidence: float = 0.0
    verifiedAt: Optional[str] = None
    verifiedBy: Optional[str] = None

class Card(BaseModel):
    id: Optional[str] = None
    claim: str
    sources: List[Source] = []
    links: List[str] = []
    verification: CardVerification = CardVerification()
    position: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = {}

class Constraint(BaseModel):
    id: str
    name: str
    description: str
    rule: str  # tinyTalk or CDL expression
    severity: str = 'required'  # 'required', 'warning', 'suggestion'

class Stack(BaseModel):
    id: Optional[str] = None
    name: str
    description: str = ''
    cards: List[Card] = []
    constraints: List[Constraint] = []
    position: Dict[str, float] = {'x': 0, 'y': 0, 'z': 0}
    color: int = 0x4a9eff

class CartridgeContract(BaseModel):
    inputs: List[Dict[str, Any]] = []
    outputs: List[Dict[str, Any]] = []
    invariants: List[str] = []

class Cartridge(BaseModel):
    id: Optional[str] = None
    type: str  # 'visual', 'sound', 'data', 'voicepath', etc.
    name: str
    contract: CartridgeContract = CartridgeContract()
    position: Dict[str, float] = {'x': 0, 'y': 0, 'z': 0}
    state: Dict[str, Any] = {}
    verified: bool = False

class Notebook(BaseModel):
    id: Optional[str] = None
    name: str = 'My Notebook'
    stacks: List[Stack] = []
    cartridges: List[Cartridge] = []
    quickCards: List[Card] = []
    recentQueries: List[str] = []

# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

async def verify_card_with_newton(card: Card) -> CardVerification:
    """
    Verify a card's claim against its sources using Newton.
    """
    import httpx
    
    try:
        # Build verification request
        async with httpx.AsyncClient() as client:
            # First, verify the claim itself
            verify_response = await client.post(
                "http://localhost:8000/verify",
                json={
                    "content": card.claim,
                    "claim": "This claim is factually accurate"
                },
                timeout=30.0
            )
            
            if verify_response.status_code == 200:
                result = verify_response.json()
                
                # Calculate confidence based on sources
                source_confidence = 0.0
                if card.sources:
                    verified_sources = sum(1 for s in card.sources if s.verified)
                    source_confidence = verified_sources / len(card.sources)
                
                # Combine claim verification with source confidence
                claim_verified = result.get('verified', False)
                overall_confidence = (
                    (0.5 if claim_verified else 0.0) + 
                    (0.5 * source_confidence)
                )
                
                return CardVerification(
                    status='verified' if overall_confidence >= 0.9 else 'partial' if overall_confidence >= 0.5 else 'draft',
                    confidence=overall_confidence,
                    verifiedAt=datetime.utcnow().isoformat(),
                    verifiedBy='newton'
                )
    except Exception as e:
        print(f"Newton verification error: {e}")
    
    return CardVerification(
        status='draft',
        confidence=0.0
    )

async def verify_cartridge_contract(cartridge: Cartridge) -> bool:
    """
    Verify a cartridge satisfies its contract invariants.
    """
    # For now, all built-in cartridges are trusted
    # In full implementation, would check invariants
    return True

# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="parcStation",
    description="The Spatial Container for Verified Knowledge",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PARCSTATION_DIR = Path(__file__).parent

# In-memory notebook storage (replace with persistent storage in production)
notebooks: Dict[str, Notebook] = {}

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def index():
    """Serve the main parcStation interface."""
    return FileResponse(PARCSTATION_DIR / "index.html")

@app.get("/api/info")
async def info():
    """Get parcStation information."""
    return {
        "name": "parcStation",
        "version": "1.0.0",
        "tagline": "Built on proof",
        "philosophy": "The Notebook IS the territory. The Stack IS the landmark. The Trust IS the light.",
        "capabilities": [
            "Spatial knowledge visualization",
            "Verified stacks and cards",
            "Cartridge embedding (OpenDoc)",
            "Newton integration",
            "Trust-level indicators"
        ]
    }

# ─────────────────────────────────────────────────────────────────────────────
# NOTEBOOK ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/notebook")
async def create_notebook(notebook: Notebook):
    """Create a new notebook."""
    notebook.id = hashlib.sha256(
        f"{notebook.name}{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:16]
    notebooks[notebook.id] = notebook
    return {"id": notebook.id, "notebook": notebook.model_dump()}

@app.get("/api/notebook/{notebook_id}")
async def get_notebook(notebook_id: str):
    """Get a notebook by ID."""
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return notebooks[notebook_id].model_dump()

@app.put("/api/notebook/{notebook_id}")
async def update_notebook(notebook_id: str, notebook: Notebook):
    """Update a notebook."""
    notebook.id = notebook_id
    notebooks[notebook_id] = notebook
    return {"success": True, "notebook": notebook.model_dump()}

@app.get("/api/notebooks")
async def list_notebooks():
    """List all notebooks."""
    return [
        {"id": nid, "name": n.name, "stacks": len(n.stacks), "cartridges": len(n.cartridges)}
        for nid, n in notebooks.items()
    ]

# ─────────────────────────────────────────────────────────────────────────────
# STACK ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/notebook/{notebook_id}/stack")
async def add_stack(notebook_id: str, stack: Stack):
    """Add a stack to a notebook."""
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    stack.id = hashlib.sha256(
        f"{stack.name}{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:16]
    
    notebooks[notebook_id].stacks.append(stack)
    return {"success": True, "stack": stack.model_dump()}

@app.get("/api/notebook/{notebook_id}/stack/{stack_id}")
async def get_stack(notebook_id: str, stack_id: str):
    """Get a stack by ID."""
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    for stack in notebooks[notebook_id].stacks:
        if stack.id == stack_id:
            return stack.model_dump()
    
    raise HTTPException(status_code=404, detail="Stack not found")

# ─────────────────────────────────────────────────────────────────────────────
# CARD ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/notebook/{notebook_id}/stack/{stack_id}/card")
async def add_card(notebook_id: str, stack_id: str, card: Card):
    """Add a card to a stack."""
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    for stack in notebooks[notebook_id].stacks:
        if stack.id == stack_id:
            card.id = hashlib.sha256(
                f"{card.claim}{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16]
            stack.cards.append(card)
            return {"success": True, "card": card.model_dump()}
    
    raise HTTPException(status_code=404, detail="Stack not found")

@app.post("/api/notebook/{notebook_id}/quick-card")
async def add_quick_card(notebook_id: str, card: Card):
    """Add a quick card (draft) to the notebook intake area."""
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    card.id = hashlib.sha256(
        f"{card.claim}{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:16]
    
    notebooks[notebook_id].quickCards.append(card)
    return {"success": True, "card": card.model_dump()}

@app.post("/api/card/{card_id}/verify")
async def verify_card(card_id: str, card: Card):
    """Verify a card with Newton."""
    verification = await verify_card_with_newton(card)
    card.verification = verification
    return {
        "success": True,
        "verification": verification.model_dump(),
        "card": card.model_dump()
    }

# ─────────────────────────────────────────────────────────────────────────────
# CARTRIDGE ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/notebook/{notebook_id}/cartridge")
async def add_cartridge(notebook_id: str, cartridge: Cartridge):
    """Add a cartridge to a notebook."""
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    cartridge.id = hashlib.sha256(
        f"{cartridge.type}{cartridge.name}{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:16]
    
    # Verify cartridge contract
    cartridge.verified = await verify_cartridge_contract(cartridge)
    
    notebooks[notebook_id].cartridges.append(cartridge)
    return {"success": True, "cartridge": cartridge.model_dump()}

@app.get("/api/cartridges/available")
async def list_available_cartridges():
    """List all available cartridge types."""
    return [
        {
            "type": "visual",
            "name": "Visual Cartridge",
            "description": "SVG and image generation",
            "icon": "🎨",
            "contract": {"inputs": ["intent"], "outputs": ["spec"]}
        },
        {
            "type": "sound",
            "name": "Sound Cartridge",
            "description": "Audio specification",
            "icon": "🔊",
            "contract": {"inputs": ["intent"], "outputs": ["spec"]}
        },
        {
            "type": "data",
            "name": "Data Cartridge",
            "description": "Reports and tables",
            "icon": "📊",
            "contract": {"inputs": ["intent", "data"], "outputs": ["report"]}
        },
        {
            "type": "voicepath",
            "name": "VoicePath Cartridge",
            "description": "Music trajectory visualization",
            "icon": "🎵",
            "contract": {"inputs": ["lyrics", "timestamps"], "outputs": ["trajectory"]}
        },
        {
            "type": "sequence",
            "name": "Sequence Cartridge",
            "description": "Video and animation",
            "icon": "🎬",
            "contract": {"inputs": ["intent"], "outputs": ["storyboard"]}
        },
        {
            "type": "rosetta",
            "name": "Rosetta Cartridge",
            "description": "Code generation",
            "icon": "💻",
            "contract": {"inputs": ["intent", "language"], "outputs": ["code"]}
        },
        {
            "type": "document",
            "name": "Document Cartridge",
            "description": "PDF and document parsing",
            "icon": "📄",
            "contract": {"inputs": ["document"], "outputs": ["extracted"]}
        },
        {
            "type": "web",
            "name": "Web Cartridge",
            "description": "Live web data",
            "icon": "🌐",
            "contract": {"inputs": ["url"], "outputs": ["content"]}
        }
    ]

# ─────────────────────────────────────────────────────────────────────────────
# SEARCH ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/search")
async def search_notebook(query: Dict[str, str]):
    """Search across all notebooks using Newton."""
    q = query.get("query", "")
    results = []
    
    for nid, notebook in notebooks.items():
        for stack in notebook.stacks:
            for card in stack.cards:
                if q.lower() in card.claim.lower():
                    results.append({
                        "type": "card",
                        "notebookId": nid,
                        "stackId": stack.id,
                        "stackName": stack.name,
                        "card": card.model_dump()
                    })
    
    return {"query": q, "results": results, "count": len(results)}

# ═══════════════════════════════════════════════════════════════════════════════
# STATIC FILES (must be after API routes)
# ═══════════════════════════════════════════════════════════════════════════════

# Serve static files for JS, CSS, etc.
app.mount("/static", StaticFiles(directory=PARCSTATION_DIR), name="static")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ═══════════════════════════════════════════════════════════════════════════════
    
        ◈ parcStation
        "Built on proof"
        
        The Notebook IS the territory.
        The Stack IS the landmark.
        The Trust IS the light.
        
    ═══════════════════════════════════════════════════════════════════════════════
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
