#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
CYBERDOG UI SERVER — Newton-Verified Internet Suite
═══════════════════════════════════════════════════════════════════════════════

Modern reimagining of Apple's 1996 CyberDog internet suite.

Run: python foghorn/cyberdog_server.py
Then visit: http://localhost:8080

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import asdict

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Import CyberDog/OpenDoc
from foghorn.opendoc import (
    Part, PartType, PartState, CompoundDocument,
    create_document, create_part, embed_part,
    get_document_store, BentoSerializer,
)
from foghorn.cyberdog import (
    CyberDogSuite, CyberDogComponent,
    WebBrowserPart, WebResource,
    EmailClientPart, EmailMessage,
    NewsReaderPart, NewsFeed, NewsItem,
    FTPClientPart,
    AddressBookPart, Contact,
    BookmarksPart, Bookmark,
    create_cyberdog, create_web_browser, create_email_client,
    create_news_reader, create_ftp_client, create_address_book, create_bookmarks,
)


# ═══════════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="CyberDog",
    description="Newton-Verified Internet Suite - OpenDoc Reimagined",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL STATE (in-memory for demo)
# ═══════════════════════════════════════════════════════════════════════════════

# Initialize CyberDog suite
suite = create_cyberdog()
browser = suite.browser
email = suite.email
news = suite.news
ftp = suite.ftp
contacts = suite.address_book
bookmarks = suite.bookmarks

# Pre-populate with demo data
contacts.add_contact("Ada Lovelace", "ada@computing.dev", "555-1815")
contacts.add_contact("Charles Babbage", "charles@engines.io", "555-1791")
contacts.add_contact("Alan Turing", "alan@enigma.uk", "555-1912")

bookmarks.add("https://newton.dev", "Newton - Verified Computing", "Newton")
bookmarks.add("https://github.com", "GitHub", "Development")
bookmarks.add("https://news.ycombinator.com", "Hacker News", "News")

news.subscribe("https://newton.dev/feed.xml", "Newton Updates")
news.subscribe("https://ycombinator.com/rss", "Hacker News")


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class NavigateRequest(BaseModel):
    url: str

class EmailComposeRequest(BaseModel):
    to: List[str]
    subject: str
    body: str

class ContactRequest(BaseModel):
    name: str
    email: str = ""
    phone: str = ""

class BookmarkRequest(BaseModel):
    url: str
    title: str
    folder: str = ""

class FeedRequest(BaseModel):
    url: str
    title: str = ""

class DocumentRequest(BaseModel):
    title: str
    content: str = ""  # Optional initial content for text part

class DocumentUpdateRequest(BaseModel):
    parts: List[Dict[str, Any]] = []

class PartRequest(BaseModel):
    doc_hash: str
    name: str
    part_type: str
    content: Any


# ═══════════════════════════════════════════════════════════════════════════════
# BROWSER ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/browser/navigate")
async def browser_navigate(req: NavigateRequest):
    """Navigate to a URL."""
    resource = browser.navigate(req.url)
    return {
        "success": True,
        "resource": resource.to_dict(),
        "current_url": browser.current_url,
        "history": browser.history,
    }

@app.post("/api/browser/back")
async def browser_back():
    """Go back in history."""
    resource = browser.back()
    return {
        "success": resource is not None,
        "resource": resource.to_dict() if resource else None,
        "current_url": browser.current_url,
    }

@app.post("/api/browser/forward")
async def browser_forward():
    """Go forward in history."""
    resource = browser.forward()
    return {
        "success": resource is not None,
        "resource": resource.to_dict() if resource else None,
        "current_url": browser.current_url,
    }

@app.get("/api/browser/history")
async def browser_history():
    """Get browsing history."""
    return {
        "history": browser.history,
        "current_index": browser.history_index,
        "current_url": browser.current_url,
    }


class ScriptRequest(BaseModel):
    """HyperCard-style script command."""
    script: str


