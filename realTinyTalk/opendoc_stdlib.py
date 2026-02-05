"""
═══════════════════════════════════════════════════════════════════════════════
OPENDOC/CYBERDOG STDLIB — TinyTalk Bindings for Newton OpenDoc & CyberDog
═══════════════════════════════════════════════════════════════════════════════

This module exposes OpenDoc and CyberDog to TinyTalk programs.

Users can work with compound documents:

    # Create a document
    let doc = Document.new("My Report")
    
    # Add parts
    let text = TextPart.new("Introduction", "Hello world")
    Document.add(doc, text)
    
    # Create CyberDog components
    let browser = Browser.new()
    Browser.navigate(browser, "https://example.com")
    
    # Email
    let email = Email.new("me@example.com")
    let msg = Email.compose(email, ["friend@example.com"], "Hello", "How are you?")

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from realTinyTalk.types import Value, ValueType
from realTinyTalk.foghorn_stdlib import foghorn_to_tinytalk, tinytalk_to_foghorn

# Import OpenDoc and CyberDog
from foghorn.opendoc import (
    Part, PartType, PartState, CompoundDocument,
    get_document_store, get_part_registry,
    create_document, create_part, embed_part,
    BentoSerializer,
)

from foghorn.cyberdog import (
    CyberDogSuite, CyberDogComponent,
    WebBrowserPart, WebResource,
    EmailClientPart, EmailMessage,
    NewsReaderPart, NewsFeed, NewsItem,
    FTPClientPart, FTPFile,
    AddressBookPart, Contact,
    BookmarksPart, Bookmark,
    create_cyberdog, create_web_browser, create_email_client,
    create_news_reader, create_ftp_client, create_address_book, create_bookmarks,
)


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# In-memory storage for objects created in this session
_session_docs: Dict[str, CompoundDocument] = {}
_session_parts: Dict[str, Part] = {}
_session_browsers: Dict[str, WebBrowserPart] = {}
_session_emails: Dict[str, EmailClientPart] = {}
_session_news: Dict[str, NewsReaderPart] = {}
_session_ftp: Dict[str, FTPClientPart] = {}
_session_contacts: Dict[str, AddressBookPart] = {}
_session_bookmarks: Dict[str, BookmarksPart] = {}


def builtin_document_new(args: List[Value]) -> Value:
    """
    Create a new compound document.
    
    Usage:
        let doc = Document.new("My Report")
    """
    title = "Untitled"
    if args and args[0].type == ValueType.STRING:
        title = args[0].data
    
    doc = create_document(title)
    _session_docs[doc.hash] = doc
    
    return foghorn_to_tinytalk(doc)


def builtin_document_get(args: List[Value]) -> Value:
    """
    Get a document by hash.
    
    Usage:
        let doc = Document.get("abc123")
    """
    if not args or args[0].type != ValueType.STRING:
        return Value.null_val()
    
    hash_val = args[0].data
    
    # Check session first
    if hash_val in _session_docs:
        return foghorn_to_tinytalk(_session_docs[hash_val])
    
    # Check document store
    doc = get_document_store().get(hash_val)
    if doc:
        return foghorn_to_tinytalk(doc)
    
    return Value.null_val()


def builtin_document_add(args: List[Value]) -> Value:
    """
    Add a part to a document.
    
    Usage:
        Document.add(doc, part)
        Document.add(doc, part, container_hash)
    """
    if len(args) < 2:
        return Value.bool_val(False)
    
    # Get document
    doc_hash = _get_hash_from_value(args[0])
    if not doc_hash or doc_hash not in _session_docs:
        return Value.bool_val(False)
    doc = _session_docs[doc_hash]
    
    # Get part
    part_hash = _get_hash_from_value(args[1])
    if not part_hash or part_hash not in _session_parts:
        return Value.bool_val(False)
    part = _session_parts[part_hash]
    
    # Container (optional)
    container = None
    if len(args) > 2 and args[2].type == ValueType.STRING:
        container = args[2].data
    
    new_hash = embed_part(doc, part, container)
    return Value.string_val(new_hash)


def builtin_document_verify(args: List[Value]) -> Value:
    """
    Verify all parts in a document.
    
    Usage:
        let results = Document.verify(doc)
    """
    if not args:
        return Value.null_val()
    
    doc_hash = _get_hash_from_value(args[0])
    if not doc_hash or doc_hash not in _session_docs:
        return Value.null_val()
    
    doc = _session_docs[doc_hash]
    results = doc.verify_all()
    
    return foghorn_to_tinytalk(results)


def builtin_document_all(args: List[Value]) -> Value:
    """
    List all documents.
    
    Usage:
        let docs = Document.all()
    """
    all_docs = list(_session_docs.values()) + get_document_store().list_all()
    return Value.list_val([foghorn_to_tinytalk(d) for d in all_docs])


def builtin_document_serialize(args: List[Value]) -> Value:
    """
    Serialize a document to JSON (Bento format).
    
    Usage:
        let json = Document.serialize(doc)
    """
    if not args:
        return Value.null_val()
    
    doc_hash = _get_hash_from_value(args[0])
    if not doc_hash or doc_hash not in _session_docs:
        return Value.null_val()
    
    doc = _session_docs[doc_hash]
    return Value.string_val(BentoSerializer.serialize(doc))


# ═══════════════════════════════════════════════════════════════════════════════
# PART FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_part_new(args: List[Value]) -> Value:
    """
    Create a new part.
    
    Usage:
        let part = Part.new("text", "Introduction", "Hello world")
        let part = Part.new("table", "Data", [[1,2],[3,4]])
    """
    if len(args) < 3:
        return Value.null_val()
    
    type_str = args[0].data if args[0].type == ValueType.STRING else "text"
    name = args[1].data if args[1].type == ValueType.STRING else ""
    content = tinytalk_to_foghorn(args[2])
    
    try:
        part_type = PartType(type_str)
    except ValueError:
        part_type = PartType.TEXT
    
    part = create_part(name, part_type, content)
    _session_parts[part.hash] = part
    
    return foghorn_to_tinytalk(part)


def builtin_textpart_new(args: List[Value]) -> Value:
    """
    Create a text part (convenience function).
    
    Usage:
        let text = TextPart.new("Title", "Content here")
    """
    if len(args) < 2:
        return Value.null_val()
    
    name = args[0].data if args[0].type == ValueType.STRING else ""
    content = args[1].data if args[1].type == ValueType.STRING else ""
    
    part = create_part(name, PartType.TEXT, content)
    _session_parts[part.hash] = part
    
    return foghorn_to_tinytalk(part)


def builtin_tablepart_new(args: List[Value]) -> Value:
    """
    Create a table part.
    
    Usage:
        let table = TablePart.new("Data", [["A", "B"], [1, 2], [3, 4]])
    """
    if len(args) < 2:
        return Value.null_val()
    
    name = args[0].data if args[0].type == ValueType.STRING else ""
    content = tinytalk_to_foghorn(args[1])
    
    part = create_part(name, PartType.TABLE, content)
    _session_parts[part.hash] = part
    
    return foghorn_to_tinytalk(part)


def builtin_part_verify(args: List[Value]) -> Value:
    """
    Verify a part against its constraints.
    
    Usage:
        let ok = Part.verify(part)
    """
    if not args:
        return Value.bool_val(False)
    
    part_hash = _get_hash_from_value(args[0])
    if not part_hash or part_hash not in _session_parts:
        return Value.bool_val(False)
    
    part = _session_parts[part_hash]
    return Value.bool_val(part.verify())


def builtin_parttype_list(args: List[Value]) -> Value:
    """
    List all available part types.
    
    Usage:
        let types = PartType.list()
    """
    return Value.list_val([Value.string_val(pt.value) for pt in PartType])


# ═══════════════════════════════════════════════════════════════════════════════
# WEB BROWSER FUNCTIONS (CyberDog)
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_browser_new(args: List[Value]) -> Value:
    """
    Create a web browser component.
    
    Usage:
        let browser = Browser.new()
        let browser = Browser.new("My Browser")
    """
    name = "Browser"
    if args and args[0].type == ValueType.STRING:
        name = args[0].data
    
    browser = create_web_browser(name)
    _session_browsers[browser.hash] = browser
    
    return foghorn_to_tinytalk(browser)


def builtin_browser_navigate(args: List[Value]) -> Value:
    """
    Navigate to a URL.
    
    Usage:
        let resource = Browser.navigate(browser, "https://example.com")
    """
    if len(args) < 2:
        return Value.null_val()
    
    browser_hash = _get_hash_from_value(args[0])
    if not browser_hash or browser_hash not in _session_browsers:
        return Value.null_val()
    
    url = args[1].data if args[1].type == ValueType.STRING else str(args[1].data)
    
    browser = _session_browsers[browser_hash]
    resource = browser.navigate(url)
    
    # Update hash after mutation
    del _session_browsers[browser_hash]
    _session_browsers[browser.hash] = browser
    
    return foghorn_to_tinytalk(resource)


def builtin_browser_back(args: List[Value]) -> Value:
    """
    Navigate back in history.
    
    Usage:
        Browser.back(browser)
    """
    if not args:
        return Value.null_val()
    
    browser_hash = _get_hash_from_value(args[0])
    if not browser_hash or browser_hash not in _session_browsers:
        return Value.null_val()
    
    browser = _session_browsers[browser_hash]
    resource = browser.back()
    
    return foghorn_to_tinytalk(resource) if resource else Value.null_val()


def builtin_browser_forward(args: List[Value]) -> Value:
    """
    Navigate forward in history.
    
    Usage:
        Browser.forward(browser)
    """
    if not args:
        return Value.null_val()
    
    browser_hash = _get_hash_from_value(args[0])
    if not browser_hash or browser_hash not in _session_browsers:
        return Value.null_val()
    
    browser = _session_browsers[browser_hash]
    resource = browser.forward()
    
    return foghorn_to_tinytalk(resource) if resource else Value.null_val()


def builtin_browser_history(args: List[Value]) -> Value:
    """
    Get browser history.
    
    Usage:
        let urls = Browser.history(browser)
    """
    if not args:
        return Value.list_val([])
    
    browser_hash = _get_hash_from_value(args[0])
    if not browser_hash or browser_hash not in _session_browsers:
        return Value.list_val([])
    
    browser = _session_browsers[browser_hash]
    return Value.list_val([Value.string_val(url) for url in browser.history])


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL FUNCTIONS (CyberDog)
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_email_new(args: List[Value]) -> Value:
    """
    Create an email client.
    
    Usage:
        let email = Email.new("me@example.com")
    """
    account = ""
    if args and args[0].type == ValueType.STRING:
        account = args[0].data
    
    email = create_email_client("Email", account)
    _session_emails[email.hash] = email
    
    return foghorn_to_tinytalk(email)


def builtin_email_compose(args: List[Value]) -> Value:
    """
    Compose a new email.
    
    Usage:
        let msg = Email.compose(email, ["to@example.com"], "Subject", "Body")
    """
    if len(args) < 4:
        return Value.null_val()
    
    email_hash = _get_hash_from_value(args[0])
    if not email_hash or email_hash not in _session_emails:
        return Value.null_val()
    
    to = []
    if args[1].type == ValueType.LIST:
        to = [v.data for v in args[1].data if v.type == ValueType.STRING]
    elif args[1].type == ValueType.STRING:
        to = [args[1].data]
    
    subject = args[2].data if args[2].type == ValueType.STRING else ""
    body = args[3].data if args[3].type == ValueType.STRING else ""
    
    email_client = _session_emails[email_hash]
    msg = email_client.compose(to, subject, body)
    
    return foghorn_to_tinytalk(msg)


def builtin_email_send(args: List[Value]) -> Value:
    """
    Send a draft email.
    
    Usage:
        Email.send(email, message_id)
    """
    if len(args) < 2:
        return Value.bool_val(False)
    
    email_hash = _get_hash_from_value(args[0])
    if not email_hash or email_hash not in _session_emails:
        return Value.bool_val(False)
    
    msg_id = args[1].data if args[1].type == ValueType.STRING else str(args[1].data)
    
    email_client = _session_emails[email_hash]
    return Value.bool_val(email_client.send(msg_id))


def builtin_email_inbox(args: List[Value]) -> Value:
    """
    Get inbox messages.
    
    Usage:
        let messages = Email.inbox(email)
    """
    if not args:
        return Value.list_val([])
    
    email_hash = _get_hash_from_value(args[0])
    if not email_hash or email_hash not in _session_emails:
        return Value.list_val([])
    
    email_client = _session_emails[email_hash]
    return Value.list_val([foghorn_to_tinytalk(m) for m in email_client.inbox])


def builtin_email_drafts(args: List[Value]) -> Value:
    """
    Get draft messages.
    
    Usage:
        let drafts = Email.drafts(email)
    """
    if not args:
        return Value.list_val([])
    
    email_hash = _get_hash_from_value(args[0])
    if not email_hash or email_hash not in _session_emails:
        return Value.list_val([])
    
    email_client = _session_emails[email_hash]
    return Value.list_val([foghorn_to_tinytalk(m) for m in email_client.drafts])


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS READER FUNCTIONS (CyberDog)
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_news_new(args: List[Value]) -> Value:
    """
    Create a news reader.
    
    Usage:
        let news = News.new()
    """
    name = "News"
    if args and args[0].type == ValueType.STRING:
        name = args[0].data
    
    news = create_news_reader(name)
    _session_news[news.hash] = news
    
    return foghorn_to_tinytalk(news)


def builtin_news_subscribe(args: List[Value]) -> Value:
    """
    Subscribe to a feed.
    
    Usage:
        let feed = News.subscribe(news, "https://example.com/rss")
        let feed = News.subscribe(news, "https://example.com/rss", "Example Feed")
    """
    if len(args) < 2:
        return Value.null_val()
    
    news_hash = _get_hash_from_value(args[0])
    if not news_hash or news_hash not in _session_news:
        return Value.null_val()
    
    url = args[1].data if args[1].type == ValueType.STRING else ""
    title = args[2].data if len(args) > 2 and args[2].type == ValueType.STRING else ""
    
    news_reader = _session_news[news_hash]
    feed = news_reader.subscribe(url, title)
    
    return foghorn_to_tinytalk(feed)


def builtin_news_refresh(args: List[Value]) -> Value:
    """
    Refresh feeds to get new items.
    
    Usage:
        let items = News.refresh(news)
        let items = News.refresh(news, feed_id)
    """
    if not args:
        return Value.list_val([])
    
    news_hash = _get_hash_from_value(args[0])
    if not news_hash or news_hash not in _session_news:
        return Value.list_val([])
    
    feed_id = None
    if len(args) > 1 and args[1].type == ValueType.STRING:
        feed_id = args[1].data
    
    news_reader = _session_news[news_hash]
    items = news_reader.refresh(feed_id)
    
    return Value.list_val([foghorn_to_tinytalk(i) for i in items])


def builtin_news_unread(args: List[Value]) -> Value:
    """
    Get all unread items.
    
    Usage:
        let items = News.unread(news)
    """
    if not args:
        return Value.list_val([])
    
    news_hash = _get_hash_from_value(args[0])
    if not news_hash or news_hash not in _session_news:
        return Value.list_val([])
    
    news_reader = _session_news[news_hash]
    return Value.list_val([foghorn_to_tinytalk(i) for i in news_reader.get_unread()])


# ═══════════════════════════════════════════════════════════════════════════════
# FTP CLIENT FUNCTIONS (CyberDog)
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_ftp_new(args: List[Value]) -> Value:
    """
    Create an FTP client.
    
    Usage:
        let ftp = FTP.new()
    """
    ftp = create_ftp_client()
    _session_ftp[ftp.hash] = ftp
    return foghorn_to_tinytalk(ftp)


def builtin_ftp_connect(args: List[Value]) -> Value:
    """
    Connect to an FTP server.
    
    Usage:
        FTP.connect(ftp, "ftp.example.com")
        FTP.connect(ftp, "ftp.example.com", 21, "user", "pass")
    """
    if len(args) < 2:
        return Value.bool_val(False)
    
    ftp_hash = _get_hash_from_value(args[0])
    if not ftp_hash or ftp_hash not in _session_ftp:
        return Value.bool_val(False)
    
    host = args[1].data if args[1].type == ValueType.STRING else ""
    port = 21
    username = "anonymous"
    password = ""
    
    if len(args) > 2 and args[2].type == ValueType.INT:
        port = args[2].data
    if len(args) > 3 and args[3].type == ValueType.STRING:
        username = args[3].data
    if len(args) > 4 and args[4].type == ValueType.STRING:
        password = args[4].data
    
    ftp = _session_ftp[ftp_hash]
    return Value.bool_val(ftp.connect(host, port, username, password))


def builtin_ftp_list(args: List[Value]) -> Value:
    """
    List files in current directory.
    
    Usage:
        let files = FTP.list(ftp)
    """
    if not args:
        return Value.list_val([])
    
    ftp_hash = _get_hash_from_value(args[0])
    if not ftp_hash or ftp_hash not in _session_ftp:
        return Value.list_val([])
    
    ftp = _session_ftp[ftp_hash]
    return Value.list_val([foghorn_to_tinytalk({
        "name": f.name,
        "path": f.path,
        "size": f.size,
        "is_dir": f.is_dir,
    }) for f in ftp.files])


def builtin_ftp_download(args: List[Value]) -> Value:
    """
    Download a file.
    
    Usage:
        let transfer = FTP.download(ftp, "/remote/file.txt", "/local/file.txt")
    """
    if len(args) < 3:
        return Value.null_val()
    
    ftp_hash = _get_hash_from_value(args[0])
    if not ftp_hash or ftp_hash not in _session_ftp:
        return Value.null_val()
    
    remote = args[1].data if args[1].type == ValueType.STRING else ""
    local = args[2].data if args[2].type == ValueType.STRING else ""
    
    ftp = _session_ftp[ftp_hash]
    transfer = ftp.download(remote, local)
    
    return foghorn_to_tinytalk(transfer)


# ═══════════════════════════════════════════════════════════════════════════════
# ADDRESS BOOK FUNCTIONS (CyberDog)
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_contacts_new(args: List[Value]) -> Value:
    """
    Create an address book.
    
    Usage:
        let contacts = Contacts.new()
    """
    contacts = create_address_book()
    _session_contacts[contacts.hash] = contacts
    return foghorn_to_tinytalk(contacts)


def builtin_contacts_add(args: List[Value]) -> Value:
    """
    Add a contact.
    
    Usage:
        let contact = Contacts.add(contacts, "John Doe", "john@example.com")
        let contact = Contacts.add(contacts, "John Doe", "john@example.com", "555-1234")
    """
    if len(args) < 3:
        return Value.null_val()
    
    contacts_hash = _get_hash_from_value(args[0])
    if not contacts_hash or contacts_hash not in _session_contacts:
        return Value.null_val()
    
    name = args[1].data if args[1].type == ValueType.STRING else ""
    email = args[2].data if args[2].type == ValueType.STRING else ""
    phone = args[3].data if len(args) > 3 and args[3].type == ValueType.STRING else ""
    
    address_book = _session_contacts[contacts_hash]
    contact = address_book.add_contact(name, email, phone)
    
    return foghorn_to_tinytalk(contact)


def builtin_contacts_search(args: List[Value]) -> Value:
    """
    Search contacts.
    
    Usage:
        let results = Contacts.search(contacts, "john")
    """
    if len(args) < 2:
        return Value.list_val([])
    
    contacts_hash = _get_hash_from_value(args[0])
    if not contacts_hash or contacts_hash not in _session_contacts:
        return Value.list_val([])
    
    query = args[1].data if args[1].type == ValueType.STRING else ""
    
    address_book = _session_contacts[contacts_hash]
    results = address_book.search(query)
    
    return Value.list_val([foghorn_to_tinytalk(c) for c in results])


def builtin_contacts_all(args: List[Value]) -> Value:
    """
    Get all contacts.
    
    Usage:
        let all = Contacts.all(contacts)
    """
    if not args:
        return Value.list_val([])
    
    contacts_hash = _get_hash_from_value(args[0])
    if not contacts_hash or contacts_hash not in _session_contacts:
        return Value.list_val([])
    
    address_book = _session_contacts[contacts_hash]
    return Value.list_val([foghorn_to_tinytalk(c) for c in address_book.contacts.values()])


# ═══════════════════════════════════════════════════════════════════════════════
# BOOKMARKS FUNCTIONS (CyberDog)
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_bookmarks_new(args: List[Value]) -> Value:
    """
    Create a bookmarks collection.
    
    Usage:
        let bookmarks = Bookmarks.new()
    """
    bookmarks = create_bookmarks()
    _session_bookmarks[bookmarks.hash] = bookmarks
    return foghorn_to_tinytalk(bookmarks)


def builtin_bookmarks_add(args: List[Value]) -> Value:
    """
    Add a bookmark.
    
    Usage:
        let bm = Bookmarks.add(bookmarks, "https://example.com", "Example Site")
        let bm = Bookmarks.add(bookmarks, "https://example.com", "Example Site", "folder")
    """
    if len(args) < 3:
        return Value.null_val()
    
    bookmarks_hash = _get_hash_from_value(args[0])
    if not bookmarks_hash or bookmarks_hash not in _session_bookmarks:
        return Value.null_val()
    
    url = args[1].data if args[1].type == ValueType.STRING else ""
    title = args[2].data if args[2].type == ValueType.STRING else ""
    folder = args[3].data if len(args) > 3 and args[3].type == ValueType.STRING else ""
    
    bookmarks_part = _session_bookmarks[bookmarks_hash]
    bookmark = bookmarks_part.add(url, title, folder)
    
    return foghorn_to_tinytalk(bookmark)


def builtin_bookmarks_search(args: List[Value]) -> Value:
    """
    Search bookmarks.
    
    Usage:
        let results = Bookmarks.search(bookmarks, "example")
    """
    if len(args) < 2:
        return Value.list_val([])
    
    bookmarks_hash = _get_hash_from_value(args[0])
    if not bookmarks_hash or bookmarks_hash not in _session_bookmarks:
        return Value.list_val([])
    
    query = args[1].data if args[1].type == ValueType.STRING else ""
    
    bookmarks_part = _session_bookmarks[bookmarks_hash]
    results = bookmarks_part.search(query)
    
    return Value.list_val([foghorn_to_tinytalk(b) for b in results])


def builtin_bookmarks_recent(args: List[Value]) -> Value:
    """
    Get recent bookmarks.
    
    Usage:
        let recent = Bookmarks.recent(bookmarks)
        let recent = Bookmarks.recent(bookmarks, 5)
    """
    if not args:
        return Value.list_val([])
    
    bookmarks_hash = _get_hash_from_value(args[0])
    if not bookmarks_hash or bookmarks_hash not in _session_bookmarks:
        return Value.list_val([])
    
    limit = 10
    if len(args) > 1 and args[1].type == ValueType.INT:
        limit = args[1].data
    
    bookmarks_part = _session_bookmarks[bookmarks_hash]
    recent = bookmarks_part.get_recent(limit)
    
    return Value.list_val([foghorn_to_tinytalk(b) for b in recent])


# ═══════════════════════════════════════════════════════════════════════════════
# CYBERDOG SUITE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

_cyberdog_instance: Dict[str, CyberDogSuite] = {}


def builtin_cyberdog_new(args: List[Value]) -> Value:
    """
    Create a complete CyberDog suite with all components.
    
    Usage:
        let suite = CyberDog.new()
    """
    suite = create_cyberdog()
    _cyberdog_instance[suite.document.hash] = suite
    
    # Register all components
    _session_browsers[suite.browser.hash] = suite.browser
    _session_emails[suite.email.hash] = suite.email
    _session_news[suite.news.hash] = suite.news
    _session_ftp[suite.ftp.hash] = suite.ftp
    _session_contacts[suite.address_book.hash] = suite.address_book
    _session_bookmarks[suite.bookmarks.hash] = suite.bookmarks
    
    return foghorn_to_tinytalk(suite)


def builtin_cyberdog_verify(args: List[Value]) -> Value:
    """
    Verify all CyberDog components.
    
    Usage:
        let results = CyberDog.verify(suite)
    """
    if not args:
        return Value.null_val()
    
    doc_hash = _get_hash_from_value(args[0])
    if not doc_hash or doc_hash not in _cyberdog_instance:
        # Try document hash from suite dict
        if args[0].type == ValueType.MAP and "document" in args[0].data:
            doc_data = args[0].data["document"]
            if hasattr(doc_data, 'data') and isinstance(doc_data.data, dict):
                doc_hash = doc_data.data.get("hash", Value.null_val())
                if hasattr(doc_hash, 'data'):
                    doc_hash = doc_hash.data
    
    if doc_hash and doc_hash in _cyberdog_instance:
        suite = _cyberdog_instance[doc_hash]
        results = suite.verify_all()
        return foghorn_to_tinytalk(results)
    
    return Value.null_val()


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_hash_from_value(val: Value) -> str:
    """Extract hash from a TinyTalk value representing an object."""
    if val.type == ValueType.STRING:
        return val.data
    
    if val.type == ValueType.MAP and "hash" in val.data:
        hash_val = val.data["hash"]
        if hasattr(hash_val, 'data'):
            return hash_val.data
        return str(hash_val)
    
    return ""


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER ALL BUILTINS
# ═══════════════════════════════════════════════════════════════════════════════

OPENDOC_CYBERDOG_BUILTINS = {
    # Document
    'Document.new': builtin_document_new,
    'Document.get': builtin_document_get,
    'Document.add': builtin_document_add,
    'Document.verify': builtin_document_verify,
    'Document.all': builtin_document_all,
    'Document.serialize': builtin_document_serialize,
    
    # Part
    'Part.new': builtin_part_new,
    'Part.verify': builtin_part_verify,
    'TextPart.new': builtin_textpart_new,
    'TablePart.new': builtin_tablepart_new,
    'PartType.list': builtin_parttype_list,
    
    # Browser (CyberDog)
    'Browser.new': builtin_browser_new,
    'Browser.navigate': builtin_browser_navigate,
    'Browser.back': builtin_browser_back,
    'Browser.forward': builtin_browser_forward,
    'Browser.history': builtin_browser_history,
    
    # Email (CyberDog)
    'Email.new': builtin_email_new,
    'Email.compose': builtin_email_compose,
    'Email.send': builtin_email_send,
    'Email.inbox': builtin_email_inbox,
    'Email.drafts': builtin_email_drafts,
    
    # News (CyberDog)
    'News.new': builtin_news_new,
    'News.subscribe': builtin_news_subscribe,
    'News.refresh': builtin_news_refresh,
    'News.unread': builtin_news_unread,
    
    # FTP (CyberDog)
    'FTP.new': builtin_ftp_new,
    'FTP.connect': builtin_ftp_connect,
    'FTP.list': builtin_ftp_list,
    'FTP.download': builtin_ftp_download,
    
    # Contacts (CyberDog)
    'Contacts.new': builtin_contacts_new,
    'Contacts.add': builtin_contacts_add,
    'Contacts.search': builtin_contacts_search,
    'Contacts.all': builtin_contacts_all,
    
    # Bookmarks (CyberDog)
    'Bookmarks.new': builtin_bookmarks_new,
    'Bookmarks.add': builtin_bookmarks_add,
    'Bookmarks.search': builtin_bookmarks_search,
    'Bookmarks.recent': builtin_bookmarks_recent,
    
    # CyberDog Suite
    'CyberDog.new': builtin_cyberdog_new,
    'CyberDog.verify': builtin_cyberdog_verify,
}


def register_opendoc_cyberdog_stdlib(runtime):
    """Register OpenDoc/CyberDog builtins with a TinyTalk runtime."""
    from realTinyTalk.runtime import TinyFunction
    from realTinyTalk.types import ValueType
    
    for name, fn in OPENDOC_CYBERDOG_BUILTINS.items():
        # Create a native function wrapper
        func = TinyFunction(
            name=name,
            params=[],
            body=None,
            closure=runtime.global_scope,
            is_native=True,
            native_fn=fn,
        )
        
        # Handle dotted names (Document.new -> Document object with new method)
        if '.' in name:
            parts = name.split('.')
            obj_name, method_name = parts[0], parts[1]
            
            # Get or create the namespace object
            ns = runtime.global_scope.get(obj_name)
            if ns is None or ns.type != ValueType.MAP:
                ns = Value.map_val({})
                runtime.global_scope.define(obj_name, ns)
            
            # Add method
            ns.data[method_name] = Value(ValueType.FUNCTION, func)
        else:
            # Simple function
            runtime.global_scope.define(name, Value(ValueType.FUNCTION, func))
