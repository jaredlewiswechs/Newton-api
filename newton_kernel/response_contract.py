# Unified Response Contract
# This module defines the standard response schema for all Newton modules.

from typing import List, Dict, Any

class ResponseContract:
    def __init__(self, content: Any, verdict: str, provenance: List[Dict[str, Any]], bounds: Dict[str, Any], trace_id: str):
        self.content = content
        self.verdict = verdict
        self.provenance = provenance
        self.bounds = bounds
        self.trace_id = trace_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "verdict": self.verdict,
            "provenance": self.provenance,
            "bounds": self.bounds,
            "trace_id": self.trace_id,
        }

# Example usage
# response = ResponseContract(
#     content="Result",
#     verdict="verified",
#     provenance=[{"source": "KB", "hash": "abc123"}],
#     bounds={"ops": 100, "time": 0.5, "depth": 3},
#     trace_id="unique-trace-id"
# )
# print(response.to_dict())