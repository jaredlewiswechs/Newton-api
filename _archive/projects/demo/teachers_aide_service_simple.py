"""Lightweight fallback HTTP server for Teacher's Aide service.

Uses Python stdlib `http.server` to provide basic JSON endpoints without
FastAPI (for environments where FastAPI/Pydantic import fails).

Endpoints:
- GET /health
- GET /teks
- GET /teks/{code}
- GET /search?q=...
- POST /logic/evaluate
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional

from tinytalk_py.education import get_teks_library
from core.logic import LogicEngine, ExecutionContext
from core.ti_calc import bounded_normalized_distance, citation_score, combine_scores
from demo.adanpedia_adapter import fetch_examples

API_KEY = "demo-key"


def _require_api_key(headers) -> bool:
    key = headers.get("x-api-key")
    return key == API_KEY


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        # Auth
        if not _require_api_key(self.headers):
            return self._send(401, {"detail": "Invalid or missing API key"})

        if path == "/health":
            return self._send(200, {"status": "ok"})

        if path == "/teks":
            q = qs.get("q", [None])[0]
            teks = get_teks_library()
            if not q:
                return self._send(200, {"count": len(teks), "keys": list(teks.keys())})
            keys = [k for k, v in teks.items() if q.lower() in (v.skill_statement + v.knowledge_statement).lower()]
            return self._send(200, {"count": len(keys), "keys": keys})

        if path.startswith("/teks/"):
            code = path.split("/", 2)[2]
            teks = get_teks_library()
            std = teks.get(code)
            if not std:
                return self._send(404, {"detail": "TEKS not found"})
            return self._send(200, {
                "code": std.code,
                "grade": std.grade,
                "subject": str(std.subject.value),
                "knowledge": std.knowledge_statement,
                "skill": std.skill_statement,
            })

        if path == "/search":
            q = qs.get("q", [None])[0]
            limit = int(qs.get("limit", [5])[0])
            if not q:
                return self._send(400, {"detail": "Missing q"})
            teks = get_teks_library()
            try:
                teks_results = teks.search(q)
                teks_hits = [{"code": r.code, "skill": r.skill_statement} for r in teks_results[:limit]]
            except Exception:
                teks_hits = []
            examples = fetch_examples(handles=[q], max_examples=limit)
            # try portable store
            portable_hits = []
            try:
                from adan.knowledge_store import get_knowledge_store
                ks = get_knowledge_store()
                facts = ks.search(q, limit=limit)
                portable_hits = [{"id": f.id, "key": f.key, "snippet": f.fact} for f in facts]
            except Exception:
                portable_hits = []
            return self._send(200, {"query": q, "teks": teks_hits, "examples": examples, "portable": portable_hits})

        return self._send(404, {"detail": "Not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Auth
        if not _require_api_key(self.headers):
            return self._send(401, {"detail": "Invalid or missing API key"})

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length else ""
        try:
            data = json.loads(body) if body else {}
        except Exception:
            return self._send(400, {"detail": "Invalid JSON"})

        if path == "/logic/evaluate":
            expr = data.get("expr")
            if expr is None:
                return self._send(400, {"detail": "Missing expr"})
            engine = LogicEngine()
            ctx = ExecutionContext()
            result = engine.evaluate(expr, context=ctx)
            out = result.to_dict()
            out["trace"] = result.trace
            return self._send(200, out)

        if path == "/ti/bounded_distance":
            score = bounded_normalized_distance(data.get("value"), data.get("lo"), data.get("hi"))
            return self._send(200, {"score": score})

        if path == "/ti/citation_score":
            score = citation_score(data.get("required", True), data.get("found", 0), data.get("min_required"))
            return self._send(200, {"score": score})

        if path == "/ti/combine":
            scores = data or {}
            return self._send(200, {"combined": combine_scores(scores)})

        return self._send(404, {"detail": "Not found"})


def run(host: str = "127.0.0.1", port: int = 8088):
    server = HTTPServer((host, port), Handler)
    print(f"Teacher's Aide simple server running at http://{host}:{port} (API key: {API_KEY})")
    server.serve_forever()


if __name__ == "__main__":
    run()