@app.post("/api/browser/script")
async def browser_script(req: ScriptRequest):
    """
    Execute HyperCard-style commands.
    
    Bill Atkinson's vision: One-line commands that feel like conversation.
    
    Examples:
        go to "https://example.com"
        back
        forward
        history
        check changes
        get text
        get hash
        help
    """
    result = browser.execute_script(req.script)
    return {
        "success": result.get("ok", False),
        **result,
        "current_url": browser.current_url,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/email/inbox")
async def email_inbox():
    """Get inbox messages."""
    return {
        "messages": [m.to_dict() for m in email.inbox],
        "count": len(email.inbox),
    }

@app.get("/api/email/drafts")
async def email_drafts():
    """Get draft messages."""
    return {
        "messages": [m.to_dict() for m in email.drafts],
        "count": len(email.drafts),
    }

@app.get("/api/email/sent")
async def email_sent():
    """Get sent messages."""
    return {
        "messages": [m.to_dict() for m in email.sent],
        "count": len(email.sent),
    }

@app.post("/api/email/compose")
async def email_compose(req: EmailComposeRequest):
    """Compose a new email draft."""
    msg = email.compose(req.to, req.subject, req.body)
    return {
        "success": True,
        "message": msg.to_dict(),
        "draft_count": len(email.drafts),
    }

@app.post("/api/email/send/{message_id}")
async def email_send(message_id: str):
    """Send a draft email."""
    success = email.send(message_id)
    return {
        "success": success,
        "sent_count": len(email.sent),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/news/feeds")
async def news_feeds():
    """Get all subscribed feeds."""
    return {
        "feeds": [f.to_dict() for f in news.feeds.values()],
        "count": len(news.feeds),
    }

@app.post("/api/news/subscribe")
async def news_subscribe(req: FeedRequest):
    """Subscribe to a feed."""
    feed = news.subscribe(req.url, req.title)
    return {
        "success": True,
        "feed": feed.to_dict(),
    }

@app.post("/api/news/refresh")
async def news_refresh(feed_id: Optional[str] = None):
    """Refresh feeds to get new items."""
    items = news.refresh(feed_id)
    return {
        "success": True,
        "new_items": [i.to_dict() for i in items],
        "count": len(items),
    }

@app.get("/api/news/unread")
async def news_unread():
    """Get all unread items."""
    unread = news.get_unread()
    return {
        "items": [i.to_dict() for i in unread],
        "count": len(unread),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONTACTS ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/contacts")
async def contacts_list():
    """Get all contacts."""
    return {
        "contacts": [c.to_dict() for c in contacts.contacts.values()],
        "count": len(contacts.contacts),
    }

@app.post("/api/contacts")
async def contacts_add(req: ContactRequest):
    """Add a new contact."""
    contact = contacts.add_contact(req.name, req.email, req.phone)
    return {
        "success": True,
        "contact": contact.to_dict(),
    }

@app.get("/api/contacts/search")
async def contacts_search(q: str = Query(...)):
    """Search contacts."""
    results = contacts.search(q)
    return {
        "results": [c.to_dict() for c in results],
        "count": len(results),
    }

@app.delete("/api/contacts/{contact_id}")
async def contacts_delete(contact_id: str):
    """Delete a contact."""
    success = contacts.delete_contact(contact_id)
    return {"success": success}


# ═══════════════════════════════════════════════════════════════════════════════
# BOOKMARKS ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/bookmarks")
async def bookmarks_list():
    """Get all bookmarks."""
    return {
        "bookmarks": [b.to_dict() for b in bookmarks.bookmarks.values()],
        "folders": list(bookmarks.folders.keys()),
        "count": len(bookmarks.bookmarks),
    }

@app.post("/api/bookmarks")
async def bookmarks_add(req: BookmarkRequest):
    """Add a new bookmark."""
    bm = bookmarks.add(req.url, req.title, req.folder)
    return {
        "success": True,
        "bookmark": bm.to_dict(),
    }

@app.get("/api/bookmarks/search")
async def bookmarks_search(q: str = Query(...)):
    """Search bookmarks."""
    results = bookmarks.search(q)
    return {
        "results": [b.to_dict() for b in results],
        "count": len(results),
    }

@app.get("/api/bookmarks/recent")
async def bookmarks_recent(limit: int = 10):
    """Get recent bookmarks."""
    recent = bookmarks.get_recent(limit)
    return {
        "bookmarks": [b.to_dict() for b in recent],
        "count": len(recent),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENTS (OPENDOC) ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

# In-memory document storage
_documents: Dict[str, CompoundDocument] = {}
_parts: Dict[str, Part] = {}


@app.get("/api/documents")
async def documents_list():
    """Get all documents."""
    store = get_document_store()
    docs = list(_documents.values()) + store.list_all()
    return {
        "documents": [d.to_dict() for d in docs],
        "count": len(docs),
    }

@app.post("/api/documents")
async def documents_create(req: DocumentRequest):
    """Create a new document."""
    doc = create_document(req.title)
    
    # Add initial text part if content provided
    if req.content:
        part = create_part("content", PartType.TEXT, req.content)
        _parts[part.hash] = part
        doc.add_part(part)
    
    _documents[doc.hash] = doc
    return {
        "success": True,
        "document": doc.to_dict(),
    }

@app.get("/api/documents/{doc_hash}")
async def documents_get(doc_hash: str):
    """Get a document by hash."""
    doc = _documents.get(doc_hash) or get_document_store().get(doc_hash)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document": doc.to_dict()}

@app.put("/api/documents/{doc_hash}")
async def documents_update(doc_hash: str, req: DocumentUpdateRequest):
    """Update a document's parts."""
    doc = _documents.get(doc_hash) or get_document_store().get(doc_hash)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Clear existing parts and add new ones
    doc.parts = {}
    for part_data in req.parts:
        try:
            part_type = PartType(part_data.get('type', 'text'))
        except ValueError:
            part_type = PartType.TEXT
        
        part = create_part(
            part_data.get('name', 'part'),
            part_type,
            part_data.get('content', '')
        )
        _parts[part.hash] = part
        doc.add_part(part)
    
    # Verify after update
    doc.verify_all()
    _documents[doc.hash] = doc
    
    return {
        "success": True,
        "document": doc.to_dict(),
    }

@app.post("/api/documents/{doc_hash}/parts")
async def documents_add_part(doc_hash: str, req: PartRequest):
    """Add a part to a document."""
    doc = _documents.get(doc_hash) or get_document_store().get(doc_hash)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        part_type = PartType(req.part_type)
    except ValueError:
        part_type = PartType.TEXT
    
    part = create_part(req.name, part_type, req.content)
    _parts[part.hash] = part
    doc.add_part(part)
    _documents[doc.hash] = doc
    
    return {
        "success": True,
        "part": part.to_dict(),
        "document": doc.to_dict(),
    }

@app.post("/api/documents/{doc_hash}/verify")
async def documents_verify(doc_hash: str):
    """Verify all parts in a document."""
    doc = _documents.get(doc_hash) or get_document_store().get(doc_hash)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    results = doc.verify_all()
    return {
        "success": all(results.values()) if results else True,
        "results": results,
        "document": doc.to_dict(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SUITE STATUS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/status")
async def suite_status():
    """Get CyberDog suite status."""
    return {
        "suite": "CyberDog 2.0",
        "components": {
            "browser": {
                "current_url": browser.current_url,
                "history_count": len(browser.history),
            },
            "email": {
                "inbox_count": len(email.inbox),
                "drafts_count": len(email.drafts),
                "sent_count": len(email.sent),
            },
            "news": {
                "feed_count": len(news.feeds),
                "unread_count": len(news.get_unread()),
            },
            "contacts": {
                "count": len(contacts.contacts),
            },
            "bookmarks": {
                "count": len(bookmarks.bookmarks),
                "folder_count": len(bookmarks.folders),
            },
            "documents": {
                "count": len(_documents),
            },
        },
        "verified": True,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# UI ROUTE
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the CyberDog UI."""
    ui_path = Path(__file__).parent / "cyberdog_ui.html"
    if ui_path.exists():
        return HTMLResponse(content=ui_path.read_text(encoding='utf-8'))
    return HTMLResponse("<h1>CyberDog</h1><p>UI not found</p>")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██████╗  ██████╗  ██████╗           ║
║  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔═══██╗██╔════╝           ║
║  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██║  ██║██║   ██║██║  ███╗          ║
║  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║  ██║██║   ██║██║   ██║          ║
║  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║██████╔╝╚██████╔╝╚██████╔╝          ║
║   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚═════╝           ║
║                                                                               ║
║   Newton-Verified Internet Suite                                              ║
║   OpenDoc Reimagined for 2026                                                 ║
║                                                                               ║
║   Visit: http://localhost:8080                                                ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8080)
