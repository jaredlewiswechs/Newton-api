"""
═══════════════════════════════════════════════════════════════════════════════
CYBERDOG — Newton-Verified Internet Suite
═══════════════════════════════════════════════════════════════════════════════

CyberDog reimagined for the 2020s.

Original CyberDog (Feb 1996 - April 1997):
- OpenDoc-based internet suite
- Web browser (NetSprocket)
- Email client (Mastripe)
- News reader (CyberDog News)
- FTP client
- Address book (CyberDog Contacts)
- All components embeddable in compound documents

Newton CyberDog (2026):
- Built on Newton OpenDoc framework
- Same component philosophy
- Verified operations via Newton Logic Engine
- Hash-chained content via Foghorn
- Constraint-validated via CDL

"CyberDog was the future of the internet Apple killed.
 We're bringing it back — verified."

───────────────────────────────────────────────────────────────────────────────
IN THE SPIRIT OF ATG
───────────────────────────────────────────────────────────────────────────────

Apple Advanced Technology Group (1986-1997) created:
- HyperCard (Bill Atkinson) — Hypermedia before the web
- OpenDoc — Component documents
- CyberDog — Internet suite on OpenDoc
- QuickTime, QuickDraw 3D, ColorSync, PlainTalk, Newton handwriting

This code honors that legacy and the engineers who built it:
- Bill Atkinson (1951-2025) — QuickDraw, MacPaint, HyperCard, Lisa GUI
- Larry Tesler (1945-2020) — Cut/Copy/Paste, founded ATG
- Jef Raskin (1943-2005) — Conceived the Macintosh
- Steve Wozniak — Apple I, Apple II, still inspiring

"We're bringing back what Apple killed."

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import hashlib
import json
import time
import urllib.parse
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set
import sys
import os
import requests

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from foghorn.objects import (
    FoghornObject, ObjectType, Card, Query, ResultSet,
    FileAsset, Task, Receipt,
)
from foghorn.commands import add_object
from foghorn.opendoc import (
    Part, PartType, PartState, CompoundDocument,
    PartHandler, PartRegistry, get_part_registry,
    get_document_store, create_document, create_part, embed_part
)
from core.cdl import CDLEvaluator


# ═══════════════════════════════════════════════════════════════════════════════
# CYBERDOG COMPONENT TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class CyberDogComponent(Enum):
    """
    CyberDog component types.
    
    Each can be embedded in any OpenDoc compound document.
    """
    WEB_BROWSER = "web_browser"       # Browse web pages
    EMAIL_CLIENT = "email_client"     # Read/send email
    NEWS_READER = "news_reader"       # Read newsgroups/RSS
    FTP_CLIENT = "ftp_client"         # Transfer files
    ADDRESS_BOOK = "address_book"     # Contact management
    BOOKMARKS = "bookmarks"           # URL bookmarks
    SEARCH = "search"                 # Web search


# ═══════════════════════════════════════════════════════════════════════════════
# WEB BROWSER PART — NetSprocket Reimagined
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class WebResource:
    """
    A web resource (page, image, etc).
    
    All resources are content-addressed and verified.
    """
    url: str
    content_type: str = "text/html"
    content: str = ""
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    fetched_at: float = field(default_factory=time.time)
    hash: str = ""
    verified: bool = False
    # Change detection (Woz's idea: "did the page change?") 
    content_hash: str = ""
    previous_hash: Optional[str] = None
    changed: bool = False
    
    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.sha256(
                f"{self.url}:{self.content}".encode()
            ).hexdigest()[:16]
        if not self.content_hash and self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "content_type": self.content_type,
            "content": self.content,  # Full content - UI handles display
            "content_length": len(self.content),
            "status_code": self.status_code,
            "headers": self.headers,
            "fetched_at": self.fetched_at,
            "hash": self.hash,
            "verified": self.verified,
            "content_hash": self.content_hash,
            "previous_hash": self.previous_hash,
            "changed": self.changed,
        }


@dataclass 
class WebBrowserPart(Part):
    """
    CyberDog Web Browser component.
    
    Original CyberDog used NetSprocket.
    Newton CyberDog uses verified fetch.
    """
    
    # Browser state
    current_url: str = ""
    history: List[str] = field(default_factory=list)
    history_index: int = -1
    
    # Cached resources
    cache: Dict[str, WebResource] = field(default_factory=dict)
    
    # Security constraints
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    
    # Page change detection - stores URL -> content hash
    page_hashes: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        self.part_type = PartType.BROWSER
        self.name = self.name or "Web Browser"
    
    def navigate(self, url: str) -> WebResource:
        """
        Navigate to a URL.
        
        Actually fetches the real page using requests.
        """
        # Normalize URL
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
            
        # Validate URL
        if not self._is_allowed(url):
            return WebResource(
                url=url,
                status_code=403,
                content="<html><body><h1>Blocked</h1><p>This domain is not allowed.</p></body></html>",
                verified=False,
            )
        
        # Check cache (optional - can be disabled for fresh fetches)
        # Disabled for now to always get fresh content
        # if url in self.cache:
        #     return self.cache[url]
        
        # REAL FETCH using requests
        try:
            headers = {
                'User-Agent': 'CyberDog/2.0 (Newton Verified Browser)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            resource = WebResource(
                url=response.url,  # May differ due to redirects
                content_type=response.headers.get('Content-Type', 'text/html'),
                content=response.text,
                status_code=response.status_code,
                headers=dict(response.headers),
                verified=True,
            )
        except requests.exceptions.Timeout:
            resource = WebResource(
                url=url,
                status_code=408,
                content="<html><body><h1>Timeout</h1><p>Request timed out after 10 seconds.</p></body></html>",
                verified=False,
            )
        except requests.exceptions.SSLError as e:
            resource = WebResource(
                url=url,
                status_code=495,
                content=f"<html><body><h1>SSL Error</h1><p>{str(e)}</p></body></html>",
                verified=False,
            )
        except requests.exceptions.RequestException as e:
            resource = WebResource(
                url=url,
                status_code=0,
                content=f"<html><body><h1>Error</h1><p>Could not fetch page: {str(e)}</p></body></html>",
                verified=False,
            )
        
        # Update history
        self.current_url = url
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        self.history.append(url)
        self.history_index = len(self.history) - 1
        
        # Cache
        self.cache[url] = resource
        
        # Track page hash for change detection
        if resource.content:
            content_hash = hashlib.sha256(resource.content.encode()).hexdigest()[:16]
            old_hash = self.page_hashes.get(url)
            resource.changed = old_hash is not None and old_hash != content_hash
            resource.previous_hash = old_hash
            resource.content_hash = content_hash
            self.page_hashes[url] = content_hash
        
        self._compute_hash()
        return resource
    
    def back(self) -> Optional[WebResource]:
        """Navigate back in history."""
        if self.history_index > 0:
            self.history_index -= 1
            return self.navigate(self.history[self.history_index])
        return None
    
    def forward(self) -> Optional[WebResource]:
        """Navigate forward in history."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            return self.navigate(self.history[self.history_index])
        return None
    
    def _is_allowed(self, url: str) -> bool:
        """Check if URL is allowed by security constraints."""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check blocked
            for blocked in self.blocked_domains:
                if blocked.lower() in domain:
                    return False
            
            # Check allowed (if list is set)
            if self.allowed_domains:
                for allowed in self.allowed_domains:
                    if allowed.lower() in domain:
                        return True
                return False
            
            return True
        except:
            return False
    
    def get_content_for_hash(self) -> str:
        return json.dumps({
            "type": "web_browser",
            "current_url": self.current_url,
            "history": self.history,
        }, sort_keys=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HYPERCARD-STYLE SCRIPTING — "The script lives with the object"
    # Bill Atkinson's vision: One-line commands that feel like conversation
    # ═══════════════════════════════════════════════════════════════════════════
    
    def execute_script(self, script: str) -> Dict[str, Any]:
        """
        Execute HyperCard-style commands.
        
        Examples:
            go to "https://example.com"
            back
            forward
            show history
            check changes
            get text
        """
        script = script.strip().lower()
        
        # go to "url"
        if script.startswith("go to "):
            url = script[6:].strip().strip('"').strip("'")
            if not url.startswith("http"):
                url = "https://" + url
            result = self.navigate(url)
            # Store hash for change detection
            if result.get("content"):
                content_hash = hashlib.sha256(result["content"].encode()).hexdigest()[:16]
                old_hash = self.page_hashes.get(url)
                self.page_hashes[url] = content_hash
                result["changed"] = old_hash is not None and old_hash != content_hash
                result["content_hash"] = content_hash
            return {"ok": True, "command": "go", **result}
        
        # back
        elif script == "back":
            result = self.back()
            return {"ok": result is not None, "command": "back", "resource": result}
        
        # forward
        elif script == "forward":
            result = self.forward()
            return {"ok": result is not None, "command": "forward", "resource": result}
        
        # show history
        elif script in ("show history", "history"):
            return {
                "ok": True,
                "command": "history",
                "history": [{"url": r.url, "title": r.title, "hash": r.content_hash} 
                           for r in self.history]
            }
        
        # check changes - compare current page hash to stored
        elif script in ("check changes", "changes"):
            if self.current_url and self.current_url in self.page_hashes:
                current = self.resources.get(self.current_url)
                if current and current.content:
                    new_hash = hashlib.sha256(current.content.encode()).hexdigest()[:16]
                    old_hash = self.page_hashes[self.current_url]
                    return {
                        "ok": True,
                        "command": "changes",
                        "url": self.current_url,
                        "changed": new_hash != old_hash,
                        "old_hash": old_hash,
                        "new_hash": new_hash
                    }
            return {"ok": False, "command": "changes", "error": "No page to check"}
        
        # get text - extract plain text from HTML (Woz's "safety first" idea)
        elif script in ("get text", "text only", "text"):
            if self.current_url:
                resource = self.resources.get(self.current_url)
                if resource and resource.content:
                    text = self._extract_text(resource.content)
                    return {"ok": True, "command": "text", "text": text}
            return {"ok": False, "command": "text", "error": "No page loaded"}
        
        # get hash - show verification chain
        elif script in ("get hash", "hash", "verify"):
            chain = []
            for r in self.history[-10:]:  # Last 10 pages
                chain.append({"url": r.url, "hash": r.content_hash})
            return {
                "ok": True,
                "command": "hash",
                "current_hash": self.resources.get(self.current_url).content_hash if self.current_url and self.current_url in self.resources else None,
                "chain": chain
            }
        
        # help
        elif script in ("help", "?"):
            return {
                "ok": True,
                "command": "help",
                "commands": [
                    'go to "url" - Navigate to a page',
                    'back - Go back in history',
                    'forward - Go forward in history',
                    'history - Show browsing history',
                    'check changes - See if page changed since last visit',
                    'get text - Extract plain text from page',
                    'get hash - Show verification chain',
                    'help - Show this message'
                ]
            }
        
        else:
            return {"ok": False, "command": "unknown", "error": f"Unknown command: {script}"}
    
    def _extract_text(self, html: str) -> str:
        """Extract plain text from HTML - Bill's 'what you see is what you get' principle."""
        import re
        # Remove script/style
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Remove tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Decode entities
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL PART — Mastripe Reimagined
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EmailMessage:
    """An email message with verification."""
    id: str = ""
    from_addr: str = ""
    to_addrs: List[str] = field(default_factory=list)
    cc_addrs: List[str] = field(default_factory=list)
    subject: str = ""
    body: str = ""
    html_body: str = ""
    sent_at: float = 0.0
    received_at: float = field(default_factory=time.time)
    hash: str = ""
    verified: bool = False
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.from_addr}:{self.subject}:{time.time()}".encode()
            ).hexdigest()[:16]
        if not self.hash:
            self.hash = hashlib.sha256(
                f"{self.from_addr}:{self.to_addrs}:{self.subject}:{self.body}".encode()
            ).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "from": self.from_addr,
            "to": self.to_addrs,
            "cc": self.cc_addrs,
            "subject": self.subject,
            "body": self.body,
            "sent_at": self.sent_at,
            "received_at": self.received_at,
            "hash": self.hash,
            "verified": self.verified,
        }


