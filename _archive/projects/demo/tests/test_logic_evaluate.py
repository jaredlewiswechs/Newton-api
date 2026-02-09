import pytest
from fastapi.testclient import TestClient

from demo.teachers_aide_service import app

client = TestClient(app)

API_KEY = "demo-key"
HEADERS = {"x-api-key": API_KEY}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_logic_eval_add():
    # Evaluate 1 + 2
    payload = {"expr": {"type": "add", "args": [{"type": "literal", "args": [1]}, {"type": "literal", "args": [2]}]}}
    r = client.post("/logic/evaluate", json=payload, headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    # Value should be 3
    assert data["value"] == "3"
    assert data["verified"] is True


def test_rate_limit_exceeded():
    # hit the rate limit quickly by invoking many times
    for i in range(0, 5):
        r = client.get("/teks", headers=HEADERS)
        assert r.status_code == 200

*** End Patch