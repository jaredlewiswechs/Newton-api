"""Simple client examples for the Teacher's Aide service.

Demonstrates calling `/search` and `/logic/evaluate`.
"""
import requests

BASE = "http://127.0.0.1:8088"
API_KEY = "demo-key"
HEADERS = {"x-api-key": API_KEY}


def example_search(q: str):
    r = requests.get(f"{BASE}/search", params={"q": q, "limit": 3}, headers=HEADERS)
    print("SEARCH", r.status_code, r.json())


def example_logic():
    # Simple expression: 1 + 2 == 3
    expr = {"type": "literal", "args": [1]}  # trivial literal example
    payload = {"expr": {"type": "add", "args": [{"type": "literal", "args": [1]}, {"type": "literal", "args": [2]}]}}
    r = requests.post(f"{BASE}/logic/evaluate", json=payload, headers=HEADERS)
    print("EVAL", r.status_code, r.json())


if __name__ == "__main__":
    example_search("fractions")
    example_logic()