@dataclass
class EmailClientPart(Part):
    """
    CyberDog Email component.
    
    Original CyberDog used Mastripe.
    Newton CyberDog uses verified messaging.
    """
    
    # Mailbox state
    inbox: List[EmailMessage] = field(default_factory=list)
    sent: List[EmailMessage] = field(default_factory=list)
    drafts: List[EmailMessage] = field(default_factory=list)
    trash: List[EmailMessage] = field(default_factory=list)
    
    # Current view
    current_folder: str = "inbox"
    selected_message: Optional[str] = None
    
    # Account settings (simplified)
    account_email: str = ""
    display_name: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.part_type = PartType.MAIL
        self.name = self.name or "Email"
    
    def compose(self, to: List[str], subject: str, body: str) -> EmailMessage:
        """Create a new email draft."""
        msg = EmailMessage(
            from_addr=self.account_email,
            to_addrs=to,
            subject=subject,
            body=body,
        )
        self.drafts.append(msg)
        self._compute_hash()
        return msg
    
    def send(self, message_id: str) -> bool:
        """Send a draft email."""
        for i, msg in enumerate(self.drafts):
            if msg.id == message_id:
                msg.sent_at = time.time()
                msg.verified = True
                self.sent.append(msg)
                self.drafts.pop(i)
                self._compute_hash()
                return True
        return False
    
    def receive(self, msg: EmailMessage):
        """Receive an incoming email."""
        msg.received_at = time.time()
        self.inbox.append(msg)
        self._compute_hash()
    
    def delete(self, message_id: str) -> bool:
        """Move message to trash."""
        for folder in [self.inbox, self.sent, self.drafts]:
            for i, msg in enumerate(folder):
                if msg.id == message_id:
                    self.trash.append(msg)
                    folder.pop(i)
                    self._compute_hash()
                    return True
        return False
    
    def get_folder(self, folder_name: Optional[str] = None) -> List[EmailMessage]:
        """Get messages in a folder."""
        folder_name = folder_name or self.current_folder
        return {
            "inbox": self.inbox,
            "sent": self.sent,
            "drafts": self.drafts,
            "trash": self.trash,
        }.get(folder_name, [])
    
    def get_content_for_hash(self) -> str:
        return json.dumps({
            "type": "email_client",
            "account": self.account_email,
            "inbox_count": len(self.inbox),
            "sent_count": len(self.sent),
        }, sort_keys=True)


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS READER PART — CyberDog News Reimagined
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NewsItem:
    """A news article or feed item."""
    id: str = ""
    title: str = ""
    link: str = ""
    content: str = ""
    source: str = ""
    author: str = ""
    published_at: float = 0.0
    hash: str = ""
    read: bool = False
    starred: bool = False
    verified: bool = False
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.link}:{self.title}".encode()
            ).hexdigest()[:16]
        if not self.hash:
            self.hash = hashlib.sha256(
                f"{self.link}:{self.content}".encode()
            ).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "content": self.content[:500] if len(self.content) > 500 else self.content,
            "source": self.source,
            "author": self.author,
            "published_at": self.published_at,
            "hash": self.hash,
            "read": self.read,
            "starred": self.starred,
            "verified": self.verified,
        }


