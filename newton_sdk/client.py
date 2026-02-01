"""
═══════════════════════════════════════════════════════════════════════════════
 Newton Client - Connect to Newton Supercomputer
═══════════════════════════════════════════════════════════════════════════════
"""

import requests
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


class NewtonError(Exception):
    """Error from Newton server."""
    def __init__(self, message: str, code: int = None, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


@dataclass
class VerificationResult:
    """Result of a verification request."""
    verified: bool
    code: int
    content: dict
    signal: dict
    elapsed_us: int


@dataclass
class CalculationResult:
    """Result of a calculation request."""
    result: Any
    type: str
    verified: bool
    operations: int
    elapsed_us: int
    fingerprint: str


@dataclass
class ConstraintResult:
    """Result of a constraint evaluation."""
    result: bool
    terminates: bool
    elapsed_us: int


class Newton:
    """
    Client for Newton Supercomputer.

    Usage:
        newton = Newton()  # Connects to localhost:8000
        newton = Newton("https://newton-api-1.onrender.com")  # Remote server

        # Calculate
        result = newton.calculate({"op": "+", "args": [2, 3]})
        print(result.result)  # 5

        # Verify content
        result = newton.verify("Is this safe?")
        print(result.verified)  # True

        # Check constraint
        result = newton.constraint(
            {"field": "balance", "operator": "ge", "value": 0},
            {"balance": 100}
        )
        print(result.result)  # True
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._session = requests.Session()

        if api_key:
            self._session.headers["Authorization"] = f"Bearer {api_key}"

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
        params: dict = None
    ) -> dict:
        """Make a request to Newton."""
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = self._session.get(
                    url, params=params, timeout=self.timeout
                )
            else:
                response = self._session.post(
                    url, json=data, timeout=self.timeout
                )

            if response.status_code >= 400:
                raise NewtonError(
                    f"Newton returned {response.status_code}",
                    code=response.status_code,
                    details=response.json() if response.text else {}
                )

            return response.json()

        except requests.exceptions.ConnectionError:
            raise NewtonError(
                f"Cannot connect to Newton at {self.base_url}. "
                "Is the server running? Start with: newton serve"
            )
        except requests.exceptions.Timeout:
            raise NewtonError(f"Request timed out after {self.timeout}s")

    # ═══════════════════════════════════════════════════════════════════════
    # Core API
    # ═══════════════════════════════════════════════════════════════════════

    def health(self) -> dict:
        """Check server health."""
        return self._request("GET", "/health")

    def ask(self, query: str) -> dict:
        """Ask Newton anything (full verification pipeline)."""
        return self._request("POST", "/ask", {"query": query})

    def verify(self, content: str) -> VerificationResult:
        """Verify content against safety constraints."""
        result = self._request("POST", "/verify", {"input": content})
        return VerificationResult(
            verified=result.get("verified", False),
            code=result.get("code", 0),
            content=result.get("content", {}),
            signal=result.get("signal", {}),
            elapsed_us=result.get("elapsed_us", 0)
        )

    def calculate(self, expression: dict) -> CalculationResult:
        """
        Execute verified computation.

        Expression format:
            {"op": "+", "args": [2, 3]}
            {"op": "*", "args": [{"op": "+", "args": [1, 2]}, 4]}

        Operators: +, -, *, /, %, **, and, or, not, ==, !=, <, >, <=, >=,
                   if, for, while, map, filter, reduce, def, call, lambda
        """
        result = self._request("POST", "/calculate", {"expression": expression})
        return CalculationResult(
            result=result.get("result"),
            type=result.get("type", "unknown"),
            verified=result.get("verified", False),
            operations=result.get("operations", 0),
            elapsed_us=result.get("elapsed_us", 0),
            fingerprint=result.get("fingerprint", "")
        )

    def constraint(
        self,
        constraint: dict,
        obj: dict
    ) -> ConstraintResult:
        """
        Evaluate a CDL constraint against an object.

        Constraint format:
            {"field": "balance", "operator": "ge", "value": 0}
            {"logic": "and", "constraints": [...]}

        Operators: eq, ne, lt, gt, le, ge, contains, matches, in, not_in,
                   exists, empty, within, after, before
        """
        result = self._request("POST", "/constraint", {
            "constraint": constraint,
            "object": obj
        })
        return ConstraintResult(
            result=result.get("result", False),
            terminates=result.get("terminates", True),
            elapsed_us=result.get("elapsed_us", 0)
        )

    def ground(
        self,
        claim: str,
        confidence: float = 0.8
    ) -> dict:
        """Ground a claim in external evidence."""
        return self._request("POST", "/ground", {
            "claim": claim,
            "confidence": confidence
        })

    def statistics(self, data: List[float], locked: bool = False) -> dict:
        """Calculate robust statistics (MAD over mean)."""
        return self._request("POST", "/statistics", {
            "data": data,
            "locked": locked
        })

    # ═══════════════════════════════════════════════════════════════════════
    # Storage & Audit
    # ═══════════════════════════════════════════════════════════════════════

    def vault_store(self, key: str, value: Any, identity: str) -> dict:
        """Store encrypted data in the vault."""
        return self._request("POST", "/vault/store", {
            "key": key,
            "value": value,
            "identity": identity
        })

    def vault_retrieve(self, key: str, identity: str) -> dict:
        """Retrieve encrypted data from the vault."""
        return self._request("POST", "/vault/retrieve", {
            "key": key,
            "identity": identity
        })

    def ledger(self, limit: int = 100) -> List[dict]:
        """View the immutable audit trail."""
        result = self._request("GET", "/ledger", params={"limit": limit})
        return result.get("entries", [])

    def ledger_entry(self, index: int) -> dict:
        """Get a specific ledger entry with Merkle proof."""
        return self._request("GET", f"/ledger/{index}")

    # ═══════════════════════════════════════════════════════════════════════
    # Cartridges (Media Specification)
    # ═══════════════════════════════════════════════════════════════════════

    def cartridge_visual(self, description: str, **kwargs) -> dict:
        """Generate SVG/image specification."""
        return self._request("POST", "/cartridge/visual", {
            "description": description,
            **kwargs
        })

    def cartridge_sound(self, description: str, **kwargs) -> dict:
        """Generate audio specification."""
        return self._request("POST", "/cartridge/sound", {
            "description": description,
            **kwargs
        })

    def cartridge_sequence(self, description: str, **kwargs) -> dict:
        """Generate video/animation specification."""
        return self._request("POST", "/cartridge/sequence", {
            "description": description,
            **kwargs
        })

    def cartridge_data(self, description: str, **kwargs) -> dict:
        """Generate report specification."""
        return self._request("POST", "/cartridge/data", {
            "description": description,
            **kwargs
        })

    def cartridge_rosetta(self, description: str, language: str, **kwargs) -> dict:
        """Generate code generation prompt."""
        return self._request("POST", "/cartridge/rosetta", {
            "description": description,
            "language": language,
            **kwargs
        })

    # ═══════════════════════════════════════════════════════════════════════
    # Convenience Methods
    # ═══════════════════════════════════════════════════════════════════════

    def add(self, a: float, b: float) -> float:
        """Verified addition."""
        return float(self.calculate({"op": "+", "args": [a, b]}).result)

    def subtract(self, a: float, b: float) -> float:
        """Verified subtraction."""
        return float(self.calculate({"op": "-", "args": [a, b]}).result)

    def multiply(self, a: float, b: float) -> float:
        """Verified multiplication."""
        return float(self.calculate({"op": "*", "args": [a, b]}).result)

    def divide(self, a: float, b: float) -> float:
        """Verified division."""
        return float(self.calculate({"op": "/", "args": [a, b]}).result)

    def is_safe(self, content: str) -> bool:
        """Quick check if content is safe."""
        return self.verify(content).verified

    def __repr__(self):
        return f"Newton('{self.base_url}')"
