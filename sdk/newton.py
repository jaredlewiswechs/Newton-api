"""
Newton SDK v3.0 - The Self-Discovering Verified Computation Engine

Just like numpy, but for verified AI:

    from newton import Newton
    n = Newton()

    # Core verification
    result = n.ask("What is 2+2?")
    verified = n.verify("user input", constraints=["no_profanity"])

    # Cartridges
    svg = n.cartridge.visual("a red circle")
    audio = n.cartridge.sound("peaceful melody")
    video = n.cartridge.sequence("bouncing ball animation")
    code = n.cartridge.rosetta("todo app", platform="iOS")

    # Education
    lesson = n.education.lesson(grade=3, subject="math", topic="fractions")

    # Voice (MOAD)
    app = n.voice.ask("build me a todo app")

    # And 100+ more endpoints...

Auto-Discovery:
    - On init, fetches /openapi.json from Newton API
    - Dynamically creates methods for ALL endpoints
    - When you update GitHub → Render deploys → SDK knows new features

    # See what's available
    n.endpoints()  # List all discovered endpoints
    n.help("cartridge")  # Help on cartridge system
    n.capabilities()  # Full capability report

Installation:
    pip install requests  # Only dependency

    # Then just drop this file anywhere:
    from newton import Newton
"""

import requests
import json
import re
import hashlib
import time
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from functools import wraps
import threading
from datetime import datetime

__version__ = "3.0.0"
__author__ = "Newton Verified Computation Engine"

# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_BASE_URL = "https://newton-api.onrender.com"
OPENAPI_PATH = "/openapi.json"
CARTRIDGE_INFO_PATH = "/cartridge/info"
DISCOVERY_CACHE_TTL = 300  # 5 minutes

# =============================================================================
# EXCEPTIONS
# =============================================================================

class NewtonError(Exception):
    """Base exception for Newton SDK"""
    pass

class NewtonConnectionError(NewtonError):
    """Failed to connect to Newton API"""
    pass

class NewtonValidationError(NewtonError):
    """Constraint validation failed"""
    pass

class NewtonAuthError(NewtonError):
    """Authentication failed"""
    pass

class NewtonRateLimitError(NewtonError):
    """Rate limit exceeded"""
    pass

class NewtonVerificationFailed(NewtonError):
    """Verification constraints not satisfied"""
    pass

# =============================================================================
# RESPONSE WRAPPER
# =============================================================================

@dataclass
class NewtonResponse:
    """Wrapper for Newton API responses with verification metadata"""
    success: bool
    data: Any
    verified: bool = False
    constraints_checked: List[str] = field(default_factory=list)
    ledger_index: Optional[int] = None
    merkle_root: Optional[str] = None
    latency_ms: float = 0.0
    raw: Dict = field(default_factory=dict)

    def __repr__(self):
        status = "✓ verified" if self.verified else "○ unverified"
        return f"<NewtonResponse {status} data={type(self.data).__name__}>"

    def __getattr__(self, name):
        """Allow accessing data fields directly"""
        if isinstance(self.data, dict) and name in self.data:
            return self.data[name]
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def __getitem__(self, key):
        """Allow dict-style access to data"""
        if isinstance(self.data, dict):
            return self.data[key]
        return self.data[key]

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "data": self.data,
            "verified": self.verified,
            "constraints_checked": self.constraints_checked,
            "ledger_index": self.ledger_index,
            "merkle_root": self.merkle_root,
            "latency_ms": self.latency_ms
        }

# =============================================================================
# NAMESPACE CLASSES - Generated dynamically but defined for type hints
# =============================================================================

class CartridgeNamespace:
    """
    Cartridge System - Verified media generation

    Five cartridge types:
    - visual: SVG/image specifications
    - sound: Audio specifications
    - sequence: Video/animation specifications
    - data: Report specifications
    - rosetta: Code generation (Swift/Python/TypeScript)
    - auto: Auto-detect cartridge type
    """
    pass

class EducationNamespace:
    """
    Education Module - Teacher support system

    - lesson: NES-compliant lesson plans
    - slides: Slide deck generation
    - assess: Assessment analysis
    - plc: PLC report generation
    - teks: TEKS standards lookup
    """
    pass

class TeachersNamespace:
    """
    Teachers Database - Classroom management

    - students: Student CRUD
    - classrooms: Classroom management
    - assessments: Assessment tracking
    - interventions: Intervention planning
    - groups: Auto-differentiated grouping
    """
    pass