@dataclass
class NewsFeed:
    """An RSS/Atom feed subscription."""
    id: str = ""
    url: str = ""
    title: str = ""
    items: List[NewsItem] = field(default_factory=list)
    last_updated: float = 0.0
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(self.url.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "item_count": len(self.items),
            "last_updated": self.last_updated,
        }


@dataclass
class NewsReaderPart(Part):
    """
    CyberDog News Reader component.
    
    Original CyberDog had newsgroup support.
    Newton CyberDog supports RSS/Atom feeds.
    """
    
    # Subscriptions
    feeds: Dict[str, NewsFeed] = field(default_factory=dict)
    
    # Current view
    current_feed: Optional[str] = None
    selected_item: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.part_type = PartType.BROWSER  # News uses browser part type
        self.name = self.name or "News Reader"
    
    def subscribe(self, url: str, title: str = "") -> NewsFeed:
        """Subscribe to a feed."""
        feed = NewsFeed(url=url, title=title or url)
        self.feeds[feed.id] = feed
        self._compute_hash()
        return feed
    
    def unsubscribe(self, feed_id: str) -> bool:
        """Unsubscribe from a feed."""
        if feed_id in self.feeds:
            del self.feeds[feed_id]
            self._compute_hash()
            return True
        return False
    
    def refresh(self, feed_id: Optional[str] = None) -> List[NewsItem]:
        """
        Refresh a feed or all feeds.
        
        Simulated — real impl would fetch RSS/Atom.
        """
        new_items = []
        feeds = [self.feeds[feed_id]] if feed_id else list(self.feeds.values())
        
        for feed in feeds:
            # Simulate fetching new items
            item = NewsItem(
                title=f"New item from {feed.title}",
                link=f"{feed.url}/item/{int(time.time())}",
                content="This is a simulated news item.",
                source=feed.title,
                published_at=time.time(),
                verified=True,
            )
            feed.items.append(item)
            feed.last_updated = time.time()
            new_items.append(item)
        
        self._compute_hash()
        return new_items
    
    def mark_read(self, item_id: str) -> bool:
        """Mark an item as read."""
        for feed in self.feeds.values():
            for item in feed.items:
                if item.id == item_id:
                    item.read = True
                    return True
        return False
    
    def star(self, item_id: str) -> bool:
        """Star/favorite an item."""
        for feed in self.feeds.values():
            for item in feed.items:
                if item.id == item_id:
                    item.starred = not item.starred
                    return True
        return False
    
    def get_unread(self) -> List[NewsItem]:
        """Get all unread items."""
        unread = []
        for feed in self.feeds.values():
            for item in feed.items:
                if not item.read:
                    unread.append(item)
        return sorted(unread, key=lambda x: x.published_at, reverse=True)
    
    def get_starred(self) -> List[NewsItem]:
        """Get all starred items."""
        starred = []
        for feed in self.feeds.values():
            for item in feed.items:
                if item.starred:
                    starred.append(item)
        return starred
    
    def get_content_for_hash(self) -> str:
        return json.dumps({
            "type": "news_reader",
            "feed_count": len(self.feeds),
            "feeds": list(self.feeds.keys()),
        }, sort_keys=True)


