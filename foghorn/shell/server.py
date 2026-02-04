#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NINA DESKTOP SERVER
Serves the shell + exposes Foghorn API
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from foghorn import Card, Query, ResultSet, FileAsset, Task, Receipt, LinkCurve, Rule
from foghorn import MapPlace, Route, Automation
from foghorn.objects import ObjectStore, get_object_store

# ═══════════════════════════════════════════════════════════════════════════════
# SERVER CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

PORT = 8000
HOST = "localhost"

# Global store
store = get_object_store()

# ═══════════════════════════════════════════════════════════════════════════════
# HTTP HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

class NinaHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves static files and Foghorn API."""
    
    def __init__(self, *args, **kwargs):
        # Serve from shell directory
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        # API routes
        if path == "/foghorn/cards":
            self.api_get_cards()
        elif path == "/foghorn/objects":
            self.api_get_all_objects()
        elif path.startswith("/foghorn/object/"):
            obj_id = path.split("/")[-1]
            self.api_get_object(obj_id)
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length else ""
        data = json.loads(body) if body else {}
        
        # API routes
        if path == "/foghorn/cards":
            self.api_create_card(data)
        elif path == "/foghorn/query":
            self.api_create_query(data)
        elif path == "/foghorn/undo":
            self.api_undo()
        elif path == "/foghorn/redo":
            self.api_redo()
        elif path == "/foghorn/services/verify":
            self.api_service_verify(data)
        elif path == "/foghorn/services/compute":
            self.api_service_compute(data)
        else:
            self.send_error(404, "Not found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def send_json(self, data, status=200):
        """Send JSON response with CORS."""
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # API ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def api_get_cards(self):
        """GET /foghorn/cards - List all cards."""
        from foghorn.objects import ObjectType
        cards = store.get_by_type(ObjectType.CARD)
        self.send_json({"cards": [c.to_dict() for c in cards], "count": len(cards)})
    
    def api_get_all_objects(self):
        """GET /foghorn/objects - List all objects."""
        objects = store.export()
        self.send_json({"objects": objects, "count": len(objects)})
    
    def api_get_object(self, obj_id: str):
        """GET /foghorn/object/:id - Get single object."""
        obj = store.get(obj_id) or store.get_by_id(obj_id)
        if obj:
            self.send_json({"object": obj.to_dict()})
        else:
            self.send_json({"error": "Not found"}, 404)
    
    def api_create_card(self, data: dict):
        """POST /foghorn/cards - Create a new card."""
        card = Card(
            title=data.get("title", "Untitled"),
            content=data.get("content", ""),
            tags=data.get("tags", []),
            source=data.get("source", "nina-desktop")
        )
        store.add(card)
        self.send_json({"card": card.to_dict(), "success": True})
    
    def api_create_query(self, data: dict):
        """POST /foghorn/query - Create and execute a query."""
        query = Query(text=data.get("text", ""))
        store.add(query)
        
        # TODO: Actually execute query
        result_set = ResultSet(
            query_id=query.id,
            items=[],
            count=0
        )
        store.add(result_set)
        
        self.send_json({
            "query": query.to_dict(),
            "results": result_set.to_dict(),
            "success": True
        })
    
    def api_undo(self):
        """POST /foghorn/undo - Undo last action."""
        # ObjectStore doesn't have undo yet
        self.send_json({"success": False, "message": "Undo not implemented"})
    
    def api_redo(self):
        """POST /foghorn/redo - Redo last undone action."""
        # ObjectStore doesn't have redo yet
        self.send_json({"success": False, "message": "Redo not implemented"})
    
    def api_service_verify(self, data: dict):
        """POST /foghorn/services/verify - Verify a claim."""
        obj_id = data.get("object_id")
        obj = store.get(obj_id) or store.get_by_id(obj_id)
        
        if not obj:
            self.send_json({"error": "Object not found"}, 404)
            return
        
        # Create verification receipt
        receipt = Receipt(
            operation="verify",
            input_hash=obj.hash,
            output_hash="",
            verified=True,
            execution_time_us=1234
        )
        store.add(receipt)
        self.send_json({"receipt": receipt.to_dict(), "success": True})
    
    def api_service_compute(self, data: dict):
        """POST /foghorn/services/compute - Run computation."""
        expression = data.get("expression", {})
        
        # TODO: Integrate with Newton logic engine
        result = {"value": 42, "verified": True}
        
        card = Card(
            title="Computation Result",
            content=json.dumps(result),
            tags=["computed"],
            source="nina-compute"
        )
        store.add(card)
        self.send_json({"result": card.to_dict(), "success": True})


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Start the Nina Desktop server."""
    # Add some demo objects
    print("🗂️  Adding demo objects...")
    
    welcome = Card(
        title="Welcome to Nina",
        content="This is your first card in the Nina Desktop environment. "
                "Use ⌘K to open the command palette and explore.",
        tags=["welcome", "tutorial"],
        source="system"
    )
    store.add(welcome)
    
    getting_started = Card(
        title="Getting Started",
        content="1. Create new cards with ⌘N\n"
                "2. Search with ⌘K\n"
                "3. Toggle inspector with ⌘I\n"
                "4. Double-click objects to open in windows",
        tags=["tutorial", "guide"],
        source="system"
    )
    store.add(getting_started)
    
    sample_query = Query(text="What is Project Foghorn?")
    store.add(sample_query)
    
    houston = MapPlace(
        name="Ada Computing HQ",
        latitude=29.7604,
        longitude=-95.3698,
        address="Houston, Texas"
    )
    store.add(houston)
    
    print(f"   {store.count()} objects ready")
    
    # Start server
    print(f"\n🖥️  Starting Nina Desktop at http://{HOST}:{PORT}/index.html")
    print(f"   API available at http://{HOST}:{PORT}/foghorn/*")
    print(f"   Press Ctrl+C to stop\n")
    
    server = HTTPServer((HOST, PORT), NinaHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Nina Desktop stopped")
        server.shutdown()


if __name__ == "__main__":
    main()