class VoiceNamespace:
    """
    Voice Interface - MOAD (Mother Of All Demos)

    - ask: Natural language to verified app
    - stream: Streaming responses
    - intent: Parse intent
    - patterns: App patterns
    """
    pass

class VaultNamespace:
    """
    Vault - Encrypted storage

    - store: Store encrypted data
    - retrieve: Retrieve encrypted data
    """
    pass

class LedgerNamespace:
    """
    Ledger - Immutable audit trail

    - entries: Get ledger entries
    - entry: Get specific entry
    - certificate: Get verification certificate
    """
    pass

class MerkleNamespace:
    """
    Merkle - Cryptographic anchoring

    - anchors: List anchors
    - anchor: Create/get anchor
    - proof: Get Merkle proof
    """
    pass

class PolicyNamespace:
    """
    Policy Engine - Governance rules

    - list: List policies
    - add: Add policy
    - remove: Remove policy
    """
    pass

class NegotiatorNamespace:
    """
    Negotiator - Human-in-the-loop approvals

    - pending: Get pending requests
    - request: Create request
    - approve: Approve request
    - reject: Reject request
    """
    pass

class InterfaceNamespace:
    """
    Interface Builder - Verified UI generation

    - templates: List templates
    - build: Build interface
    - components: Available components
    """
    pass

class JesterNamespace:
    """
    Jester - Code constraint analyzer

    - analyze: Analyze source code
    - cdl: Get CDL output
    - languages: Supported languages
    """
    pass

class ChatbotNamespace:
    """
    Chatbot Compiler - Type-safe constraint checking

    - compile: Process through constraint pipeline
    - classify: Classify input
    - batch: Batch processing
    """
    pass

class ExtractNamespace:
    """
    Constraint Extraction - Fuzzy to Formal

    - extract: Extract constraints from natural language
    - verify: Verify plan against constraints
    """
    pass

class LicenseNamespace:
    """
    License Management - Gumroad integration

    - verify: Verify license key
    - info: Get pricing info
    """
    pass

class ParcCloudNamespace:
    """
    parcCloud Authentication

    - signup: Create account
    - signin: Sign in
    - verify: Verify session
    - logout: Logout
    """
    pass

# =============================================================================
# DYNAMIC METHOD BUILDER
# =============================================================================

class DynamicNamespace:
    """Dynamically built namespace from OpenAPI spec"""

    def __init__(self, newton: 'Newton', name: str, description: str = ""):
        self._newton = newton
        self._name = name
        self._description = description
        self._methods: Dict[str, Callable] = {}

    def __repr__(self):
        methods = list(self._methods.keys())
        return f"<Newton.{self._name} methods={methods}>"

    def _add_method(self, name: str, method: Callable, doc: str = ""):
        """Add a method to this namespace"""
        method.__doc__ = doc
        self._methods[name] = method
        setattr(self, name, method)

    def help(self):
        """Show help for this namespace"""
        print(f"\n{'='*60}")
        print(f"Newton.{self._name}")
        print(f"{'='*60}")
        print(f"\n{self._description}\n")
        print("Methods:")
        for name, method in self._methods.items():
            doc = method.__doc__ or "No description"
            first_line = doc.split('\n')[0]
            print(f"  .{name}() - {first_line}")
        print()

# =============================================================================
# MAIN NEWTON CLASS
# =============================================================================

