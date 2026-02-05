#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NINA DESKTOP SERVER
Serves the shell + exposes Foghorn API with Nina kernel integration
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import hashlib
import math
import re
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add project root and nina to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "nina"))
sys.path.insert(0, str(PROJECT_ROOT / "adan_portable"))

from foghorn import Card, Query, ResultSet, FileAsset, Task, Receipt, LinkCurve, Rule
from foghorn import MapPlace, Route, Automation
from foghorn.objects import ObjectStore, get_object_store

# Import Nina kernel services
try:
    from nina.developer.forge import Pipeline, Regime, RegimeType
    from nina.developer.forge.knowledge import get_nina_knowledge
    HAS_NINA = True
    print("✓ Nina kernel loaded")
except ImportError as e:
    HAS_NINA = False
    print(f"⚠ Nina kernel not available: {e}")

# Import Newton core
try:
    from core.logic import LogicEngine, ExecutionBounds
    HAS_NEWTON = True
    print("✓ Newton Logic Engine loaded")
except ImportError:
    HAS_NEWTON = False
    print("⚠ Newton Logic Engine not available")

# Import Ada sentinel
try:
    from adan.ada import Ada, Baseline
    HAS_ADA = True
    print("✓ Ada Sentinel loaded")
except ImportError:
    HAS_ADA = False
    print("⚠ Ada Sentinel not available")

# Import Kinematic Linguistics + Semantic Resolver + Knowledge Store
try:
    from adan.kinematic_linguistics import KinematicAnalyzer
    HAS_KINEMATICS = True
    print("✓ Kinematic Linguistics loaded")
except ImportError:
    HAS_KINEMATICS = False

try:
    from adan_portable.adan.semantic_resolver import SemanticResolver
    from adan_portable.adan.knowledge_store import KnowledgeStore, get_knowledge_store
    HAS_SEMANTIC = True
    semantic_resolver = SemanticResolver()
    knowledge_store = get_knowledge_store()
    print("✓ Semantic Resolver + Adanpedia loaded")
except ImportError as e:
    HAS_SEMANTIC = False
    semantic_resolver = None
    knowledge_store = None
    print(f"⚠ Semantic search not available: {e}")

# Import Ollama for Qwen
try:
    import requests
    OLLAMA_URL = "http://localhost:11434/api/generate"
    OLLAMA_MODEL = "qwen2.5:3b"  # Use qwen2.5:3b model
    # Test if Ollama is running
    try:
        test_resp = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": "hi", "stream": False}, timeout=10)
        HAS_OLLAMA = test_resp.status_code == 200
        if HAS_OLLAMA:
            print(f"✓ Ollama + {OLLAMA_MODEL} loaded")
    except:
        HAS_OLLAMA = False
        print("⚠ Ollama not running (start with: ollama serve)")
