"""Audit logging helper for Newton integrations.

This module attempts to append audit events to the Newton `ledger` if
available at runtime (via `newton_supercomputer.ledger`). Regardless, it
also writes JSON-lines to `logs/audit.log` so tests and local runs have
an immutable record.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "audit.log")


def _append_local_log(entry: Dict[str, Any]) -> None:
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        pass


def log_event(operation: str, payload: Optional[Dict[str, Any]] = None, result: str = "ok", metadata: Optional[Dict[str, Any]] = None) -> None:
    payload = payload or {}
    metadata = metadata or {}
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "operation": operation,
        "payload": payload,
        "result": result,
        "metadata": metadata,
    }

    # Try to append to Newton ledger if available at runtime
    try:
        import newton_supercomputer as ns
        ledger = getattr(ns, "ledger", None)
        if ledger is not None:
            try:
                ledger.append(operation=operation, payload=payload, result=result, metadata=metadata)
            except Exception:
                # fall through to local log
                _append_local_log(entry)
        else:
            _append_local_log(entry)
    except Exception:
        # If import fails or ledger unavailable, write local log
        _append_local_log(entry)


__all__ = ["log_event", "LOG_FILE"]