class Newton:
    """
    Newton Verified Computation Engine - Auto-Discovering SDK

    Usage:
        from newton import Newton

        # Connect to Newton
        n = Newton()  # Uses default URL
        n = Newton("https://your-instance.com")  # Custom instance
        n = Newton(api_key="your-key")  # With authentication

        # Core operations
        result = n.ask("What is quantum computing?")
        verified = n.verify("user input", constraints=["safe"])

        # Namespaces (auto-discovered)
        n.cartridge.visual("red circle")
        n.education.lesson(grade=3, subject="math")
        n.voice.ask("build me a todo app")

        # Discovery
        n.endpoints()  # List all endpoints
        n.capabilities()  # Full capability report
        n.help("cartridge")  # Help on specific namespace
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: Optional[str] = None,
        auto_discover: bool = True,
        timeout: int = 30,
        verify_ssl: bool = True,
        debug: bool = False
    ):
        """
        Initialize Newton SDK

        Args:
            base_url: Newton API URL (default: production)
            api_key: Optional API key for authentication
            auto_discover: Auto-discover endpoints from OpenAPI (default: True)
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
            debug: Enable debug logging
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.debug = debug

        # Session for connection pooling
        self._session = requests.Session()
        if api_key:
            self._session.headers['X-API-Key'] = api_key
        self._session.headers['User-Agent'] = f'Newton-SDK/{__version__}'
        self._session.headers['Content-Type'] = 'application/json'

        # Discovery cache
        self._openapi_spec: Optional[Dict] = None
        self._cartridge_info: Optional[Dict] = None
        self._discovery_time: float = 0
        self._discovered_endpoints: Dict[str, Dict] = {}

        # Initialize namespaces
        self._namespaces: Dict[str, DynamicNamespace] = {}

        # Create placeholder namespaces (will be populated on discovery)
        self.cartridge = DynamicNamespace(self, "cartridge", "Verified media generation")
        self.education = DynamicNamespace(self, "education", "Teacher support system")
        self.teachers = DynamicNamespace(self, "teachers", "Classroom management")
        self.voice = DynamicNamespace(self, "voice", "MOAD - Natural language to verified apps")
        self.vault = DynamicNamespace(self, "vault", "Encrypted storage")
        self.ledger = DynamicNamespace(self, "ledger", "Immutable audit trail")
        self.merkle = DynamicNamespace(self, "merkle", "Cryptographic anchoring")
        self.policy = DynamicNamespace(self, "policy", "Governance rules")
        self.negotiator = DynamicNamespace(self, "negotiator", "Human-in-the-loop approvals")
        self.interface = DynamicNamespace(self, "interface", "Verified UI generation")
        self.jester = DynamicNamespace(self, "jester", "Code constraint analyzer")
        self.chatbot = DynamicNamespace(self, "chatbot", "Type-safe constraint checking")
        self.extract = DynamicNamespace(self, "extract", "Constraint extraction")
        self.license = DynamicNamespace(self, "license", "License management")
        self.parccloud = DynamicNamespace(self, "parccloud", "Authentication")

        self._namespaces = {
            "cartridge": self.cartridge,
            "education": self.education,
            "teachers": self.teachers,
            "voice": self.voice,
            "vault": self.vault,
            "ledger": self.ledger,
            "merkle": self.merkle,
            "policy": self.policy,
            "negotiator": self.negotiator,
            "interface": self.interface,
            "jester": self.jester,
            "chatbot": self.chatbot,
            "extract": self.extract,
            "license": self.license,
            "parccloud": self.parccloud
        }

        # Auto-discover on init, or build hardcoded fallback
        if auto_discover:
            self._discover()
        else:
            # Build hardcoded endpoints for offline use
            self._build_hardcoded_endpoints()

    # =========================================================================
    # DISCOVERY
    # =========================================================================

    def _discover(self) -> bool:
        """
        Discover all endpoints from OpenAPI spec

        Called automatically on init. Fetches /openapi.json and
        dynamically creates methods for all discovered endpoints.
        """
        try:
            # Try to fetch OpenAPI spec
            self._openapi_spec = self._fetch_openapi()
            if self._openapi_spec:
                self._build_from_openapi()
                self._discovery_time = time.time()
                return True
        except Exception as e:
            if self.debug:
                print(f"[Newton] OpenAPI discovery failed: {e}")

        # Fallback: build hardcoded endpoints
        self._build_hardcoded_endpoints()
        return False

    def _fetch_openapi(self) -> Optional[Dict]:
        """Fetch OpenAPI specification from server"""
        try:
            resp = self._session.get(
                f"{self.base_url}{OPENAPI_PATH}",
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            if self.debug:
                print(f"[Newton] Failed to fetch OpenAPI: {e}")
        return None

    def _build_from_openapi(self):
        """Build SDK methods from OpenAPI spec"""
        if not self._openapi_spec:
            return

        paths = self._openapi_spec.get("paths", {})

        for path, methods in paths.items():
            for http_method, spec in methods.items():
                if http_method not in ["get", "post", "put", "delete", "patch"]:
                    continue

                # Parse the path to determine namespace and method name
                self._register_endpoint(path, http_method.upper(), spec)

    def _register_endpoint(self, path: str, method: str, spec: Dict):
        """Register an endpoint as a callable method"""
        # Parse path: /cartridge/visual -> namespace=cartridge, action=visual
        parts = path.strip('/').split('/')

        if len(parts) == 0:
            return

        # Determine namespace and method name
        namespace_name = parts[0]

        if len(parts) == 1:
            method_name = parts[0]
            namespace_name = None
        elif len(parts) >= 2:
            # Handle paths like /teachers/students/{id}
            method_name = '_'.join(parts[1:])
            # Clean up path parameters
            method_name = re.sub(r'\{[^}]+\}', '', method_name)
            method_name = method_name.strip('_').replace('__', '_')
            if not method_name:
                method_name = parts[0]

        # Get description from spec
        description = spec.get("summary", "") or spec.get("description", "")

        # Store endpoint info
        endpoint_key = f"{method} {path}"
        self._discovered_endpoints[endpoint_key] = {
            "path": path,
            "method": method,
            "description": description,
            "namespace": namespace_name,
            "action": method_name,
            "spec": spec
        }

        # Create the callable
        def make_caller(p, m, s):
            def caller(**kwargs):
                return self._call_endpoint(p, m, **kwargs)
            caller.__doc__ = s.get("summary", "") or s.get("description", "")
            return caller

        endpoint_caller = make_caller(path, method, spec)

        # Add to appropriate namespace or root
        if namespace_name and namespace_name in self._namespaces:
            ns = self._namespaces[namespace_name]
            ns._add_method(method_name or "call", endpoint_caller, description)

    def _build_hardcoded_endpoints(self):
        """Fallback: build commonly used endpoints without OpenAPI"""

        # Core endpoints
        self.cartridge._add_method("visual",
            lambda **kw: self._call_endpoint("/cartridge/visual", "POST", **kw),
            "Generate verified SVG specification")
        self.cartridge._add_method("sound",
            lambda **kw: self._call_endpoint("/cartridge/sound", "POST", **kw),
            "Generate verified audio specification")
        self.cartridge._add_method("sequence",
            lambda **kw: self._call_endpoint("/cartridge/sequence", "POST", **kw),
            "Generate verified video/animation specification")
        self.cartridge._add_method("data",
            lambda **kw: self._call_endpoint("/cartridge/data", "POST", **kw),
            "Generate verified data report")
        self.cartridge._add_method("rosetta",
            lambda **kw: self._call_endpoint("/cartridge/rosetta", "POST", **kw),
            "Generate code for target platform")
        self.cartridge._add_method("auto",
            lambda **kw: self._call_endpoint("/cartridge/auto", "POST", **kw),
            "Auto-detect cartridge type")
        self.cartridge._add_method("info",
            lambda: self._call_endpoint("/cartridge/info", "GET"),
            "Get cartridge capabilities")

        # Education
        self.education._add_method("lesson",
            lambda **kw: self._call_endpoint("/education/lesson", "POST", **kw),
            "Generate NES-compliant lesson plan")
        self.education._add_method("slides",
            lambda **kw: self._call_endpoint("/education/slides", "POST", **kw),
            "Generate slide deck")
        self.education._add_method("assess",
            lambda **kw: self._call_endpoint("/education/assess", "POST", **kw),
            "Analyze assessment data")
        self.education._add_method("plc",
            lambda **kw: self._call_endpoint("/education/plc", "POST", **kw),
            "Generate PLC report")
        self.education._add_method("teks",
            lambda **kw: self._call_endpoint("/education/teks", "GET", **kw),
            "Get TEKS standards")
        self.education._add_method("info",
            lambda: self._call_endpoint("/education/info", "GET"),
            "Get education module info")

        # Voice (MOAD)
        self.voice._add_method("ask",
            lambda **kw: self._call_endpoint("/voice/ask", "POST", **kw),
            "Natural language to verified app")
        self.voice._add_method("stream",
            lambda **kw: self._call_endpoint("/voice/stream", "POST", **kw),
            "Streaming voice interface")
        self.voice._add_method("intent",
            lambda **kw: self._call_endpoint("/voice/intent", "POST", **kw),
            "Parse intent from text")
        self.voice._add_method("patterns",
            lambda **kw: self._call_endpoint("/voice/patterns", "GET", **kw),
            "List app patterns")
        self.voice._add_method("demo",
            lambda: self._call_endpoint("/voice/demo", "GET"),
            "MOAD demo scenarios")

        # Vault
        self.vault._add_method("store",
            lambda **kw: self._call_endpoint("/vault/store", "POST", **kw),
            "Store encrypted data")
        self.vault._add_method("retrieve",
            lambda **kw: self._call_endpoint("/vault/retrieve", "POST", **kw),
            "Retrieve encrypted data")

        # Ledger
        self.ledger._add_method("entries",
            lambda **kw: self._call_endpoint("/ledger", "GET", **kw),
            "Get ledger entries")
        self.ledger._add_method("certificate",
            lambda index: self._call_endpoint(f"/ledger/certificate/{index}", "GET"),
            "Get verification certificate")

        # Jester
        self.jester._add_method("analyze",
            lambda **kw: self._call_endpoint("/jester/analyze", "POST", **kw),
            "Analyze source code for constraints")
        self.jester._add_method("cdl",
            lambda **kw: self._call_endpoint("/jester/cdl", "POST", **kw),
            "Get CDL output for code")
        self.jester._add_method("info",
            lambda: self._call_endpoint("/jester/info", "GET"),
            "Get Jester capabilities")

        # Interface Builder
        self.interface._add_method("templates",
            lambda **kw: self._call_endpoint("/interface/templates", "GET", **kw),
            "List available templates")
        self.interface._add_method("build",
            lambda **kw: self._call_endpoint("/interface/build", "POST", **kw),
            "Build interface from spec")
        self.interface._add_method("components",
            lambda: self._call_endpoint("/interface/components", "GET"),
            "Get available components")
        self.interface._add_method("info",
            lambda: self._call_endpoint("/interface/info", "GET"),
            "Get Interface Builder info")

        # Chatbot
        self.chatbot._add_method("compile",
            lambda **kw: self._call_endpoint("/chatbot/compile", "POST", **kw),
            "Process through constraint pipeline")
        self.chatbot._add_method("classify",
            lambda **kw: self._call_endpoint("/chatbot/classify", "POST", **kw),
            "Classify input")
        self.chatbot._add_method("batch",
            lambda **kw: self._call_endpoint("/chatbot/batch", "POST", **kw),
            "Batch processing")

        # Extract
        self.extract._add_method("constraints",
            lambda **kw: self._call_endpoint("/extract", "POST", **kw),
            "Extract constraints from natural language")
        self.extract._add_method("verify",
            lambda **kw: self._call_endpoint("/extract/verify", "POST", **kw),
            "Verify plan against constraints")

        # Policy
        self.policy._add_method("list",
            lambda: self._call_endpoint("/policy", "GET"),
            "List all policies")
        self.policy._add_method("add",
            lambda **kw: self._call_endpoint("/policy", "POST", **kw),
            "Add new policy")

        # Negotiator
        self.negotiator._add_method("pending",
            lambda **kw: self._call_endpoint("/negotiator/pending", "GET", **kw),
            "Get pending requests")
        self.negotiator._add_method("request",
            lambda **kw: self._call_endpoint("/negotiator/request", "POST", **kw),
            "Create approval request")
        self.negotiator._add_method("approve",
            lambda request_id, **kw: self._call_endpoint(f"/negotiator/approve/{request_id}", "POST", **kw),
            "Approve request")
        self.negotiator._add_method("reject",
            lambda request_id, **kw: self._call_endpoint(f"/negotiator/reject/{request_id}", "POST", **kw),
            "Reject request")

        # Merkle
        self.merkle._add_method("anchors",
            lambda: self._call_endpoint("/merkle/anchors", "GET"),
            "List all anchors")
        self.merkle._add_method("anchor",
            lambda **kw: self._call_endpoint("/merkle/anchor", "POST", **kw),
            "Create anchor")
        self.merkle._add_method("proof",
            lambda index: self._call_endpoint(f"/merkle/proof/{index}", "GET"),
            "Get Merkle proof")
        self.merkle._add_method("latest",
            lambda: self._call_endpoint("/merkle/latest", "GET"),
            "Get latest anchor")

        # License
        self.license._add_method("verify",
            lambda **kw: self._call_endpoint("/license/verify", "POST", **kw),
            "Verify license key")
        self.license._add_method("info",
            lambda: self._call_endpoint("/license/info", "GET"),
            "Get licensing info")

        # parcCloud
        self.parccloud._add_method("signup",
            lambda **kw: self._call_endpoint("/parccloud/signup", "POST", **kw),
            "Create account")
        self.parccloud._add_method("signin",
            lambda **kw: self._call_endpoint("/parccloud/signin", "POST", **kw),
            "Sign in")
        self.parccloud._add_method("verify",
            lambda: self._call_endpoint("/parccloud/verify", "GET"),
            "Verify session")
        self.parccloud._add_method("logout",
            lambda: self._call_endpoint("/parccloud/logout", "POST"),
            "Logout")
        self.parccloud._add_method("stats",
            lambda: self._call_endpoint("/parccloud/stats", "GET"),
            "Get stats")

        # Teachers - simplified
        self.teachers._add_method("students",
            lambda **kw: self._call_endpoint("/teachers/students", "GET" if not kw else "POST", **kw),
            "Manage students")
        self.teachers._add_method("classrooms",
            lambda **kw: self._call_endpoint("/teachers/classrooms", "GET" if not kw else "POST", **kw),
            "Manage classrooms")
        self.teachers._add_method("assessments",
            lambda **kw: self._call_endpoint("/teachers/assessments", "GET" if not kw else "POST", **kw),
            "Manage assessments")
        self.teachers._add_method("info",
            lambda: self._call_endpoint("/teachers/info", "GET"),
            "Get Teachers Database info")

    # =========================================================================
    # HTTP LAYER
    # =========================================================================

    def _call_endpoint(self, path: str, method: str, **kwargs) -> NewtonResponse:
        """Make HTTP call to Newton API"""
        url = f"{self.base_url}{path}"
        start_time = time.time()

        try:
            if method == "GET":
                resp = self._session.get(url, params=kwargs, timeout=self.timeout, verify=self.verify_ssl)
            elif method == "POST":
                resp = self._session.post(url, json=kwargs, timeout=self.timeout, verify=self.verify_ssl)
            elif method == "PUT":
                resp = self._session.put(url, json=kwargs, timeout=self.timeout, verify=self.verify_ssl)
            elif method == "DELETE":
                resp = self._session.delete(url, timeout=self.timeout, verify=self.verify_ssl)
            else:
                raise NewtonError(f"Unsupported HTTP method: {method}")

            latency = (time.time() - start_time) * 1000

            # Parse response
            try:
                data = resp.json()
            except:
                data = resp.text

            # Handle errors
            if resp.status_code == 401:
                raise NewtonAuthError("Authentication required")
            elif resp.status_code == 429:
                raise NewtonRateLimitError("Rate limit exceeded")
            elif resp.status_code >= 400:
                error_msg = data.get("detail", str(data)) if isinstance(data, dict) else str(data)
                raise NewtonError(f"API error ({resp.status_code}): {error_msg}")

            # Extract verification metadata
            verified = False
            constraints_checked = []
            ledger_index = None
            merkle_root = None

            if isinstance(data, dict):
                verified = data.get("verified", False) or data.get("valid", False)
                constraints_checked = data.get("constraints_checked", []) or data.get("policies_applied", [])
                ledger_index = data.get("ledger_index")
                merkle_root = data.get("merkle_root")

            return NewtonResponse(
                success=True,
                data=data,
                verified=verified,
                constraints_checked=constraints_checked,
                ledger_index=ledger_index,
                merkle_root=merkle_root,
                latency_ms=latency,
                raw={"status_code": resp.status_code, "headers": dict(resp.headers)}
            )

        except requests.exceptions.ConnectionError as e:
            raise NewtonConnectionError(f"Failed to connect to Newton: {e}")
        except requests.exceptions.Timeout:
            raise NewtonConnectionError(f"Request timed out after {self.timeout}s")

    # =========================================================================
    # CORE API METHODS
    # =========================================================================

    def ask(
        self,
        query: str,
        constraints: Optional[List[str]] = None,
        context: Optional[Dict] = None,
        **kwargs
    ) -> NewtonResponse:
        """
        Ask Newton anything - full verification pipeline

        Args:
            query: Your question or request
            constraints: Optional list of constraints to apply
            context: Optional context dictionary

        Returns:
            NewtonResponse with verified answer

        Example:
            >>> n.ask("What is the capital of France?")
            >>> n.ask("Summarize this text", constraints=["factual", "concise"])
        """
        payload = {"query": query, **kwargs}
        if constraints:
            payload["constraints"] = constraints
        if context:
            payload["context"] = context
        return self._call_endpoint("/ask", "POST", **payload)

    def verify(
        self,
        input: str,
        constraints: Optional[List[str]] = None,
        **kwargs
    ) -> NewtonResponse:
        """
        Verify input against safety constraints

        Args:
            input: Text to verify
            constraints: Constraints to check against

        Returns:
            NewtonResponse with verification result

        Example:
            >>> n.verify("Hello world", constraints=["no_profanity", "safe_for_work"])
        """
        payload = {"input": input, **kwargs}
        if constraints:
            payload["constraints"] = constraints
        return self._call_endpoint("/verify", "POST", **payload)

    def verify_batch(
        self,
        inputs: List[str],
        constraints: Optional[List[str]] = None,
        **kwargs
    ) -> NewtonResponse:
        """
        Batch verify multiple inputs

        Args:
            inputs: List of texts to verify
            constraints: Constraints to check against

        Returns:
            NewtonResponse with batch verification results
        """
        payload = {"inputs": inputs, **kwargs}
        if constraints:
            payload["constraints"] = constraints
        return self._call_endpoint("/verify/batch", "POST", **payload)

    def constraint(
        self,
        constraint: str,
        object: Dict,
        **kwargs
    ) -> NewtonResponse:
        """
        Evaluate a CDL constraint against an object

        Args:
            constraint: CDL constraint specification
            object: Object to evaluate against

        Returns:
            NewtonResponse with constraint evaluation result
        """
        return self._call_endpoint("/constraint", "POST", constraint=constraint, object=object, **kwargs)

    def ground(self, claim: str, **kwargs) -> NewtonResponse:
        """
        Ground a claim in external evidence

        Args:
            claim: The claim to verify

        Returns:
            NewtonResponse with grounding evidence
        """
        return self._call_endpoint("/ground", "POST", claim=claim, **kwargs)

    def calculate(
        self,
        expression: str,
        max_iterations: int = 1000,
        max_operations: int = 10000,
        timeout_seconds: float = 5.0,
        **kwargs
    ) -> NewtonResponse:
        """
        Execute verified computation

        Args:
            expression: Mathematical expression to evaluate
            max_iterations: Maximum loop iterations
            max_operations: Maximum total operations
            timeout_seconds: Computation timeout

        Returns:
            NewtonResponse with computation result

        Example:
            >>> n.calculate("sum([x**2 for x in range(10)])")
        """
        return self._call_endpoint(
            "/calculate", "POST",
            expression=expression,
            max_iterations=max_iterations,
            max_operations=max_operations,
            timeout_seconds=timeout_seconds,
            **kwargs
        )

    def statistics(
        self,
        values: List[float],
        test_value: Optional[float] = None,
        threshold: float = 3.5,
        **kwargs
    ) -> NewtonResponse:
        """
        Robust statistics using MAD (Median Absolute Deviation)

        Args:
            values: List of numeric values
            test_value: Optional value to test for anomaly
            threshold: Z-score threshold for anomaly detection

        Returns:
            NewtonResponse with statistical analysis

        Example:
            >>> n.statistics([1, 2, 3, 4, 100])  # 100 is outlier
        """
        payload = {"values": values, "threshold": threshold, **kwargs}
        if test_value is not None:
            payload["test_value"] = test_value
        return self._call_endpoint("/statistics", "POST", **payload)

    # =========================================================================
    # SYSTEM METHODS
    # =========================================================================

    def ping(self) -> bool:
        """Check if Newton is reachable"""
        try:
            resp = self._session.get(f"{self.base_url}/health", timeout=5)
            return resp.status_code == 200
        except:
            return False

    def health(self) -> NewtonResponse:
        """Get system health status"""
        return self._call_endpoint("/health", "GET")

    def metrics(self) -> NewtonResponse:
        """Get detailed system metrics"""
        return self._call_endpoint("/metrics", "GET")

    def refresh(self) -> bool:
        """Refresh endpoint discovery from OpenAPI"""
        return self._discover()

    # =========================================================================
    # DISCOVERY & HELP
    # =========================================================================

    def endpoints(self, filter: Optional[str] = None) -> List[str]:
        """
        List all discovered endpoints

        Args:
            filter: Optional filter string (e.g., "cartridge", "POST")

        Returns:
            List of endpoint strings
        """
        endpoints = list(self._discovered_endpoints.keys())

        if filter:
            filter_lower = filter.lower()
            endpoints = [e for e in endpoints if filter_lower in e.lower()]

        for e in sorted(endpoints):
            info = self._discovered_endpoints[e]
            print(f"  {e}")
            if info.get("description"):
                print(f"    └─ {info['description'][:60]}")

        return sorted(endpoints)

    def capabilities(self) -> Dict:
        """
        Get full capability report

        Returns:
            Dictionary of all Newton capabilities organized by category
        """
        report = {
            "version": __version__,
            "base_url": self.base_url,
            "authenticated": self.api_key is not None,
            "discovery_source": "openapi" if self._openapi_spec else "hardcoded",
            "endpoint_count": len(self._discovered_endpoints),
            "namespaces": {},
            "core_methods": ["ask", "verify", "verify_batch", "constraint", "ground", "calculate", "statistics"]
        }

        for name, ns in self._namespaces.items():
            report["namespaces"][name] = {
                "description": ns._description,
                "methods": list(ns._methods.keys())
            }

        return report

    def help(self, topic: Optional[str] = None):
        """
        Get help on Newton SDK

        Args:
            topic: Optional topic (namespace name or "all")
        """
        if topic is None:
            print("""
╔══════════════════════════════════════════════════════════════╗
║              NEWTON VERIFIED COMPUTATION ENGINE               ║
║                    SDK v{version} - Auto-Discovering                ║
╚══════════════════════════════════════════════════════════════╝

QUICK START:
    from newton import Newton
    n = Newton()

    # Core operations
    n.ask("What is quantum computing?")
    n.verify("user input", constraints=["safe"])
    n.calculate("2 + 2")

NAMESPACES:
    n.cartridge    - Verified media generation (visual, sound, video, code)
    n.education    - Teacher support (lessons, assessments, TEKS)
    n.teachers     - Classroom database (students, groups, interventions)
    n.voice        - MOAD (natural language to verified apps)
    n.vault        - Encrypted storage
    n.ledger       - Immutable audit trail
    n.merkle       - Cryptographic anchoring
    n.policy       - Governance rules
    n.negotiator   - Human-in-the-loop approvals
    n.interface    - Verified UI generation
    n.jester       - Code constraint analyzer
    n.chatbot      - Type-safe constraint checking
    n.extract      - Constraint extraction
    n.license      - License management
    n.parccloud    - Authentication

DISCOVERY:
    n.endpoints()       # List all {count} discovered endpoints
    n.capabilities()    # Full capability report
    n.help("cartridge") # Help on specific namespace
    n.refresh()         # Re-discover from API

AUTHENTICATION:
    n = Newton(api_key="your-key")
    # Or get a key:
    n.license.verify(license_key="gumroad-key")
""".format(version=__version__, count=len(self._discovered_endpoints)))
            return

        topic = topic.lower()

        if topic in self._namespaces:
            self._namespaces[topic].help()
        elif topic == "all":
            for ns in self._namespaces.values():
                ns.help()
        else:
            print(f"Unknown topic: {topic}")
            print(f"Available: {', '.join(self._namespaces.keys())}")

    # =========================================================================
    # CONVENIENCE PROPERTIES
    # =========================================================================

    @property
    def is_connected(self) -> bool:
        """Check if connected to Newton"""
        return self.ping()

    @property
    def endpoint_count(self) -> int:
        """Number of discovered endpoints"""
        return len(self._discovered_endpoints)

    def __repr__(self):
        status = "connected" if self.ping() else "disconnected"
        return f"<Newton {status} endpoints={self.endpoint_count} url={self.base_url}>"


# =============================================================================
# MODULE-LEVEL CONVENIENCE
# =============================================================================

# Default instance for quick access
_default_instance: Optional[Newton] = None

def connect(base_url: str = DEFAULT_BASE_URL, **kwargs) -> Newton:
    """
    Connect to Newton (creates default instance)

    Usage:
        import newton
        newton.connect()
        newton.ask("Hello!")
    """
    global _default_instance
    _default_instance = Newton(base_url=base_url, **kwargs)
    return _default_instance

def ask(query: str, **kwargs) -> NewtonResponse:
    """Quick ask using default instance"""
    global _default_instance
    if _default_instance is None:
        _default_instance = Newton()
    return _default_instance.ask(query, **kwargs)

def verify(input: str, **kwargs) -> NewtonResponse:
    """Quick verify using default instance"""
    global _default_instance
    if _default_instance is None:
        _default_instance = Newton()
    return _default_instance.verify(input, **kwargs)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point"""
    import sys

    print(f"Newton SDK v{__version__}")
    print("Connecting to Newton...")

    n = Newton()

    if n.ping():
        print(f"✓ Connected to {n.base_url}")
        print(f"✓ Discovered {n.endpoint_count} endpoints")

        caps = n.capabilities()
        print(f"\nNamespaces: {', '.join(caps['namespaces'].keys())}")
        print(f"\nType 'n.help()' for usage information")
    else:
        print(f"✗ Could not connect to {n.base_url}")
        print("  Newton might be cold-starting (free tier)")
        print("  Try again in 30 seconds")

    # Start interactive mode if no args
    if len(sys.argv) == 1:
        print("\n--- Interactive Mode ---")
        print("Instance available as 'n'")
        import code
        code.interact(local={"n": n, "Newton": Newton, "newton": sys.modules[__name__]})


if __name__ == "__main__":
    main()