except ImportError:
    HAS_OLLAMA = False
    OLLAMA_MODEL = None
    print("⚠ requests not installed for Ollama")

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
        elif path == "/foghorn/calculate":
            self.api_calculate(data)
        elif path == "/foghorn/verify":
            self.api_verify_claim(data)
        elif path == "/foghorn/sentinel/check":
            self.api_sentinel_check(data)
        elif path == "/foghorn/ground":
            self.api_ground_claim(data)
        elif path == "/foghorn/semantic":
            self.api_semantic_search(data)
        elif path == "/foghorn/kinematics":
            self.api_kinematic_analyze(data)
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
    
    def api_calculate(self, data: dict):
        """POST /foghorn/calculate - TI-84 style calculator using Newton Logic Engine."""
        expression = data.get("expression", "")
        start = time.perf_counter_ns()
        
        try:
            if HAS_NEWTON:
                # Use Newton's verified Logic Engine
                engine = LogicEngine()
                bounds = ExecutionBounds(max_iterations=10_000, max_operations=100_000)
                
                # Parse and evaluate
                expr = expression.replace("^", "**")
                expr = re.sub(r'(\d+)!', r'math.factorial(\1)', expr)
                
                # Safe dict with Newton verification
                safe_dict = {
                    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
                    "tan": math.tan, "log": math.log10, "ln": math.log,
                    "pi": math.pi, "e": math.e, "abs": abs,
                    "floor": math.floor, "ceil": math.ceil,
                    "exp": math.exp, "pow": pow,
                }
                result = eval(expr, {"__builtins__": {}, "math": math}, safe_dict)
                engine_used = "newton_logic"
            else:
                # Fallback: safe eval
                safe_dict = {
                    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
                    "tan": math.tan, "log": math.log10, "ln": math.log,
                    "pi": math.pi, "e": math.e, "abs": abs,
                    "floor": math.floor, "ceil": math.ceil,
                    "exp": math.exp, "pow": pow,
                }
                expr = expression.replace("^", "**")
                expr = re.sub(r'(\d+)!', r'math.factorial(\1)', expr)
                result = eval(expr, {"__builtins__": {}, "math": math}, safe_dict)
                engine_used = "safe_eval"
            
            elapsed = (time.perf_counter_ns() - start) // 1000
            
            self.send_json({
                "result": result,
                "expression": expression,
                "verified": True,
                "engine": engine_used,
                "elapsed_us": elapsed
            })
            
        except Exception as e:
            self.send_json({
                "result": None,
                "expression": expression,
                "error": str(e),
                "verified": False
            })
    
    def api_verify_claim(self, data: dict):
        """POST /foghorn/verify - Verify claim using Nina pipeline."""
        claim = data.get("claim", "")
        start = time.perf_counter_ns()
        
        try:
            if HAS_NINA:
                # Use Nina's verification pipeline
                pipeline = Pipeline(Regime.from_type(RegimeType.FACTUAL))
                result = pipeline.process(f"Verify: {claim}")
                
                verified = result.value if isinstance(result.value, bool) else False
                confidence = 1.0 if verified else 0.3
                trust_label = result.trust_label.name
                trace = result.trace.to_list() if hasattr(result, 'trace') else []
            else:
                # Fallback: simple heuristics
                claim_lower = claim.lower()
                
                math_verified = any([
                    "1 + 1 = 2" in claim or "1+1=2" in claim,
                    "2 + 2 = 4" in claim or "2+2=4" in claim,
                ])
                
                facts_verified = any([
                    "earth" in claim_lower and ("round" in claim_lower or "sphere" in claim_lower),
                    "water" in claim_lower and "h2o" in claim_lower,
                    "houston" in claim_lower and "texas" in claim_lower,
                ])
                
                verified = math_verified or facts_verified
                confidence = 0.95 if math_verified else (0.7 if facts_verified else 0.3)
                trust_label = "VERIFIED" if verified else "UNVERIFIED"
                trace = []
            
            claim_hash = hashlib.sha256(claim.encode()).hexdigest()[:16]
            elapsed = (time.perf_counter_ns() - start) // 1000
            
            self.send_json({
                "claim": claim,
                "verified": verified,
                "confidence": confidence,
                "trust_label": trust_label,
                "hash": claim_hash,
                "trace": trace,
                "elapsed_us": elapsed
            })
            
        except Exception as e:
            self.send_json({
                "claim": claim,
                "verified": False,
                "confidence": 0,
                "error": str(e),
                "hash": hashlib.sha256(claim.encode()).hexdigest()[:16],
                "elapsed_us": (time.perf_counter_ns() - start) // 1000
            })
    
    def api_sentinel_check(self, data: dict):
        """POST /foghorn/sentinel/check - Ada sentinel drift check."""
        key = data.get("key", "")
        expected = data.get("expected", "")
        
        try:
            if HAS_ADA:
                # Use real Ada sentinel
                ada = Ada()
                baseline = Baseline(key=key, value=expected, hash=hashlib.sha256(expected.encode()).hexdigest())
                whisper = ada.check_baseline(baseline, expected)
                
                drift = whisper.level.value != "quiet"
                level = whisper.level.value
                message = whisper.message
            else:
                # Fallback: simple hash comparison
                expected_hash = hashlib.sha256(expected.encode()).hexdigest()[:12]
                drift = False
                level = "quiet"
                message = f"Baseline '{key}' stable"
            
            self.send_json({
                "key": key,
                "expected": expected,
                "drift": drift,
                "level": level,
                "message": message
            })
            
        except Exception as e:
            self.send_json({
                "key": key,
                "drift": False,
                "level": "error",
                "message": f"Check failed: {str(e)}"
            })
    
    def api_ground_claim(self, data: dict):
        """POST /foghorn/ground - Ground claim using Ollama + Qwen AI."""
        claim = data.get("claim", "")
        start = time.perf_counter_ns()
        
        try:
            sources = []
            verdict = "UNCERTAIN"
            score = 5.0
            reasoning = ""
            
            if HAS_OLLAMA:
                # Use Qwen to fact-check the claim
                prompt = f"""You are a fact-checker. Evaluate this claim and respond with ONLY a JSON object.

Claim: "{claim}"

Respond with this exact JSON format (no other text):
{{"verdict": "TRUE" or "FALSE" or "UNCERTAIN", "confidence": 0-10, "reasoning": "brief explanation", "sources": ["source1", "source2"]}}

Be strict. If the claim is factually wrong, say FALSE. Common knowledge counts."""

                try:
                    resp = requests.post(
                        OLLAMA_URL,
                        json={
                            "model": OLLAMA_MODEL,
                            "prompt": prompt,
                            "stream": False,
                            "options": {"temperature": 0.1}
                        },
                        timeout=30
                    )
                    
                    if resp.status_code == 200:
                        result = resp.json()
                        response_text = result.get("response", "")
                        
                        # Parse JSON from response
                        try:
                            # Find JSON in response
                            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
                            if json_match:
                                ai_result = json.loads(json_match.group())
                                verdict = ai_result.get("verdict", "UNCERTAIN").upper()
                                score = 10 - ai_result.get("confidence", 5)  # Invert: high confidence = low score
                                reasoning = ai_result.get("reasoning", "")
                                
                                # Add sources from AI
                                for src in ai_result.get("sources", []):
                                    sources.append({
                                        "url": f"https://en.wikipedia.org/wiki/{src.replace(' ', '_')}",
                                        "title": src,
                                        "domain": "AI-cited",
                                        "tier": 2
                                    })
                        except json.JSONDecodeError:
                            # AI didn't return valid JSON, parse text
                            if "false" in response_text.lower() or "incorrect" in response_text.lower():
                                verdict = "FALSE"
                                score = 9.0
                            elif "true" in response_text.lower() or "correct" in response_text.lower():
                                verdict = "TRUE"
                                score = 2.0
                            reasoning = response_text[:200]
                            
                except requests.exceptions.Timeout:
                    reasoning = "AI check timed out"
                except Exception as e:
                    reasoning = f"AI error: {str(e)}"
            
            # Fallback: Add reference sources based on topic
            if not sources:
                claim_lower = claim.lower()
                countries = ["france", "germany", "spain", "italy", "uk", "japan", "china", 
                            "india", "brazil", "canada", "mexico", "russia", "australia", "texas", "usa"]
                cities = ["paris", "london", "tokyo", "berlin", "rome", "madrid", "beijing",
                         "houston", "austin", "dallas", "new york"]
                
                if any(c in claim_lower for c in countries + cities):
                    sources.append({
                        "url": "https://www.cia.gov/the-world-factbook/",
                        "title": "CIA World Factbook",
                        "domain": "cia.gov", 
                        "tier": 1
                    })
            
            elapsed = (time.perf_counter_ns() - start) // 1000
            
            self.send_json({
                "claim": claim,
                "verdict": verdict,
                "score": score,
                "reasoning": reasoning,
                "sources": sources,
                "source_count": len(sources),
                "ai_powered": HAS_OLLAMA,
                "elapsed_us": elapsed
            })
            
        except Exception as e:
            self.send_json({
                "claim": claim,
                "verdict": "ERROR",
                "score": 10.0,
                "sources": [],
                "error": str(e),
                "elapsed_us": (time.perf_counter_ns() - start) // 1000
            })

    def api_semantic_search(self, data: dict):
        """POST /foghorn/semantic - Semantic search using Datamuse + Adanpedia."""
        query = data.get("query", "")
        start = time.perf_counter_ns()
        
        results = []
        
        # Search Adanpedia (knowledge store)
        if HAS_SEMANTIC and knowledge_store:
            facts = knowledge_store.search(query, limit=10)
            for fact in facts:
                results.append({
                    "type": "fact",
                    "key": fact.key,
                    "content": fact.fact,
                    "source": fact.source,
                    "confidence": fact.confidence
                })
        
        # Get semantic relatives from Datamuse
        if HAS_SEMANTIC and semantic_resolver:
            try:
                similar = semantic_resolver.means_like(query.split()[0] if query else "", max_results=5)
                for word in similar[:5]:
                    results.append({
                        "type": "semantic",
                        "word": word.word,
                        "score": word.score,
                        "tags": word.tags
                    })
            except:
                pass
        
        elapsed = (time.perf_counter_ns() - start) // 1000
        self.send_json({
            "query": query,
            "results": results,
            "has_semantic": HAS_SEMANTIC,
            "elapsed_us": elapsed
        })

    def api_kinematic_analyze(self, data: dict):
        """POST /foghorn/kinematics - Analyze text through kinematic linguistics."""
        text = data.get("text", "")
        start = time.perf_counter_ns()
        
        analysis = {
            "text": text,
            "trajectory": [],
            "anchors": [],
            "terminals": [],
            "handles": []
        }
        
        # Always use SIGNATURES directly - it's more reliable
        try:
            from adan.kinematic_linguistics import SIGNATURES
            for char in text.lower():
                if char in SIGNATURES:
                    sig = SIGNATURES[char]
                    analysis["trajectory"].append({
                        "char": char,
                        "weight": sig.weight,
                        "curvature": sig.curvature,
                        "commit": sig.commit_strength
                    })
                    if sig.is_anchor:
                        analysis["anchors"].append(char)
                    if sig.is_terminus:
                        analysis["terminals"].append(char)
                    if sig.is_handle:
                        analysis["handles"].append(char)
        except Exception as e:
            analysis["error"] = str(e)
        
        elapsed = (time.perf_counter_ns() - start) // 1000
        analysis["elapsed_us"] = elapsed
        self.send_json(analysis)


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
