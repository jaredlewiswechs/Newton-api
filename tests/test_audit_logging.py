import os
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.intake_api import router as intake_router

app = FastAPI()
app.include_router(intake_router, prefix="/api")
client = TestClient(app)


def test_intake_writes_audit_log():
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "audit.log")
    # remove old log if present
    try:
        if os.path.exists(log_path):
            os.remove(log_path)
    except Exception:
        pass

    resp = client.post("/api/intake", json={"prompt": "Write 200-300 words due 2026-02-14."})
    assert resp.status_code == 200
    # Allow slight delay for async write
    time.sleep(0.5)
    assert os.path.exists(log_path)
    with open(log_path, "r", encoding="utf-8") as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    assert any('"operation": "intake"' in l for l in lines)