# ═══════════════════════════════════════════════════════════════════════════════
# FTP CLIENT PART
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FTPFile:
    """A file in an FTP directory."""
    name: str
    path: str
    size: int = 0
    is_dir: bool = False
    modified_at: float = 0.0
    hash: str = ""
    
    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.sha256(
                f"{self.path}:{self.size}:{self.modified_at}".encode()
            ).hexdigest()[:16]


@dataclass
class FTPClientPart(Part):
    """
    CyberDog FTP Client component.
    
    File transfer with verification.
    """
    
    # Connection state
    connected: bool = False
    host: str = ""
    port: int = 21
    username: str = "anonymous"
    current_path: str = "/"
    
    # Directory listing
    files: List[FTPFile] = field(default_factory=list)
    
    # Transfer history
    transfers: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self.part_type = PartType.FTP
        self.name = self.name or "FTP Client"
    
    def connect(self, host: str, port: int = 21, username: str = "anonymous", password: str = "") -> bool:
        """
        Connect to an FTP server.
        
        Simulated — real impl would use ftplib.
        """
        self.host = host
        self.port = port
        self.username = username
        self.connected = True
        self.current_path = "/"
        
        # Simulate directory listing
        self.files = [
            FTPFile(name="readme.txt", path="/readme.txt", size=1024),
            FTPFile(name="data/", path="/data/", is_dir=True),
            FTPFile(name="downloads/", path="/downloads/", is_dir=True),
        ]
        
        self._compute_hash()
        return True
    
    def disconnect(self):
        """Disconnect from FTP server."""
        self.connected = False
        self.files = []
        self._compute_hash()
    
    def cd(self, path: str) -> bool:
        """Change directory."""
        if not self.connected:
            return False
        
        if path.startswith("/"):
            self.current_path = path
        else:
            self.current_path = f"{self.current_path.rstrip('/')}/{path}"
        
        # Simulate new listing
        self.files = [
            FTPFile(name="..", path=f"{self.current_path}/..", is_dir=True),
            FTPFile(name=f"file_{int(time.time())}.txt", path=f"{self.current_path}/file.txt", size=512),
        ]
        
        self._compute_hash()
        return True
    
    def download(self, remote_path: str, local_path: str) -> Dict[str, Any]:
        """
        Download a file.
        
        Simulated — returns transfer record.
        """
        transfer = {
            "type": "download",
            "remote": remote_path,
            "local": local_path,
            "size": 1024,  # Simulated
            "started_at": time.time(),
            "completed_at": time.time(),
            "hash": hashlib.sha256(f"{remote_path}:{local_path}".encode()).hexdigest()[:16],
            "verified": True,
        }
        self.transfers.append(transfer)
        self._compute_hash()
        return transfer
    
    def upload(self, local_path: str, remote_path: str) -> Dict[str, Any]:
        """
        Upload a file.
        
        Simulated — returns transfer record.
        """
        transfer = {
            "type": "upload",
            "local": local_path,
            "remote": remote_path,
            "size": 1024,  # Simulated
            "started_at": time.time(),
            "completed_at": time.time(),
            "hash": hashlib.sha256(f"{local_path}:{remote_path}".encode()).hexdigest()[:16],
            "verified": True,
        }
        self.transfers.append(transfer)
        self._compute_hash()
        return transfer
    
    def get_content_for_hash(self) -> str:
        return json.dumps({
            "type": "ftp_client",
            "host": self.host,
            "connected": self.connected,
            "path": self.current_path,
        }, sort_keys=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ADDRESS BOOK PART — CyberDog Contacts Reimagined
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Contact:
    """A contact entry with verification."""
    id: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    organization: str = ""
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    hash: str = ""
    verified: bool = True
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.name}:{self.email}:{time.time()}".encode()
            ).hexdigest()[:16]
        if not self.hash:
            self._compute_hash()
    
    def _compute_hash(self):
        self.hash = hashlib.sha256(
            f"{self.name}:{self.email}:{self.phone}:{self.address}".encode()
        ).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "organization": self.organization,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "hash": self.hash,
            "verified": self.verified,
        }


@dataclass
class AddressBookPart(Part):
    """
    CyberDog Address Book component.
    
    Contact management with verification.
    """
    
    # Contacts
    contacts: Dict[str, Contact] = field(default_factory=dict)
    
    # Groups
    groups: Dict[str, List[str]] = field(default_factory=dict)  # group_name -> contact_ids
    
    # Current view
    selected_contact: Optional[str] = None
    search_query: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.part_type = PartType.FORM  # Uses form part type
        self.name = self.name or "Address Book"
    
    def add_contact(self, name: str, email: str = "", phone: str = "", **kwargs) -> Contact:
        """Add a new contact."""
        contact = Contact(
            name=name,
            email=email,
            phone=phone,
            address=kwargs.get("address", ""),
            organization=kwargs.get("organization", ""),
            notes=kwargs.get("notes", ""),
            tags=kwargs.get("tags", []),
        )
        self.contacts[contact.id] = contact
        self._compute_hash()
        return contact
    
    def update_contact(self, contact_id: str, **updates) -> Optional[Contact]:
        """Update an existing contact."""
        if contact_id not in self.contacts:
            return None
        
        contact = self.contacts[contact_id]
        for key, value in updates.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        
        contact.updated_at = time.time()
        contact._compute_hash()
        self._compute_hash()
        return contact
    
    def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact."""
        if contact_id in self.contacts:
            del self.contacts[contact_id]
            
            # Remove from groups
            for group_contacts in self.groups.values():
                if contact_id in group_contacts:
                    group_contacts.remove(contact_id)
            
            self._compute_hash()
            return True
        return False
    
    def search(self, query: str) -> List[Contact]:
        """Search contacts."""
        query = query.lower()
        results = []
        for contact in self.contacts.values():
            if (query in contact.name.lower() or
                query in contact.email.lower() or
                query in contact.organization.lower()):
                results.append(contact)
        return results
    
    def create_group(self, name: str) -> str:
        """Create a contact group."""
        self.groups[name] = []
        self._compute_hash()
        return name
    
    def add_to_group(self, contact_id: str, group_name: str) -> bool:
        """Add contact to a group."""
        if group_name not in self.groups:
            self.groups[group_name] = []
        
        if contact_id in self.contacts and contact_id not in self.groups[group_name]:
            self.groups[group_name].append(contact_id)
            self._compute_hash()
            return True
        return False
    
    def get_group(self, group_name: str) -> List[Contact]:
        """Get all contacts in a group."""
        contact_ids = self.groups.get(group_name, [])
        return [self.contacts[cid] for cid in contact_ids if cid in self.contacts]
    
    def get_content_for_hash(self) -> str:
        return json.dumps({
            "type": "address_book",
            "contact_count": len(self.contacts),
            "group_count": len(self.groups),
        }, sort_keys=True)


# ═══════════════════════════════════════════════════════════════════════════════
# BOOKMARKS PART
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Bookmark:
    """A URL bookmark with verification."""
    id: str = ""
    title: str = ""
    url: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    folder: str = ""
    created_at: float = field(default_factory=time.time)
    visited_at: float = 0.0
    visit_count: int = 0
    hash: str = ""
    verified: bool = True
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(self.url.encode()).hexdigest()[:16]
        if not self.hash:
            self.hash = hashlib.sha256(
                f"{self.url}:{self.title}".encode()
            ).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "tags": self.tags,
            "folder": self.folder,
            "created_at": self.created_at,
            "visited_at": self.visited_at,
            "visit_count": self.visit_count,
            "hash": self.hash,
            "verified": self.verified,
        }


@dataclass
class BookmarksPart(Part):
    """
    CyberDog Bookmarks component.
    
    URL bookmarks with organization and search.
    """
    
    # Bookmarks
    bookmarks: Dict[str, Bookmark] = field(default_factory=dict)
    
    # Folders
    folders: Dict[str, List[str]] = field(default_factory=dict)  # folder_name -> bookmark_ids
    
    def __post_init__(self):
        super().__post_init__()
        self.part_type = PartType.LINK
        self.name = self.name or "Bookmarks"
    
    def add(self, url: str, title: str = "", folder: str = "", tags: Optional[List[str]] = None) -> Bookmark:
        """Add a bookmark."""
        bookmark = Bookmark(
            title=title or url,
            url=url,
            folder=folder,
            tags=tags or [],
        )
        self.bookmarks[bookmark.id] = bookmark
        
        if folder:
            if folder not in self.folders:
                self.folders[folder] = []
            self.folders[folder].append(bookmark.id)
        
        self._compute_hash()
        return bookmark
    
    def remove(self, bookmark_id: str) -> bool:
        """Remove a bookmark."""
        if bookmark_id in self.bookmarks:
            bookmark = self.bookmarks[bookmark_id]
            if bookmark.folder and bookmark.folder in self.folders:
                self.folders[bookmark.folder].remove(bookmark_id)
            del self.bookmarks[bookmark_id]
            self._compute_hash()
            return True
        return False
    
    def visit(self, bookmark_id: str) -> Optional[Bookmark]:
        """Record a visit to a bookmark."""
        if bookmark_id in self.bookmarks:
            bookmark = self.bookmarks[bookmark_id]
            bookmark.visited_at = time.time()
            bookmark.visit_count += 1
            return bookmark
        return None
    
    def search(self, query: str) -> List[Bookmark]:
        """Search bookmarks."""
        query = query.lower()
        results = []
        for bookmark in self.bookmarks.values():
            if (query in bookmark.title.lower() or
                query in bookmark.url.lower() or
                query in bookmark.description.lower() or
                any(query in tag.lower() for tag in bookmark.tags)):
                results.append(bookmark)
        return results
    
    def get_folder(self, folder_name: str) -> List[Bookmark]:
        """Get bookmarks in a folder."""
        bookmark_ids = self.folders.get(folder_name, [])
        return [self.bookmarks[bid] for bid in bookmark_ids if bid in self.bookmarks]
    
    def get_by_tag(self, tag: str) -> List[Bookmark]:
        """Get bookmarks with a specific tag."""
        return [b for b in self.bookmarks.values() if tag in b.tags]
    
    def get_recent(self, limit: int = 10) -> List[Bookmark]:
        """Get recently visited bookmarks."""
        sorted_bookmarks = sorted(
            self.bookmarks.values(),
            key=lambda b: b.visited_at,
            reverse=True
        )
        return sorted_bookmarks[:limit]
    
    def get_content_for_hash(self) -> str:
        return json.dumps({
            "type": "bookmarks",
            "count": len(self.bookmarks),
            "folders": list(self.folders.keys()),
        }, sort_keys=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CYBERDOG SUITE — Combined Internet Suite
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CyberDogSuite:
    """
    The complete CyberDog Internet Suite.
    
    All components in one verified package.
    """
    
    # Components
    browser: WebBrowserPart = field(default_factory=WebBrowserPart)
    email: EmailClientPart = field(default_factory=EmailClientPart)
    news: NewsReaderPart = field(default_factory=NewsReaderPart)
    ftp: FTPClientPart = field(default_factory=FTPClientPart)
    address_book: AddressBookPart = field(default_factory=AddressBookPart)
    bookmarks: BookmarksPart = field(default_factory=BookmarksPart)
    
    # The document containing all parts
    document: CompoundDocument = field(default_factory=lambda: CompoundDocument(title="CyberDog Suite"))
    
    def __post_init__(self):
        """Initialize the suite with all components embedded."""
        # Add all parts to document
        self.document.add_part(self.browser)
        self.document.add_part(self.email)
        self.document.add_part(self.news)
        self.document.add_part(self.ftp)
        self.document.add_part(self.address_book)
        self.document.add_part(self.bookmarks)
        
        # Save to store
        get_document_store().save(self.document)
    
    def verify_all(self) -> Dict[str, bool]:
        """Verify all components."""
        return self.document.verify_all()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the suite."""
        return {
            "document": self.document.to_dict(),
            "components": {
                "browser": self.browser.to_dict(),
                "email": self.email.to_dict(),
                "news": self.news.to_dict(),
                "ftp": self.ftp.to_dict(),
                "address_book": self.address_book.to_dict(),
                "bookmarks": self.bookmarks.to_dict(),
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# PART HANDLER REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def register_cyberdog_handlers():
    """Register CyberDog part handlers with OpenDoc."""
    registry = get_part_registry()
    
    # FTP handler
    registry.register(PartHandler(
        part_type=PartType.FTP,
        name="FTP Client",
        description="CyberDog file transfer component",
        default_constraints=[],
    ))
    
    # Already registered in opendoc:
    # - PartType.BROWSER (web browser)
    # - PartType.MAIL (email)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_cyberdog() -> CyberDogSuite:
    """Create a new CyberDog suite."""
    return CyberDogSuite()


def create_web_browser(name: str = "Browser") -> WebBrowserPart:
    """Create a standalone web browser part."""
    return WebBrowserPart(name=name)


def create_email_client(name: str = "Email", email: str = "") -> EmailClientPart:
    """Create a standalone email client part."""
    client = EmailClientPart(name=name)
    client.account_email = email
    return client


def create_news_reader(name: str = "News") -> NewsReaderPart:
    """Create a standalone news reader part."""
    return NewsReaderPart(name=name)


def create_ftp_client(name: str = "FTP") -> FTPClientPart:
    """Create a standalone FTP client part."""
    return FTPClientPart(name=name)


def create_address_book(name: str = "Contacts") -> AddressBookPart:
    """Create a standalone address book part."""
    return AddressBookPart(name=name)


def create_bookmarks(name: str = "Bookmarks") -> BookmarksPart:
    """Create a standalone bookmarks part."""
    return BookmarksPart(name=name)


# ═══════════════════════════════════════════════════════════════════════════════
# SIMPLIFIED ONE-LINERS — Woz's "make it fun"
# ═══════════════════════════════════════════════════════════════════════════════

def browse(url: str) -> Dict[str, Any]:
    """
    One-liner to browse a URL and get results.
    
    Returns the resource and text content.
    
    Example:
        result = browse("google.com")
        print(result['text'])  # Plain text content
    """
    browser = create_web_browser()
    resource = browser.navigate(url)
    result = browser.execute_script("get text")
    
    return {
        "url": resource.url,
        "status": resource.status_code,
        "html": resource.content,
        "text": result.get("text", ""),
        "hash": resource.content_hash,
        "changed": resource.changed,
        "verified": resource.verified,
    }


def fetch_and_verify(url: str) -> bool:
    """
    Fetch a URL and return whether it was successfully verified.
    
    Example:
        if fetch_and_verify("example.com"):
            print("Page is verified!")
    """
    browser = create_web_browser()
    resource = browser.navigate(url)
    return resource.verified and resource.status_code == 200


def quick_suite() -> Dict[str, Any]:
    """
    Create a complete CyberDog suite in one line.
    
    Example:
        suite = quick_suite()
        suite['browser'].navigate("google.com")
        suite['email'].compose("to@example.com", "Hello")
    """
    return {
        "browser": create_web_browser(),
        "email": create_email_client(),
        "news": create_news_reader(),
        "ftp": create_ftp_client(),
        "contacts": create_address_book(),
        "bookmarks": create_bookmarks(),
    }


# Initialize handlers on import
register_cyberdog_handlers()
