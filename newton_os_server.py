#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
NEWTON OS - UNIFIED SERVER
Ada speaks. Tahoe remembers. THIA sees. Rosetta compiles.
═══════════════════════════════════════════════════════════════════════════

Author: Jared Lewis | Ada Computing Company | Houston, Texas
"1 == 1. The cloud is weather. We're building shelter."

Architecture:
    /verify   → Newton Core (intent verification)
    /analyze  → THIA (anomaly detection)
    /compile  → Rosetta (intent-to-prompt compiler)
    /health   → Infrastructure status

One API. Multiple capabilities. Single identity.
═══════════════════════════════════════════════════════════════════════════
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from collections import defaultdict
from functools import wraps
import hashlib
import time
import re
import statistics
import json
import os
from pathlib import Path

# Grounding Engine for claim verification
from core.grounding import GroundingEngine

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

DW_AXIS = 2048
THRESHOLD = 1024
VERSION = "3.0.0"
ENGINE = f"Newton OS {VERSION}"

# Append-only ledger for audit trail
LEDGER = []
MAX_LEDGER_SIZE = 10000

# Persistent ledger path
LEDGER_PATH = Path(os.environ.get("NEWTON_LEDGER_PATH", ".newton_ledger.json"))

# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION & RATE LIMITING
# ═══════════════════════════════════════════════════════════════════════════

# API Keys (in production, use database/secrets manager)
API_KEYS: Dict[str, Dict[str, Any]] = {
    # Format: "key": {"owner": "name", "tier": "free|pro|enterprise", "rate_limit": requests_per_minute}
    "newton-public-demo": {"owner": "public", "tier": "free", "rate_limit": 60},
}

# Load custom API keys from environment
if os.environ.get("NEWTON_API_KEYS"):
    try:
        custom_keys = json.loads(os.environ["NEWTON_API_KEYS"])
        API_KEYS.update(custom_keys)
    except json.JSONDecodeError:
        pass

# Enterprise key from environment
ENTERPRISE_KEY = os.environ.get("NEWTON_ENTERPRISE_KEY")
if ENTERPRISE_KEY:
    API_KEYS[ENTERPRISE_KEY] = {"owner": "enterprise", "tier": "enterprise", "rate_limit": 10000}

# Rate limiting storage
RATE_LIMITS: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds

# Auth bypass for development
AUTH_ENABLED = os.environ.get("NEWTON_AUTH_ENABLED", "false").lower() == "true"

def check_rate_limit(api_key: str, limit: int) -> bool:
    """Check if request is within rate limit."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    # Clean old entries
    RATE_LIMITS[api_key] = [t for t in RATE_LIMITS[api_key] if t > window_start]

    if len(RATE_LIMITS[api_key]) >= limit:
        return False

    RATE_LIMITS[api_key].append(now)
    return True

async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> Dict[str, Any]:
    """Verify API key and check rate limits."""
    # If auth is disabled, allow all requests with default limits
    if not AUTH_ENABLED:
        return {"owner": "anonymous", "tier": "free", "rate_limit": 100}

    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key. Include X-API-Key header.")

    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")

    key_info = API_KEYS[x_api_key]

    if not check_rate_limit(x_api_key, key_info["rate_limit"]):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {key_info['rate_limit']} requests per minute."
        )

    return key_info

# ═══════════════════════════════════════════════════════════════════════════
# PERSISTENT LEDGER
# ═══════════════════════════════════════════════════════════════════════════

def load_ledger() -> List[Dict]:
    """Load ledger from persistent storage."""
    global LEDGER
    if LEDGER_PATH.exists():
        try:
            with open(LEDGER_PATH, 'r') as f:
                LEDGER = json.load(f)
        except (json.JSONDecodeError, IOError):
            LEDGER = []
    return LEDGER

def save_ledger():
    """Save ledger to persistent storage."""
    try:
        with open(LEDGER_PATH, 'w') as f:
            json.dump(LEDGER, f, indent=2)
    except IOError as e:
        print(f"Warning: Could not save ledger: {e}")

# Load ledger on startup
load_ledger()

# ═══════════════════════════════════════════════════════════════════════════
# CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════

CONSTRAINTS = {
    "harm": {
        "name": "No Harm",
        "patterns": [
            r"(how to )?(make|build|create|construct).*\b(bomb|weapon|explosive|poison|grenade)\b",
            r"(how to )?(kill|murder|harm|hurt|injure|assassinate)",
            r"(how to )?(suicide|self.harm)",
            r"\b(i want to|i need to|help me) (kill|murder|harm|hurt)",
        ]
    },
    "medical": {
        "name": "Medical Bounds",
        "patterns": [
            r"what (medication|drug|dosage|prescription) should (i|you) take",
            r"diagnose (my|this|the)",
            r"prescribe (me|a)",
        ]
    },
    "legal": {
        "name": "Legal Bounds",
        "patterns": [
            r"(how to )?(evade|avoid|cheat).*(tax|irs)",
            r"(how to )?(launder|hide|offshore) money",
            r"(how to )?(forge|fake|counterfeit)",
        ]
    },
    "security": {
        "name": "Security",
        "patterns": [
            r"(how to )?(hack|crack|break into|exploit|bypass)",
            r"\b(steal password|phishing|malware|ransomware)\b",
        ]
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class VerifyRequest(BaseModel):
    input: str
    constraints: Optional[List[str]] = None

class AnalyzeRequest(BaseModel):
    data: List[float]
    method: Optional[str] = "zscore"
    threshold: Optional[float] = 3.0
    labels: Optional[List[str]] = None

class BatchAnalyzeRequest(BaseModel):
    datasets: Dict[str, List[float]]
    method: Optional[str] = "zscore"
    threshold: Optional[float] = 3.0

class CompileRequest(BaseModel):
    intent: str
    target_platform: Optional[str] = "iOS"
    ios_version: Optional[str] = "18.0"
    constraints: Optional[List[str]] = None

# ═══════════════════════════════════════════════════════════════════════════
# CARTRIDGE MODELS
# ═══════════════════════════════════════════════════════════════════════════

class VisualCartridgeRequest(BaseModel):
    """SVG generation with dimension constraints."""
    intent: str
    width: Optional[int] = 800
    height: Optional[int] = 600
    max_elements: Optional[int] = 100
    color_palette: Optional[List[str]] = None

class SoundCartridgeRequest(BaseModel):
    """Audio specification with frequency/duration limits."""
    intent: str
    duration_ms: Optional[int] = 5000  # max 5 seconds
    min_frequency: Optional[float] = 20.0  # Hz
    max_frequency: Optional[float] = 20000.0  # Hz
    sample_rate: Optional[int] = 44100

class SequenceCartridgeRequest(BaseModel):
    """Video/animation specification with frame constraints."""
    intent: str
    duration_seconds: Optional[float] = 30.0
    fps: Optional[int] = 30
    width: Optional[int] = 1920
    height: Optional[int] = 1080
    max_scenes: Optional[int] = 10

class DataCartridgeRequest(BaseModel):
    """Report generation with statistical bounds."""
    intent: str
    data: Optional[Dict[str, Any]] = None
    format: Optional[str] = "json"  # json, csv, markdown
    max_rows: Optional[int] = 1000
    include_statistics: Optional[bool] = True

class SignRequest(BaseModel):
    """Cryptographic signature request."""
    payload: str
    context: Optional[str] = None

class GroundRequest(BaseModel):
    """Claim verification request."""
    query: str

# Initialize Grounding Engine
grounding_engine = GroundingEngine()

# ═══════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def fingerprint(data: Any) -> str:
    """Generate SHA-256 fingerprint."""
    h = hashlib.sha256(str(data).encode()).hexdigest()
    return h[:12].upper()

def melt(text: str) -> int:
    """Convert text to signal value."""
    cleaned = re.sub(r'[^a-z0-9\s]', '', text.lower())
    tokens = cleaned.split()

    if not tokens:
        return DW_AXIS

    signal = DW_AXIS
    for i, token in enumerate(tokens):
        h = 0
        for char in token:
            h = ((h << 5) ^ h ^ ord(char)) & 0xFFF
        weight = (h % 400) - 200
        signal += weight

    return max(0, min(4095, signal))

def snap(signal: int) -> dict:
    """Determine verification status from signal."""
    distance = abs(signal - DW_AXIS)
    crystalline = distance <= THRESHOLD
    confidence = round((1 - distance / THRESHOLD) * 100, 1) if crystalline else 0

    return {
        "signal": signal,
        "distance": distance,
        "verified": crystalline,
        "code": 200 if crystalline else 1202,
        "confidence": confidence
    }

def check_constraints(text: str, constraint_list: List[str]) -> dict:
    """Check text against constraint patterns."""
    text_lower = text.lower()
    passed = []
    failed = []

    for key in constraint_list:
        if key not in CONSTRAINTS:
            continue

        constraint = CONSTRAINTS[key]
        violation = False

        for pattern in constraint["patterns"]:
            if re.search(pattern, text_lower):
                violation = True
                break

        if violation:
            failed.append(key)
        else:
            passed.append(key)

    return {"passed": passed, "failed": failed}

# ═══════════════════════════════════════════════════════════════════════════
# THIA - ANOMALY DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def thia_zscore(values: List[float], threshold: float = 3.0) -> dict:
    """Z-score anomaly detection."""
    n = len(values)
    if n < 2:
        return {"error": "Insufficient data points", "anomalies": []}

    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    sd = variance ** 0.5 if variance > 0 else 0.0001

    scores = [(x - mean) / sd for x in values]
    anomalies = [i for i, z in enumerate(scores) if abs(z) > threshold]

    return {
        "method": "zscore",
        "threshold": threshold,
        "statistics": {
            "n": n,
            "mean": round(mean, 4),
            "std_dev": round(sd, 4),
            "min": round(min(values), 4),
            "max": round(max(values), 4)
        },
        "scores": [round(z, 4) for z in scores],
        "anomalies": anomalies,
        "anomaly_values": [round(values[i], 4) for i in anomalies],
        "n_anomalies": len(anomalies),
        "pct_anomalies": round(len(anomalies) / n * 100, 2)
    }

def thia_iqr(values: List[float], threshold: float = 1.5) -> dict:
    """IQR anomaly detection."""
    n = len(values)
    if n < 4:
        return {"error": "Insufficient data points for IQR", "anomalies": []}

    sorted_vals = sorted(values)
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    q1 = sorted_vals[q1_idx]
    q3 = sorted_vals[q3_idx]
    iqr = q3 - q1

    lower = q1 - threshold * iqr
    upper = q3 + threshold * iqr

    anomalies = [i for i, v in enumerate(values) if v < lower or v > upper]

    return {
        "method": "iqr",
        "threshold": threshold,
        "statistics": {
            "n": n,
            "q1": round(q1, 4),
            "q3": round(q3, 4),
            "iqr": round(iqr, 4),
            "lower_bound": round(lower, 4),
            "upper_bound": round(upper, 4)
        },
        "anomalies": anomalies,
        "anomaly_values": [round(values[i], 4) for i in anomalies],
        "n_anomalies": len(anomalies),
        "pct_anomalies": round(len(anomalies) / n * 100, 2)
    }

def thia_mad(values: List[float], threshold: float = 3.0) -> dict:
    """Median Absolute Deviation anomaly detection."""
    n = len(values)
    if n < 2:
        return {"error": "Insufficient data points", "anomalies": []}

    sorted_vals = sorted(values)
    median = sorted_vals[n // 2]

    abs_devs = [abs(x - median) for x in values]
    sorted_devs = sorted(abs_devs)
    mad = sorted_devs[n // 2]

    if mad == 0:
        mad = 0.0001

    scores = [abs(x - median) / mad for x in values]
    anomalies = [i for i, s in enumerate(scores) if s > threshold]

    return {
        "method": "mad",
        "threshold": threshold,
        "statistics": {
            "n": n,
            "median": round(median, 4),
            "mad": round(mad, 4)
        },
        "scores": [round(s, 4) for s in scores],
        "anomalies": anomalies,
        "anomaly_values": [round(values[i], 4) for i in anomalies],
        "n_anomalies": len(anomalies),
        "pct_anomalies": round(len(anomalies) / n * 100, 2)
    }

def thia_analyze(values: List[float], method: str = "zscore", threshold: float = 3.0) -> dict:
    """Unified THIA analysis dispatcher."""
    if method == "zscore":
        return thia_zscore(values, threshold)
    elif method == "iqr":
        return thia_iqr(values, threshold)
    elif method == "mad":
        return thia_mad(values, threshold)
    elif method == "all":
        return {
            "zscore": thia_zscore(values, threshold),
            "iqr": thia_iqr(values, 1.5),
            "mad": thia_mad(values, threshold)
        }
    else:
        return {"error": f"Unknown method: {method}. Use 'zscore', 'iqr', 'mad', or 'all'."}

# ═══════════════════════════════════════════════════════════════════════════
# ROSETTA - COMPILER CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════

# Apple Development Constraints
APP_CONSTRAINTS = {
    "app_store": {
        "name": "App Store Guidelines",
        "patterns": [
            r"\b(gambling|casino|betting)\b.*\b(real money|cash)\b",
            r"\b(cryptocurrency|crypto)\b.*\b(mining|trading)\b",
            r"\b(adult|explicit|nsfw)\b",
        ]
    },
    "privacy": {
        "name": "Privacy Requirements",
        "patterns": [
            r"\b(track|collect)\b.*\b(location|contacts|photos)\b.*\b(without|secret)",
            r"\b(sell|share)\b.*\b(user data|personal)\b",
        ]
    },
    "hig": {
        "name": "Human Interface Guidelines",
        "patterns": [
            r"\b(custom|non-standard)\b.*\b(back button|navigation)\b",
            r"\b(disable|hide)\b.*\b(status bar|home indicator)\b",
        ]
    }
}

# Framework-Specific Constraints
FRAMEWORK_CONSTRAINTS = {
    "healthkit": {
        "name": "HealthKit Medical Constraints",
        "patterns": [
            r"\b(diagnose|prescribe|treat)\b.*\b(disease|illness|condition)\b",
            r"\b(replace|substitute)\b.*\b(doctor|physician|medical)\b",
            r"\b(medical advice|health recommendation)\b.*\b(without|no)\b.*\b(disclaimer)\b",
        ],
        "required_entitlements": ["com.apple.developer.healthkit"],
        "required_descriptions": ["NSHealthShareUsageDescription", "NSHealthUpdateUsageDescription"],
        "warnings": [
            "HealthKit data is sensitive - implement proper encryption",
            "Medical apps may require FDA approval",
            "Always include medical disclaimer"
        ]
    },
    "swiftui": {
        "name": "SwiftUI Accessibility Constraints",
        "patterns": [
            r"\b(ignore|skip|disable)\b.*\b(accessibility|voiceover)\b",
            r"\b(small|tiny)\b.*\b(text|font)\b.*\b(fixed|hardcoded)\b",
            r"\b(color only)\b.*\b(indicator|status)\b",
        ],
        "required_features": ["Dynamic Type support", "VoiceOver labels", "Semantic colors"],
        "warnings": [
            "All interactive elements need accessibility labels",
            "Support Dynamic Type for text sizing",
            "Don't rely on color alone for information"
        ]
    },
    "arkit": {
        "name": "ARKit Safety Constraints",
        "patterns": [
            r"\b(obscure|block|hide)\b.*\b(real world|environment|surroundings)\b",
            r"\b(full screen|immersive)\b.*\b(no|without)\b.*\b(exit|escape)\b",
            r"\b(motion|movement)\b.*\b(extreme|rapid|disorienting)\b",
        ],
        "safety_requirements": [
            "Clear exit mechanism from AR experience",
            "Warnings for physical movement required",
            "Boundary detection for physical safety"
        ],
        "warnings": [
            "Users must maintain awareness of surroundings",
            "Avoid rapid camera movements that cause motion sickness",
            "Provide clear boundaries for safe play areas"
        ]
    },
    "coreml": {
        "name": "CoreML Epistemic Constraints",
        "patterns": [
            r"\b(100%|always|never|certain|guaranteed)\b.*\b(accurate|correct|prediction)\b",
            r"\b(replace|substitute)\b.*\b(human|expert|professional)\b.*\b(judgment|decision)\b",
            r"\b(autonomous|automatic)\b.*\b(critical|life|safety)\b.*\b(decision)\b",
        ],
        "epistemic_bounds": {
            "confidence_display": "Always show prediction confidence",
            "uncertainty": "Acknowledge model limitations",
            "human_oversight": "Critical decisions require human review"
        },
        "warnings": [
            "ML predictions have inherent uncertainty",
            "Display confidence scores to users",
            "Never claim 100% accuracy"
        ]
    },
    # ─────────────────────────────────────────────────────────────────────────
    # UNIVERSAL FRAMEWORK CONSTRAINTS (Non-Apple)
    # ─────────────────────────────────────────────────────────────────────────
    "react": {
        "name": "React Security & Accessibility",
        "patterns": [
            r"\b(dangerouslySetInnerHTML)\b.*\b(user input|untrusted|dynamic)\b",
            r"\b(disable|skip|ignore)\b.*\b(eslint|security|sanitize)\b",
            r"\b(eval|Function\()\b.*\b(user|input|dynamic)\b",
        ],
        "security_requirements": [
            "Sanitize all user inputs before rendering",
            "Use Content Security Policy headers",
            "Avoid dangerouslySetInnerHTML with untrusted content"
        ],
        "accessibility_requirements": [
            "Include ARIA labels on interactive elements",
            "Ensure keyboard navigation support",
            "Maintain focus management for modals/dialogs"
        ],
        "warnings": [
            "XSS vulnerabilities from unsanitized HTML",
            "Always escape user-provided content",
            "Use React's built-in XSS protections"
        ]
    },
    "tensorflow": {
        "name": "TensorFlow ML Safety Constraints",
        "patterns": [
            r"\b(100%|always|never|certain|guaranteed)\b.*\b(accurate|correct|prediction)\b",
            r"\b(autonomous|automatic)\b.*\b(critical|life|safety|medical|financial)\b.*\b(decision)\b",
            r"\b(train|fine-tune)\b.*\b(private|personal|sensitive)\b.*\b(data)\b.*\b(without consent)\b",
            r"\b(deepfake|fake|synthetic)\b.*\b(identity|person|face)\b",
        ],
        "epistemic_bounds": {
            "confidence_display": "Always expose prediction confidence scores",
            "uncertainty_quantification": "Use proper uncertainty estimation methods",
            "human_oversight": "Critical decisions require human review",
            "bias_testing": "Test for demographic and selection bias"
        },
        "data_requirements": [
            "Document training data sources and licenses",
            "Implement data privacy protections",
            "Maintain model versioning and lineage"
        ],
        "warnings": [
            "ML models can perpetuate biases in training data",
            "Never deploy without validation on held-out test set",
            "Monitor for distribution drift in production",
            "Document model limitations and failure modes"
        ]
    },
    "pytorch": {
        "name": "PyTorch ML Safety Constraints",
        "patterns": [
            r"\b(100%|always|never|certain|guaranteed)\b.*\b(accurate|correct|prediction)\b",
            r"\b(autonomous|automatic)\b.*\b(critical|life|safety|medical|financial)\b.*\b(decision)\b",
            r"\b(pickle|torch\.load)\b.*\b(untrusted|user|remote|download)\b",
            r"\b(deepfake|fake|synthetic)\b.*\b(identity|person|face)\b",
        ],
        "security_requirements": [
            "Never load untrusted pickle files (arbitrary code execution risk)",
            "Use weights_only=True for torch.load when possible",
            "Validate model checksums before loading"
        ],
        "epistemic_bounds": {
            "confidence_display": "Always expose prediction confidence scores",
            "uncertainty_quantification": "Use MC Dropout or ensembles for uncertainty",
            "human_oversight": "Critical decisions require human review"
        },
        "warnings": [
            "torch.load can execute arbitrary code - only load trusted models",
            "ML models can perpetuate biases in training data",
            "Monitor for adversarial inputs in production"
        ]
    },
    "nodejs": {
        "name": "Node.js Security Constraints",
        "patterns": [
            r"\b(eval|Function\(|vm\.runIn)\b.*\b(user|input|dynamic|untrusted)\b",
            r"\b(child_process|exec|spawn)\b.*\b(user|input|untrusted)\b",
            r"\b(disable|skip|ignore)\b.*\b(helmet|csp|security|sanitize)\b",
            r"\b(SQL|query)\b.*\b(concatenat|string\s*\+|template)\b.*\b(user|input)\b",
        ],
        "security_requirements": [
            "Use parameterized queries for database operations",
            "Sanitize all user inputs",
            "Implement rate limiting on API endpoints",
            "Use helmet.js for security headers"
        ],
        "warnings": [
            "Command injection via unsanitized child_process calls",
            "SQL injection via string concatenation",
            "Prototype pollution vulnerabilities",
            "Always validate and sanitize user input"
        ]
    },
    "django": {
        "name": "Django Security Constraints",
        "patterns": [
            r"\b(raw\(|extra\(|RawSQL)\b.*\b(user|input|untrusted|%s)\b",
            r"\b(safe|mark_safe)\b.*\b(user|input|untrusted)\b",
            r"\b(CSRF_COOKIE_SECURE|SESSION_COOKIE_SECURE)\b.*\b(False)\b",
            r"\b(DEBUG)\b.*\b(True)\b.*\b(production)\b",
        ],
        "security_requirements": [
            "Use Django ORM instead of raw SQL",
            "Enable CSRF protection on all forms",
            "Set DEBUG=False in production",
            "Use secure cookie settings"
        ],
        "warnings": [
            "SQL injection via raw() with user input",
            "XSS via mark_safe() with untrusted content",
            "Always use Django's built-in protections"
        ]
    },
    "flask": {
        "name": "Flask Security Constraints",
        "patterns": [
            r"\b(render_template_string)\b.*\b(user|input|untrusted)\b",
            r"\b(Markup|safe)\b.*\b(user|input|untrusted)\b",
            r"\b(debug\s*=\s*True)\b",
            r"\b(secret_key)\b.*\b(hardcoded|default|example)\b",
        ],
        "security_requirements": [
            "Use render_template() not render_template_string() with user input",
            "Set strong SECRET_KEY from environment",
            "Disable debug mode in production",
            "Implement CSRF protection with Flask-WTF"
        ],
        "warnings": [
            "SSTI vulnerability via render_template_string",
            "Session hijacking with weak secret key",
            "Debug mode exposes sensitive information"
        ]
    }
}

# Visual Cartridge Constraints
VISUAL_CONSTRAINTS = {
    "dimensions": {"min_width": 1, "max_width": 4096, "min_height": 1, "max_height": 4096},
    "elements": {"max_count": 1000},
    "colors": {"max_palette": 256},
    "patterns": [
        r"\b(offensive|inappropriate|explicit)\b.*\b(image|graphic|visual)\b",
        r"\b(copy|steal|plagiarize)\b.*\b(logo|brand|trademark)\b",
    ]
}

# Sound Cartridge Constraints
SOUND_CONSTRAINTS = {
    "duration": {"min_ms": 1, "max_ms": 300000},  # 5 minutes max
    "frequency": {"min_hz": 1, "max_hz": 22050},
    "sample_rate": {"allowed": [22050, 44100, 48000, 96000]},
    "patterns": [
        r"\b(subliminal|hidden)\b.*\b(message|audio)\b",
        r"\b(harmful|damaging)\b.*\b(frequency|sound)\b",
    ]
}

# Sequence Cartridge Constraints
SEQUENCE_CONSTRAINTS = {
    "duration": {"min_seconds": 0.1, "max_seconds": 600},  # 10 minutes max
    "fps": {"min": 1, "max": 120},
    "resolution": {"max_width": 7680, "max_height": 4320},  # 8K max
    "patterns": [
        r"\b(seizure|epilepsy)\b.*\b(inducing|triggering)\b",
        r"\b(rapid|strobing)\b.*\b(flash|flicker)\b",
    ]
}

# Data Cartridge Constraints
DATA_CONSTRAINTS = {
    "rows": {"max": 100000},
    "columns": {"max": 1000},
    "formats": ["json", "csv", "markdown", "html"],
    "patterns": [
        r"\b(fake|fabricate|falsify)\b.*\b(data|statistics|results)\b",
        r"\b(manipulate|skew)\b.*\b(numbers|metrics)\b",
    ]
}

# Framework mappings
APPLE_FRAMEWORKS = {
    "ui": ["SwiftUI", "UIKit"],
    "data": ["CoreData", "SwiftData", "CloudKit"],
    "health": ["HealthKit", "HealthKitUI"],
    "location": ["CoreLocation", "MapKit"],
    "media": ["AVFoundation", "PhotosUI", "MusicKit"],
    "ml": ["CoreML", "Vision", "NaturalLanguage"],
    "ar": ["ARKit", "RealityKit"],
    "payments": ["StoreKit", "PassKit"],
    "notifications": ["UserNotifications"],
    "network": ["Network", "URLSession"],
    "auth": ["AuthenticationServices", "LocalAuthentication"],
}

# Component patterns for parsing
COMPONENT_PATTERNS = {
    "list": r"\b(list|table|collection|feed|timeline)\b",
    "form": r"\b(form|input|settings|preferences|profile)\b",
    "detail": r"\b(detail|view|show|display|page)\b",
    "navigation": r"\b(tab|menu|sidebar|drawer|navigation)\b",
    "map": r"\b(map|location|directions|places)\b",
    "media": r"\b(photo|video|camera|gallery|player)\b",
    "chart": r"\b(chart|graph|analytics|statistics|dashboard)\b",
    "auth": r"\b(login|signup|auth|register|account)\b",
    "chat": r"\b(chat|message|conversation|inbox)\b",
    "search": r"\b(search|filter|find|browse)\b",
}

def rosetta_parse(intent: str) -> dict:
    """Parse natural language intent into structured components."""
    intent_lower = intent.lower()

    # Detect platform
    platforms = {
        "ios": r"\b(iphone|ios|mobile app)\b",
        "ipados": r"\b(ipad|ipados|tablet)\b",
        "macos": r"\b(mac|macos|desktop)\b",
        "watchos": r"\b(watch|watchos|wearable)\b",
        "visionos": r"\b(vision|visionos|spatial|ar app)\b",
        "tvos": r"\b(tv|tvos|apple tv)\b",
    }

    detected_platform = "ios"  # default
    for platform, pattern in platforms.items():
        if re.search(pattern, intent_lower):
            detected_platform = platform
            break

    # Detect components
    detected_components = []
    for component, pattern in COMPONENT_PATTERNS.items():
        if re.search(pattern, intent_lower):
            detected_components.append(component)

    # Detect required frameworks
    framework_keywords = {
        "health": r"\b(health|fitness|workout|steps|heart rate)\b",
        "location": r"\b(map|location|gps|directions|nearby)\b",
        "media": r"\b(photo|video|camera|music|audio)\b",
        "ml": r"\b(ml|ai|recognize|detect|classify|predict)\b",
        "ar": r"\b(ar|augmented|3d|spatial)\b",
        "payments": r"\b(payment|purchase|subscription|in-app)\b",
        "notifications": r"\b(notification|reminder|alert|push)\b",
        "auth": r"\b(login|auth|face id|touch id|biometric)\b",
        "data": r"\b(save|store|sync|cloud|database)\b",
    }

    detected_frameworks = ["SwiftUI"]  # Always include SwiftUI
    for category, pattern in framework_keywords.items():
        if re.search(pattern, intent_lower):
            detected_frameworks.extend(APPLE_FRAMEWORKS.get(category, []))

    # Remove duplicates while preserving order
    detected_frameworks = list(dict.fromkeys(detected_frameworks))

    # Extract app type
    app_types = {
        "utility": r"\b(utility|tool|calculator|converter|timer)\b",
        "social": r"\b(social|community|share|friends|followers)\b",
        "productivity": r"\b(productivity|task|todo|notes|calendar)\b",
        "media": r"\b(photo|video|music|podcast|streaming)\b",
        "health": r"\b(health|fitness|wellness|meditation|sleep)\b",
        "finance": r"\b(finance|budget|expense|investment|banking)\b",
        "education": r"\b(education|learn|study|course|quiz)\b",
        "lifestyle": r"\b(lifestyle|recipe|travel|weather|news)\b",
        "game": r"\b(game|play|puzzle|arcade|trivia)\b",
    }

    app_type = "utility"  # default
    for atype, pattern in app_types.items():
        if re.search(pattern, intent_lower):
            app_type = atype
            break

    return {
        "platform": detected_platform,
        "app_type": app_type,
        "components": detected_components if detected_components else ["list", "detail"],
        "frameworks": detected_frameworks,
        "tokens": len(intent.split()),
    }

def rosetta_verify_app_constraints(intent: str) -> dict:
    """Verify intent against Apple development constraints."""
    intent_lower = intent.lower()
    passed = []
    failed = []
    warnings = []

    for key, constraint in APP_CONSTRAINTS.items():
        violation = False
        for pattern in constraint["patterns"]:
            if re.search(pattern, intent_lower):
                violation = True
                break

        if violation:
            failed.append(key)
        else:
            passed.append(key)

    # Add warnings for complex features
    if re.search(r"\b(health|healthkit)\b", intent_lower):
        warnings.append("HealthKit requires special entitlements and privacy descriptions")
    if re.search(r"\b(location|gps)\b", intent_lower):
        warnings.append("Location services require NSLocationWhenInUseUsageDescription")
    if re.search(r"\b(camera|photo)\b", intent_lower):
        warnings.append("Camera/Photos require NSCameraUsageDescription or NSPhotoLibraryUsageDescription")
    if re.search(r"\b(notification|push)\b", intent_lower):
        warnings.append("Push notifications require APNs configuration")

    return {
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "compliant": len(failed) == 0
    }

def rosetta_generate_prompt(intent: str, parsed: dict, ios_version: str) -> str:
    """Generate structured AI Studio prompt from parsed intent."""

    # Build component specifications
    component_specs = []
    for i, comp in enumerate(parsed["components"], 1):
        component_specs.append(f"{i}. {comp.title()}View")

    prompt = f"""TARGET: {parsed['platform'].upper()} {ios_version}
FRAMEWORK: {parsed['frameworks'][0]}
APP_TYPE: {parsed['app_type']}
DATE: {time.strftime('%Y-%m-%d')}

REQUIREMENTS:
{intent}

ARCHITECTURE:
- Pattern: MVVM
- State: @Observable (iOS 17+) or ObservableObject
- Navigation: NavigationStack

FRAMEWORKS_REQUIRED:
{chr(10).join(f'- {fw}' for fw in parsed['frameworks'])}

SCREENS:
{chr(10).join(component_specs)}

DESIGN_SYSTEM:
- Typography: SF Pro (system default)
- Icons: SF Symbols
- Colors: Use semantic colors (e.g., .primary, .secondary, .accent)
- Spacing: Use standard SwiftUI spacing (8pt grid)

CONSTRAINTS:
- App Store Guidelines: VERIFY
- Human Interface Guidelines: COMPLY
- Privacy: DECLARE_ALL_USAGE
- Accessibility: SUPPORT_VOICEOVER

OUTPUT_FORMAT:
Generate complete, compilable Swift code with:
1. Data models
2. View models
3. Views (SwiftUI)
4. Navigation structure
5. Preview providers

CODE_STYLE:
- Use Swift 5.9+ syntax
- Prefer async/await for concurrency
- Use property wrappers appropriately
- Include MARK comments for sections"""

    return prompt

def rosetta_compile(intent: str, target_platform: str = "iOS", ios_version: str = "18.0") -> dict:
    """Full compilation pipeline: parse → verify → generate."""

    # Step 1: Parse intent
    parsed = rosetta_parse(intent)
    parsed["platform"] = target_platform.lower()

    # Step 2: Verify against content constraints (reuse existing)
    content_check = check_constraints(intent, list(CONSTRAINTS.keys()))

    # Step 3: Verify against app development constraints
    app_check = rosetta_verify_app_constraints(intent)

    # Step 4: Determine if compilation should proceed
    all_passed = len(content_check["failed"]) == 0 and app_check["compliant"]

    # Step 5: Generate prompt if verified
    prompt = None
    if all_passed:
        prompt = rosetta_generate_prompt(intent, parsed, ios_version)

    return {
        "parsed": parsed,
        "content_constraints": content_check,
        "app_constraints": app_check,
        "verified": all_passed,
        "prompt": prompt,
    }

# ═══════════════════════════════════════════════════════════════════════════
# LEDGER - APPEND-ONLY AUDIT TRAIL
# ═══════════════════════════════════════════════════════════════════════════

def compute_merkle_root(entries: List[Dict]) -> str:
    """Compute Merkle root of ledger entries for integrity verification."""
    if not entries:
        return "EMPTY"

    hashes = [e.get("hash", "") for e in entries]

    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])  # Duplicate last if odd
        new_hashes = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i + 1]
            new_hashes.append(hashlib.sha256(combined.encode()).hexdigest()[:16].upper())
        hashes = new_hashes

    return hashes[0]

def ledger_append(entry_type: str, payload: dict, persist: bool = True) -> dict:
    """Append entry to immutable ledger with cryptographic chaining."""
    global LEDGER

    timestamp = int(time.time())
    entry_id = len(LEDGER)

    # Create entry with cryptographic chain
    prev_hash = LEDGER[-1]["hash"] if LEDGER else "GENESIS"

    # Include nonce for additional entropy
    nonce = hashlib.sha256(f"{timestamp}{entry_id}{os.urandom(8).hex()}".encode()).hexdigest()[:8]

    entry = {
        "id": entry_id,
        "type": entry_type,
        "payload": payload,
        "timestamp": timestamp,
        "prev_hash": prev_hash,
        "nonce": nonce,
    }

    # Generate hash of this entry (includes all fields for integrity)
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256(entry_str.encode()).hexdigest()[:16].upper()

    # Append (immutable - never modify existing entries)
    if len(LEDGER) < MAX_LEDGER_SIZE:
        LEDGER.append(entry)
    else:
        # Rotate: remove oldest, keep recent (with warning)
        LEDGER = LEDGER[1:] + [entry]

    # Persist to storage
    if persist:
        save_ledger()

    return entry

def ledger_verify_chain() -> dict:
    """Verify integrity of ledger chain with comprehensive checks."""
    if not LEDGER:
        return {"valid": True, "entries": 0, "message": "Ledger empty", "merkle_root": "EMPTY"}

    errors = []
    for i, entry in enumerate(LEDGER):
        # Verify genesis block
        if i == 0:
            if entry.get("prev_hash") != "GENESIS":
                errors.append({"index": i, "error": "Genesis block prev_hash corrupted"})
        else:
            # Verify chain linkage
            if entry.get("prev_hash") != LEDGER[i - 1].get("hash"):
                errors.append({"index": i, "error": "Chain linkage broken"})

        # Verify entry hash integrity
        entry_copy = {k: v for k, v in entry.items() if k != "hash"}
        expected_hash = hashlib.sha256(json.dumps(entry_copy, sort_keys=True).encode()).hexdigest()[:16].upper()
        if entry.get("hash") != expected_hash:
            errors.append({"index": i, "error": "Entry hash mismatch (possible tampering)"})

    merkle_root = compute_merkle_root(LEDGER)

    if errors:
        return {
            "valid": False,
            "entries": len(LEDGER),
            "errors": errors,
            "message": f"Chain integrity compromised: {len(errors)} error(s)",
            "merkle_root": merkle_root
        }

    return {
        "valid": True,
        "entries": len(LEDGER),
        "message": "Chain intact - all entries verified",
        "merkle_root": merkle_root,
        "first_entry": LEDGER[0]["timestamp"] if LEDGER else None,
        "last_entry": LEDGER[-1]["timestamp"] if LEDGER else None
    }

# ═══════════════════════════════════════════════════════════════════════════
# SIGNATURE AUTHORITY
# ═══════════════════════════════════════════════════════════════════════════

def sign_payload(payload: str, context: str = None) -> dict:
    """Generate cryptographic signature for payload."""
    timestamp = int(time.time())

    # Create signature components
    sig_input = f"{payload}{context or ''}{timestamp}"
    signature = hashlib.sha256(sig_input.encode()).hexdigest()

    # Create verification token
    token = hashlib.sha256(f"{signature}{timestamp}".encode()).hexdigest()[:24].upper()

    return {
        "signature": signature,
        "token": token,
        "timestamp": timestamp,
        "payload_hash": hashlib.sha256(payload.encode()).hexdigest()[:16].upper(),
        "verified": True
    }

# ═══════════════════════════════════════════════════════════════════════════
# CARTRIDGE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def check_cartridge_constraints(intent: str, patterns: list) -> dict:
    """Check intent against cartridge-specific patterns."""
    intent_lower = intent.lower()
    violations = []

    for pattern in patterns:
        if re.search(pattern, intent_lower):
            violations.append(pattern)

    return {"passed": len(violations) == 0, "violations": violations}

def visual_cartridge_compile(request: dict) -> dict:
    """Compile visual intent into SVG specification."""
    intent = request["intent"]
    width = min(max(request.get("width", 800), 1), VISUAL_CONSTRAINTS["dimensions"]["max_width"])
    height = min(max(request.get("height", 600), 1), VISUAL_CONSTRAINTS["dimensions"]["max_height"])
    max_elements = min(request.get("max_elements", 100), VISUAL_CONSTRAINTS["elements"]["max_count"])

    # Verify constraints
    content_check = check_constraints(intent, list(CONSTRAINTS.keys()))
    visual_check = check_cartridge_constraints(intent, VISUAL_CONSTRAINTS["patterns"])

    verified = len(content_check["failed"]) == 0 and visual_check["passed"]

    # Parse visual elements from intent
    elements = []
    element_patterns = {
        "circle": r"\b(circle|dot|point|round)\b",
        "rect": r"\b(rectangle|square|box|card)\b",
        "line": r"\b(line|stroke|path|border)\b",
        "text": r"\b(text|label|title|heading)\b",
        "polygon": r"\b(triangle|polygon|shape)\b",
    }

    for elem_type, pattern in element_patterns.items():
        if re.search(pattern, intent.lower()):
            elements.append(elem_type)

    if not elements:
        elements = ["rect", "text"]  # Default

    # Generate SVG spec
    spec = None
    if verified:
        spec = {
            "type": "svg",
            "viewBox": f"0 0 {width} {height}",
            "width": width,
            "height": height,
            "elements": elements[:max_elements],
            "style": {
                "background": "#ffffff",
                "stroke": "#000000",
                "fill": "#e0e0e0"
            }
        }

    return {
        "verified": verified,
        "constraints": {
            "content": content_check,
            "visual": visual_check,
            "bounds": {"width": width, "height": height, "max_elements": max_elements}
        },
        "spec": spec
    }

def sound_cartridge_compile(request: dict) -> dict:
    """Compile sound intent into audio specification."""
    intent = request["intent"]
    duration_ms = min(max(request.get("duration_ms", 5000), 1), SOUND_CONSTRAINTS["duration"]["max_ms"])
    min_freq = max(request.get("min_frequency", 20.0), SOUND_CONSTRAINTS["frequency"]["min_hz"])
    max_freq = min(request.get("max_frequency", 20000.0), SOUND_CONSTRAINTS["frequency"]["max_hz"])
    sample_rate = request.get("sample_rate", 44100)

    if sample_rate not in SOUND_CONSTRAINTS["sample_rate"]["allowed"]:
        sample_rate = 44100

    # Verify constraints
    content_check = check_constraints(intent, list(CONSTRAINTS.keys()))
    sound_check = check_cartridge_constraints(intent, SOUND_CONSTRAINTS["patterns"])

    verified = len(content_check["failed"]) == 0 and sound_check["passed"]

    # Parse sound characteristics
    characteristics = []
    sound_patterns = {
        "tone": r"\b(tone|beep|note|pitch)\b",
        "melody": r"\b(melody|tune|music|song)\b",
        "effect": r"\b(effect|sound|sfx|audio)\b",
        "voice": r"\b(voice|speech|spoken|narration)\b",
        "ambient": r"\b(ambient|background|atmosphere)\b",
    }

    for char_type, pattern in sound_patterns.items():
        if re.search(pattern, intent.lower()):
            characteristics.append(char_type)

    if not characteristics:
        characteristics = ["tone"]

    spec = None
    if verified:
        spec = {
            "type": "audio",
            "duration_ms": duration_ms,
            "sample_rate": sample_rate,
            "frequency_range": {"min": min_freq, "max": max_freq},
            "characteristics": characteristics,
            "format": "wav",
            "channels": 2
        }

    return {
        "verified": verified,
        "constraints": {
            "content": content_check,
            "sound": sound_check,
            "bounds": {"duration_ms": duration_ms, "frequency_range": [min_freq, max_freq]}
        },
        "spec": spec
    }

def sequence_cartridge_compile(request: dict) -> dict:
    """Compile sequence intent into video/animation specification."""
    intent = request["intent"]
    duration = min(max(request.get("duration_seconds", 30.0), 0.1), SEQUENCE_CONSTRAINTS["duration"]["max_seconds"])
    fps = min(max(request.get("fps", 30), 1), SEQUENCE_CONSTRAINTS["fps"]["max"])
    width = min(request.get("width", 1920), SEQUENCE_CONSTRAINTS["resolution"]["max_width"])
    height = min(request.get("height", 1080), SEQUENCE_CONSTRAINTS["resolution"]["max_height"])
    max_scenes = min(request.get("max_scenes", 10), 50)

    # Verify constraints
    content_check = check_constraints(intent, list(CONSTRAINTS.keys()))
    sequence_check = check_cartridge_constraints(intent, SEQUENCE_CONSTRAINTS["patterns"])

    verified = len(content_check["failed"]) == 0 and sequence_check["passed"]

    # Parse sequence elements
    sequence_type = "animation"
    if re.search(r"\b(video|film|movie|clip)\b", intent.lower()):
        sequence_type = "video"
    elif re.search(r"\b(slideshow|presentation|slides)\b", intent.lower()):
        sequence_type = "slideshow"

    spec = None
    if verified:
        total_frames = int(duration * fps)
        spec = {
            "type": sequence_type,
            "duration_seconds": duration,
            "fps": fps,
            "total_frames": total_frames,
            "resolution": {"width": width, "height": height},
            "max_scenes": max_scenes,
            "format": "mp4",
            "codec": "h264"
        }

    return {
        "verified": verified,
        "constraints": {
            "content": content_check,
            "sequence": sequence_check,
            "bounds": {"duration": duration, "fps": fps, "resolution": f"{width}x{height}"}
        },
        "spec": spec
    }

def data_cartridge_compile(request: dict) -> dict:
    """Compile data intent into report specification."""
    intent = request["intent"]
    data = request.get("data", {})
    output_format = request.get("format", "json")
    max_rows = min(request.get("max_rows", 1000), DATA_CONSTRAINTS["rows"]["max"])
    include_stats = request.get("include_statistics", True)

    if output_format not in DATA_CONSTRAINTS["formats"]:
        output_format = "json"

    # Verify constraints
    content_check = check_constraints(intent, list(CONSTRAINTS.keys()))
    data_check = check_cartridge_constraints(intent, DATA_CONSTRAINTS["patterns"])

    verified = len(content_check["failed"]) == 0 and data_check["passed"]

    # Parse report type
    report_type = "general"
    report_patterns = {
        "financial": r"\b(financial|revenue|profit|expense|budget)\b",
        "analytics": r"\b(analytics|metrics|kpi|performance)\b",
        "summary": r"\b(summary|overview|report|digest)\b",
        "comparison": r"\b(comparison|compare|versus|vs)\b",
        "trend": r"\b(trend|growth|change|over time)\b",
    }

    for rtype, pattern in report_patterns.items():
        if re.search(pattern, intent.lower()):
            report_type = rtype
            break

    spec = None
    if verified:
        spec = {
            "type": "report",
            "report_type": report_type,
            "format": output_format,
            "max_rows": max_rows,
            "include_statistics": include_stats,
            "sections": ["header", "summary", "data", "footer"],
            "data_provided": bool(data)
        }

        if include_stats and data:
            # Calculate basic statistics if numeric data provided
            numeric_values = []
            for v in data.values():
                if isinstance(v, (int, float)):
                    numeric_values.append(v)
                elif isinstance(v, list):
                    numeric_values.extend([x for x in v if isinstance(x, (int, float))])

            if numeric_values:
                spec["statistics"] = {
                    "count": len(numeric_values),
                    "sum": round(sum(numeric_values), 4),
                    "mean": round(sum(numeric_values) / len(numeric_values), 4),
                    "min": round(min(numeric_values), 4),
                    "max": round(max(numeric_values), 4)
                }

    return {
        "verified": verified,
        "constraints": {
            "content": content_check,
            "data": data_check,
            "bounds": {"max_rows": max_rows, "format": output_format}
        },
        "spec": spec
    }

def verify_framework_constraints(intent: str, framework: str) -> dict:
    """Verify intent against framework-specific constraints."""
    framework_lower = framework.lower()

    if framework_lower not in FRAMEWORK_CONSTRAINTS:
        return {
            "framework": framework,
            "found": False,
            "message": f"No specific constraints for {framework}"
        }

    constraint = FRAMEWORK_CONSTRAINTS[framework_lower]
    intent_lower = intent.lower()
    violations = []

    for pattern in constraint["patterns"]:
        if re.search(pattern, intent_lower):
            violations.append(pattern)

    result = {
        "framework": framework,
        "found": True,
        "name": constraint["name"],
        "passed": len(violations) == 0,
        "violations": violations,
        "warnings": constraint.get("warnings", [])
    }

    # Add framework-specific metadata
    if "required_entitlements" in constraint:
        result["required_entitlements"] = constraint["required_entitlements"]
    if "required_descriptions" in constraint:
        result["required_descriptions"] = constraint["required_descriptions"]
    if "required_features" in constraint:
        result["required_features"] = constraint["required_features"]
    if "safety_requirements" in constraint:
        result["safety_requirements"] = constraint["safety_requirements"]
    if "epistemic_bounds" in constraint:
        result["epistemic_bounds"] = constraint["epistemic_bounds"]

    return result

# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Newton OS",
    description="Ada speaks. Tahoe remembers. THIA sees.",
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newton OS - AI Verification Layer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(180deg, #111 0%, #0a0a0a 100%);
            padding: 48px 24px;
            border-bottom: 1px solid #222;
        }
        .header-content { max-width: 900px; margin: 0 auto; }
        h1 { font-size: 42px; font-weight: 700; margin-bottom: 8px; letter-spacing: -1px; }
        .tagline { color: #00875a; font-size: 20px; margin-bottom: 8px; font-weight: 500; }
        .subtitle { color: #666; font-size: 15px; margin-bottom: 24px; }
        .status-bar {
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
            font-size: 13px;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00875a;
        }
        .status-dot.pending { background: #f59e0b; }
        .container { max-width: 900px; margin: 0 auto; padding: 32px 24px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        @media (max-width: 700px) { .grid { grid-template-columns: 1fr; } }
        .section { margin-bottom: 48px; }
        .section-title {
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #222;
        }
        .card {
            background: #111;
            border: 1px solid #222;
            padding: 20px;
            border-radius: 8px;
            transition: border-color 0.2s;
        }
        .card:hover { border-color: #333; }
        .card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
        .method {
            display: inline-block;
            padding: 3px 8px;
            font-size: 10px;
            font-weight: 700;
            border-radius: 4px;
            letter-spacing: 0.05em;
        }
        .post { background: #00875a; color: #000; }
        .get { background: #3b82f6; color: #fff; }
        .path { font-family: 'SF Mono', Consolas, monospace; font-size: 14px; font-weight: 600; }
        .card-desc { color: #888; font-size: 13px; line-height: 1.5; }
        .endpoint-group { margin-bottom: 32px; }
        .endpoint-group-title {
            font-size: 14px;
            font-weight: 600;
            color: #00875a;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .try-section {
            background: #0d0d0d;
            border: 1px solid #1a1a1a;
            border-radius: 12px;
            padding: 24px;
        }
        .tabs {
            display: flex;
            gap: 4px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            background: #111;
            padding: 4px;
            border-radius: 8px;
        }
        .tab {
            padding: 10px 16px;
            background: transparent;
            border: none;
            border-radius: 6px;
            color: #666;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
        }
        .tab:hover { color: #999; }
        .tab.active { background: #00875a; color: #000; }
        .form-section { display: none; }
        .form-section.active { display: block; }
        input, select, textarea {
            width: 100%;
            padding: 14px 16px;
            font-size: 14px;
            background: #161616;
            border: 1px solid #2a2a2a;
            border-radius: 6px;
            color: #e0e0e0;
            font-family: inherit;
            margin-bottom: 12px;
            transition: border-color 0.2s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #00875a;
        }
        textarea {
            font-family: 'SF Mono', Consolas, monospace;
            font-size: 13px;
            min-height: 120px;
            resize: vertical;
        }
        .input-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        @media (max-width: 500px) { .input-row { grid-template-columns: 1fr; } }
        label {
            display: block;
            font-size: 12px;
            color: #666;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        button {
            background: #00875a;
            color: #000;
            border: none;
            padding: 14px 32px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            border-radius: 6px;
            transition: background 0.2s;
        }
        button:hover { background: #00a06a; }
        button:disabled { background: #333; color: #666; cursor: not-allowed; }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #111;
            border: 1px solid #222;
            border-radius: 8px;
            font-family: 'SF Mono', Consolas, monospace;
            font-size: 12px;
            white-space: pre-wrap;
            display: none;
            max-height: 400px;
            overflow-y: auto;
        }
        .result.show { display: block; }
        .result.success { border-color: #00875a; }
        .result.error { border-color: #ef4444; }
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid #222;
        }
        .result-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        }
        .result-badge {
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }
        .result-badge.verified { background: #00875a; color: #000; }
        .result-badge.failed { background: #ef4444; color: #fff; }
        footer {
            border-top: 1px solid #222;
            padding: 32px 24px;
            text-align: center;
            font-size: 13px;
            color: #444;
        }
        footer a { color: #00875a; text-decoration: none; }
        footer a:hover { text-decoration: underline; }
        .help-text { font-size: 12px; color: #555; margin-top: -8px; margin-bottom: 12px; }
        .ledger-entry {
            background: #161616;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .ledger-entry-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
            color: #888;
        }
        .ledger-entry-type { color: #00875a; font-weight: 600; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>Newton OS</h1>
            <p class="tagline">The AI Verification Layer. 1 == 1</p>
            <p class="subtitle">Ada speaks. Tahoe remembers. THIA sees. Rosetta compiles.</p>
            <div class="status-bar">
                <div class="status-item">
                    <div class="status-dot" id="health-dot"></div>
                    <span id="health-status">Checking...</span>
                </div>
                <div class="status-item">
                    <span style="color: #666;">Version:</span>
                    <span id="version">-</span>
                </div>
                <div class="status-item">
                    <span style="color: #666;">Ledger:</span>
                    <span id="ledger-count">-</span>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- API Reference -->
        <div class="section">
            <div class="section-title">API Reference</div>

            <div class="endpoint-group">
                <div class="endpoint-group-title">Core Verification</div>
                <div class="grid">
                    <div class="card">
                        <div class="card-header">
                            <span class="method post">POST</span>
                            <span class="path">/verify</span>
                        </div>
                        <p class="card-desc">Verify intent against harm, medical, legal, and security constraints</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method post">POST</span>
                            <span class="path">/analyze</span>
                        </div>
                        <p class="card-desc">THIA anomaly detection using Z-score, IQR, or MAD methods</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method post">POST</span>
                            <span class="path">/compile</span>
                        </div>
                        <p class="card-desc">Rosetta compiler: natural language to AI Studio prompts</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method post">POST</span>
                            <span class="path">/analyze/batch</span>
                        </div>
                        <p class="card-desc">Batch analysis of multiple datasets in one request</p>
                    </div>
                </div>
            </div>

            <div class="endpoint-group">
                <div class="endpoint-group-title">Extension Cartridges</div>
                <div class="grid">
                    <div class="card">
                        <div class="card-header">
                            <span class="method post">POST</span>
                            <span class="path">/cartridge/visual</span>
                        </div>
                        <p class="card-desc">SVG generation with dimension and element constraints</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method post">POST</span>
                            <span class="path">/cartridge/sound</span>
                        </div>
                        <p class="card-desc">Audio specs with frequency and duration limits</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method post">POST</span>
                            <span class="path">/cartridge/sequence</span>
                        </div>
                        <p class="card-desc">Video/animation specs with frame constraints</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method post">POST</span>
                            <span class="path">/cartridge/data</span>
                        </div>
                        <p class="card-desc">Report generation with statistical bounds</p>
                    </div>
                </div>
            </div>

            <div class="endpoint-group">
                <div class="endpoint-group-title">Security & Audit</div>
                <div class="grid">
                    <div class="card">
                        <div class="card-header">
                            <span class="method post">POST</span>
                            <span class="path">/sign</span>
                        </div>
                        <p class="card-desc">Generate cryptographic signatures for payloads</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method get">GET</span>
                            <span class="path">/ledger</span>
                        </div>
                        <p class="card-desc">Append-only audit trail with chain verification</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method get">GET</span>
                            <span class="path">/ledger/verify</span>
                        </div>
                        <p class="card-desc">Verify integrity of the cryptographic ledger chain</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method post">POST</span>
                            <span class="path">/frameworks/verify</span>
                        </div>
                        <p class="card-desc">Verify against Apple framework constraints</p>
                    </div>
                </div>
            </div>

            <div class="endpoint-group">
                <div class="endpoint-group-title">Metadata</div>
                <div class="grid">
                    <div class="card">
                        <div class="card-header">
                            <span class="method get">GET</span>
                            <span class="path">/health</span>
                        </div>
                        <p class="card-desc">System status, version, and capabilities</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method get">GET</span>
                            <span class="path">/constraints</span>
                        </div>
                        <p class="card-desc">List available content constraints</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method get">GET</span>
                            <span class="path">/methods</span>
                        </div>
                        <p class="card-desc">List THIA analysis methods</p>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <span class="method get">GET</span>
                            <span class="path">/frameworks</span>
                        </div>
                        <p class="card-desc">List Apple frameworks by category</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Interactive Console -->
        <div class="section">
            <div class="section-title">Interactive Console</div>
            <div class="try-section">
                <div class="tabs">
                    <button class="tab active" onclick="switchTab('verify')">Verify</button>
                    <button class="tab" onclick="switchTab('analyze')">Analyze</button>
                    <button class="tab" onclick="switchTab('compile')">Compile</button>
                    <button class="tab" onclick="switchTab('visual')">Visual</button>
                    <button class="tab" onclick="switchTab('sound')">Sound</button>
                    <button class="tab" onclick="switchTab('data')">Data</button>
                    <button class="tab" onclick="switchTab('sign')">Sign</button>
                    <button class="tab" onclick="switchTab('ledger')">Ledger</button>
                </div>

                <!-- Verify Form -->
                <div id="verify-form" class="form-section active">
                    <label>Input Text</label>
                    <textarea id="verify-input" placeholder="Enter text to verify against safety constraints...">Help me write a business plan for a sustainable energy startup</textarea>
                    <p class="help-text">Checks against: harm, medical, legal, security constraints</p>
                    <button onclick="runVerify()">Verify Intent</button>
                </div>

                <!-- Analyze Form -->
                <div id="analyze-form" class="form-section">
                    <label>Data Points (comma-separated)</label>
                    <textarea id="analyze-input" placeholder="Enter numbers...">45.2, 46.1, 44.8, 45.5, 45.9, 46.2, 45.1, 44.9, 45.3, 102.4, 45.7, 46.0, 0.5, 45.8</textarea>
                    <div class="input-row">
                        <div>
                            <label>Method</label>
                            <select id="analyze-method">
                                <option value="zscore">Z-Score</option>
                                <option value="iqr">IQR</option>
                                <option value="mad">MAD</option>
                                <option value="all">All Methods</option>
                            </select>
                        </div>
                        <div>
                            <label>Threshold</label>
                            <input type="number" id="analyze-threshold" value="3.0" step="0.1">
                        </div>
                    </div>
                    <button onclick="runAnalyze()">Detect Anomalies</button>
                </div>

                <!-- Compile Form -->
                <div id="compile-form" class="form-section">
                    <label>App Intent</label>
                    <textarea id="compile-input" placeholder="Describe the app you want to build...">Build a fitness tracking app with workout logging, HealthKit integration, and progress charts</textarea>
                    <div class="input-row">
                        <div>
                            <label>Platform</label>
                            <select id="compile-platform">
                                <option value="iOS">iOS</option>
                                <option value="iPadOS">iPadOS</option>
                                <option value="macOS">macOS</option>
                                <option value="watchOS">watchOS</option>
                                <option value="visionOS">visionOS</option>
                            </select>
                        </div>
                        <div>
                            <label>iOS Version</label>
                            <input type="text" id="compile-version" value="18.0">
                        </div>
                    </div>
                    <button onclick="runCompile()">Compile to Prompt</button>
                </div>

                <!-- Visual Cartridge Form -->
                <div id="visual-form" class="form-section">
                    <label>Visual Intent</label>
                    <textarea id="visual-input" placeholder="Describe the visual you want to create...">Create a modern dashboard with circular progress indicators and data cards</textarea>
                    <div class="input-row">
                        <div>
                            <label>Width</label>
                            <input type="number" id="visual-width" value="800">
                        </div>
                        <div>
                            <label>Height</label>
                            <input type="number" id="visual-height" value="600">
                        </div>
                    </div>
                    <button onclick="runVisual()">Generate Visual Spec</button>
                </div>

                <!-- Sound Cartridge Form -->
                <div id="sound-form" class="form-section">
                    <label>Sound Intent</label>
                    <textarea id="sound-input" placeholder="Describe the audio you want to create...">Create a gentle notification tone with a soft melody</textarea>
                    <div class="input-row">
                        <div>
                            <label>Duration (ms)</label>
                            <input type="number" id="sound-duration" value="3000">
                        </div>
                        <div>
                            <label>Sample Rate</label>
                            <select id="sound-samplerate">
                                <option value="44100">44100 Hz</option>
                                <option value="48000">48000 Hz</option>
                                <option value="22050">22050 Hz</option>
                            </select>
                        </div>
                    </div>
                    <button onclick="runSound()">Generate Sound Spec</button>
                </div>

                <!-- Data Cartridge Form -->
                <div id="data-form" class="form-section">
                    <label>Report Intent</label>
                    <textarea id="data-input" placeholder="Describe the report you want to generate...">Generate a quarterly sales summary with trend analysis</textarea>
                    <div class="input-row">
                        <div>
                            <label>Format</label>
                            <select id="data-format">
                                <option value="json">JSON</option>
                                <option value="markdown">Markdown</option>
                                <option value="csv">CSV</option>
                            </select>
                        </div>
                        <div>
                            <label>Max Rows</label>
                            <input type="number" id="data-maxrows" value="1000">
                        </div>
                    </div>
                    <button onclick="runData()">Generate Report Spec</button>
                </div>

                <!-- Sign Form -->
                <div id="sign-form" class="form-section">
                    <label>Payload</label>
                    <textarea id="sign-payload" placeholder="Enter content to sign...">{"transaction": "ABC123", "amount": 150.00, "timestamp": "2025-01-01"}</textarea>
                    <label>Context (optional)</label>
                    <input type="text" id="sign-context" placeholder="e.g., contract-2025, invoice-001">
                    <button onclick="runSign()">Generate Signature</button>
                </div>

                <!-- Ledger View -->
                <div id="ledger-form" class="form-section">
                    <div class="input-row">
                        <div>
                            <label>Limit</label>
                            <input type="number" id="ledger-limit" value="10">
                        </div>
                        <div>
                            <label>Offset</label>
                            <input type="number" id="ledger-offset" value="0">
                        </div>
                    </div>
                    <button onclick="runLedger()">View Ledger</button>
                    <button onclick="verifyLedger()" style="margin-top: 8px; background: #3b82f6;">Verify Chain Integrity</button>
                </div>

                <div id="result" class="result"></div>
            </div>
        </div>
    </div>

    <footer>
        <p style="margin-bottom: 8px;"><strong>Newton OS</strong> by <a href="https://parcri.net">Ada Computing Company</a></p>
        <p>Houston, Texas · <a href="mailto:Jn.Lewis1@outlook.com">Jn.Lewis1@outlook.com</a></p>
        <p style="margin-top: 12px; color: #333;">The constraint IS the product. The compiler makes the constraint portable.</p>
    </footer>

    <script>
        // Initialize health check
        async function checkHealth() {
            try {
                const res = await fetch('/health');
                const data = await res.json();
                document.getElementById('health-dot').style.background = '#00875a';
                document.getElementById('health-status').textContent = data.status === 'ok' ? 'Operational' : 'Degraded';
                document.getElementById('version').textContent = data.engine;
                document.getElementById('ledger-count').textContent = data.ledger_entries + ' entries';
            } catch (e) {
                document.getElementById('health-dot').style.background = '#ef4444';
                document.getElementById('health-status').textContent = 'Offline';
            }
        }
        checkHealth();

        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.querySelectorAll('.form-section').forEach(f => f.classList.remove('active'));
            document.getElementById(tab + '-form').classList.add('active');
            document.getElementById('result').classList.remove('show');
        }

        function showResult(data, success = true) {
            const el = document.getElementById('result');
            el.textContent = JSON.stringify(data, null, 2);
            el.className = 'result show ' + (success ? 'success' : 'error');
        }

        async function runVerify() {
            const input = document.getElementById('verify-input').value;
            if (!input) return;
            try {
                const res = await fetch('/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ input })
                });
                const data = await res.json();
                showResult(data, data.verified);
            } catch (e) { showResult({ error: e.message }, false); }
        }

        async function runAnalyze() {
            const input = document.getElementById('analyze-input').value;
            const method = document.getElementById('analyze-method').value;
            const threshold = parseFloat(document.getElementById('analyze-threshold').value);
            if (!input) return;
            const dataArr = input.split(',').map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
            try {
                const res = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ data: dataArr, method, threshold })
                });
                const data = await res.json();
                showResult(data, !data.error);
            } catch (e) { showResult({ error: e.message }, false); }
        }

        async function runCompile() {
            const intent = document.getElementById('compile-input').value;
            const target_platform = document.getElementById('compile-platform').value;
            const ios_version = document.getElementById('compile-version').value;
            if (!intent) return;
            try {
                const res = await fetch('/compile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ intent, target_platform, ios_version })
                });
                const data = await res.json();
                showResult(data, data.compiled);
            } catch (e) { showResult({ error: e.message }, false); }
        }

        async function runVisual() {
            const intent = document.getElementById('visual-input').value;
            const width = parseInt(document.getElementById('visual-width').value);
            const height = parseInt(document.getElementById('visual-height').value);
            if (!intent) return;
            try {
                const res = await fetch('/cartridge/visual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ intent, width, height })
                });
                const data = await res.json();
                showResult(data, data.verified);
            } catch (e) { showResult({ error: e.message }, false); }
        }

        async function runSound() {
            const intent = document.getElementById('sound-input').value;
            const duration_ms = parseInt(document.getElementById('sound-duration').value);
            const sample_rate = parseInt(document.getElementById('sound-samplerate').value);
            if (!intent) return;
            try {
                const res = await fetch('/cartridge/sound', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ intent, duration_ms, sample_rate })
                });
                const data = await res.json();
                showResult(data, data.verified);
            } catch (e) { showResult({ error: e.message }, false); }
        }

        async function runData() {
            const intent = document.getElementById('data-input').value;
            const format = document.getElementById('data-format').value;
            const max_rows = parseInt(document.getElementById('data-maxrows').value);
            if (!intent) return;
            try {
                const res = await fetch('/cartridge/data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ intent, format, max_rows })
                });
                const data = await res.json();
                showResult(data, data.verified);
            } catch (e) { showResult({ error: e.message }, false); }
        }

        async function runSign() {
            const payload = document.getElementById('sign-payload').value;
            const context = document.getElementById('sign-context').value;
            if (!payload) return;
            try {
                const res = await fetch('/sign', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ payload, context: context || null })
                });
                const data = await res.json();
                showResult(data, data.verified);
            } catch (e) { showResult({ error: e.message }, false); }
        }

        async function runLedger() {
            const limit = parseInt(document.getElementById('ledger-limit').value);
            const offset = parseInt(document.getElementById('ledger-offset').value);
            try {
                const res = await fetch(`/ledger?limit=${limit}&offset=${offset}`);
                const data = await res.json();
                showResult(data, data.chain?.valid);
            } catch (e) { showResult({ error: e.message }, false); }
        }

        async function verifyLedger() {
            try {
                const res = await fetch('/ledger/verify');
                const data = await res.json();
                showResult(data, data.valid);
            } catch (e) { showResult({ error: e.message }, false); }
        }
    </script>
</body>
</html>
"""

@app.get("/ada", response_class=HTMLResponse)
async def ada_interface():
    """Ada chat interface with Grounding Engine integration."""
    ada_path = Path(__file__).parent / "ada.html"
    if ada_path.exists():
        return ada_path.read_text()
    return "<h1>Ada interface not found</h1>"

@app.get("/health")
async def health():
    """Health check endpoint."""
    chain_status = ledger_verify_chain()
    return {
        "status": "ok",
        "engine": ENGINE,
        "capabilities": [
            "verify", "analyze", "compile", "ground",
            "cartridge/visual", "cartridge/sound", "cartridge/sequence", "cartridge/data",
            "ledger", "sign",
            "frameworks/verify"
        ],
        "security": {
            "auth_enabled": AUTH_ENABLED,
            "rate_limiting": True,
            "rate_limit_window_seconds": RATE_LIMIT_WINDOW
        },
        "ledger": {
            "entries": len(LEDGER),
            "chain_valid": chain_status["valid"],
            "merkle_root": chain_status.get("merkle_root", "EMPTY"),
            "persistent_storage": str(LEDGER_PATH)
        },
        "frameworks_supported": list(FRAMEWORK_CONSTRAINTS.keys()),
        "timestamp": int(time.time())
    }

@app.get("/constraints")
async def get_constraints():
    """List available constraints."""
    return {
        "constraints": list(CONSTRAINTS.keys()),
        "details": {k: v["name"] for k, v in CONSTRAINTS.items()}
    }

@app.get("/methods")
async def get_methods():
    """List available analysis methods."""
    return {
        "methods": ["zscore", "iqr", "mad", "all"],
        "details": {
            "zscore": "Standard deviation based detection (default threshold: 3σ)",
            "iqr": "Interquartile range based detection (default threshold: 1.5×IQR)",
            "mad": "Median absolute deviation based detection (default threshold: 3)",
            "all": "Run all methods and return combined results"
        }
    }

@app.post("/verify")
async def verify(request: VerifyRequest):
    """Verify text against constraints."""
    text = request.input.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input required")

    constraint_list = request.constraints or list(CONSTRAINTS.keys())

    # Process
    signal = melt(text)
    result = snap(signal)
    constraints = check_constraints(text, constraint_list)

    # Determine final status
    verified = result["verified"] and len(constraints["failed"]) == 0
    reason = None
    if not result["verified"]:
        reason = "Signal outside verification threshold"
    elif constraints["failed"]:
        reason = f"Constraint violation: {', '.join(constraints['failed'])}"

    # Generate fingerprint
    timestamp = int(time.time())
    fp = fingerprint(f"{signal}{result['code']}{timestamp}")

    return {
        "verified": verified,
        "code": 200 if verified else 1202,
        "signal": signal,
        "distance": result["distance"],
        "confidence": result["confidence"],
        "constraints_passed": constraints["passed"],
        "constraints_failed": constraints["failed"],
        "reason": reason,
        "fingerprint": fp,
        "timestamp": timestamp,
        "engine": ENGINE
    }

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """Analyze data for anomalies using THIA."""
    if not request.data or len(request.data) < 2:
        raise HTTPException(status_code=400, detail="At least 2 data points required")

    # Generate input fingerprint
    input_fp = fingerprint(request.data)

    # Run analysis
    result = thia_analyze(
        values=request.data,
        method=request.method,
        threshold=request.threshold
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Generate output fingerprint
    timestamp = int(time.time())
    output_fp = fingerprint(f"{result}{timestamp}")

    # Add labels if provided
    if request.labels and len(request.labels) == len(request.data):
        if request.method != "all":
            result["anomaly_labels"] = [request.labels[i] for i in result["anomalies"]]

    return {
        "analysis": result,
        "input_fingerprint": input_fp,
        "output_fingerprint": output_fp,
        "timestamp": timestamp,
        "engine": ENGINE
    }

@app.post("/analyze/batch")
async def analyze_batch(request: BatchAnalyzeRequest):
    """Analyze multiple datasets in a single request."""
    results = {}
    timestamp = int(time.time())

    for name, data in request.datasets.items():
        if len(data) < 2:
            results[name] = {"error": "Insufficient data points"}
            continue

        input_fp = fingerprint(data)
        analysis = thia_analyze(data, request.method, request.threshold)
        output_fp = fingerprint(f"{analysis}{timestamp}")

        results[name] = {
            "analysis": analysis,
            "input_fingerprint": input_fp,
            "output_fingerprint": output_fp
        }

    return {
        "results": results,
        "datasets_processed": len(request.datasets),
        "timestamp": timestamp,
        "engine": ENGINE
    }

@app.post("/compile")
async def compile_intent(request: CompileRequest):
    """Compile natural language intent into AI Studio prompt."""
    intent = request.intent.strip()
    if not intent:
        raise HTTPException(status_code=400, detail="Intent required")

    if len(intent) < 10:
        raise HTTPException(status_code=400, detail="Intent too short (min 10 chars)")

    # Run the compiler
    result = rosetta_compile(
        intent=intent,
        target_platform=request.target_platform,
        ios_version=request.ios_version
    )

    # Generate fingerprints
    timestamp = int(time.time())
    input_fp = fingerprint(intent)
    output_fp = fingerprint(f"{result['prompt']}{timestamp}") if result["prompt"] else None

    return {
        "compiled": result["verified"],
        "intent": intent,
        "parsed": result["parsed"],
        "constraints": {
            "content": result["content_constraints"],
            "app_development": result["app_constraints"]
        },
        "prompt": result["prompt"],
        "input_fingerprint": input_fp,
        "output_fingerprint": output_fp,
        "timestamp": timestamp,
        "engine": ENGINE
    }

@app.get("/frameworks")
async def get_frameworks():
    """List available Apple frameworks by category."""
    return {
        "frameworks": APPLE_FRAMEWORKS,
        "platforms": ["ios", "ipados", "macos", "watchos", "visionos", "tvos"]
    }

# ═══════════════════════════════════════════════════════════════════════════
# CARTRIDGE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/cartridge/visual")
async def cartridge_visual(request: VisualCartridgeRequest):
    """Generate SVG specification with dimension constraints."""
    if not request.intent or len(request.intent.strip()) < 5:
        raise HTTPException(status_code=400, detail="Intent required (min 5 chars)")

    result = visual_cartridge_compile(request.dict())

    timestamp = int(time.time())
    fp = fingerprint(f"{request.intent}{timestamp}")

    # Log to ledger
    ledger_append("cartridge_visual", {"intent": request.intent[:100], "verified": result["verified"]})

    return {
        **result,
        "cartridge": "visual",
        "fingerprint": fp,
        "timestamp": timestamp,
        "engine": ENGINE
    }

@app.post("/cartridge/sound")
async def cartridge_sound(request: SoundCartridgeRequest):
    """Generate audio specification with frequency/duration limits."""
    if not request.intent or len(request.intent.strip()) < 5:
        raise HTTPException(status_code=400, detail="Intent required (min 5 chars)")

    result = sound_cartridge_compile(request.dict())

    timestamp = int(time.time())
    fp = fingerprint(f"{request.intent}{timestamp}")

    # Log to ledger
    ledger_append("cartridge_sound", {"intent": request.intent[:100], "verified": result["verified"]})

    return {
        **result,
        "cartridge": "sound",
        "fingerprint": fp,
        "timestamp": timestamp,
        "engine": ENGINE
    }

@app.post("/cartridge/sequence")
async def cartridge_sequence(request: SequenceCartridgeRequest):
    """Generate video/animation specification with frame constraints."""
    if not request.intent or len(request.intent.strip()) < 5:
        raise HTTPException(status_code=400, detail="Intent required (min 5 chars)")

    result = sequence_cartridge_compile(request.dict())

    timestamp = int(time.time())
    fp = fingerprint(f"{request.intent}{timestamp}")

    # Log to ledger
    ledger_append("cartridge_sequence", {"intent": request.intent[:100], "verified": result["verified"]})

    return {
        **result,
        "cartridge": "sequence",
        "fingerprint": fp,
        "timestamp": timestamp,
        "engine": ENGINE
    }

@app.post("/cartridge/data")
async def cartridge_data(request: DataCartridgeRequest):
    """Generate report specification with statistical bounds."""
    if not request.intent or len(request.intent.strip()) < 5:
        raise HTTPException(status_code=400, detail="Intent required (min 5 chars)")

    result = data_cartridge_compile(request.dict())

    timestamp = int(time.time())
    fp = fingerprint(f"{request.intent}{timestamp}")

    # Log to ledger
    ledger_append("cartridge_data", {"intent": request.intent[:100], "verified": result["verified"]})

    return {
        **result,
        "cartridge": "data",
        "fingerprint": fp,
        "timestamp": timestamp,
        "engine": ENGINE
    }

# ═══════════════════════════════════════════════════════════════════════════
# LEDGER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/ledger")
async def get_ledger(limit: int = 100, offset: int = 0):
    """Return append-only audit trail."""
    chain_status = ledger_verify_chain()

    total = len(LEDGER)
    entries = LEDGER[offset:offset + limit]

    return {
        "entries": entries,
        "total": total,
        "offset": offset,
        "limit": limit,
        "chain": chain_status,
        "engine": ENGINE
    }

@app.get("/ledger/verify")
async def verify_ledger():
    """Verify integrity of ledger chain."""
    return ledger_verify_chain()

# ═══════════════════════════════════════════════════════════════════════════
# SIGNATURE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/sign")
async def sign(request: SignRequest):
    """Generate cryptographic signature for payload."""
    if not request.payload or len(request.payload.strip()) < 1:
        raise HTTPException(status_code=400, detail="Payload required")

    result = sign_payload(request.payload, request.context)

    # Log to ledger
    ledger_append("signature", {"payload_hash": result["payload_hash"], "token": result["token"]})

    return {
        **result,
        "engine": ENGINE
    }

# ═══════════════════════════════════════════════════════════════════════════
# FRAMEWORK CONSTRAINT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/frameworks/constraints")
async def get_framework_constraints():
    """List framework-specific constraints."""
    return {
        "frameworks": list(FRAMEWORK_CONSTRAINTS.keys()),
        "details": {k: v["name"] for k, v in FRAMEWORK_CONSTRAINTS.items()}
    }

@app.post("/frameworks/verify")
async def verify_framework(intent: str, framework: str):
    """Verify intent against framework-specific constraints."""
    if not intent or len(intent.strip()) < 5:
        raise HTTPException(status_code=400, detail="Intent required (min 5 chars)")

    result = verify_framework_constraints(intent, framework)

    timestamp = int(time.time())
    fp = fingerprint(f"{intent}{framework}{timestamp}")

    # Log to ledger
    ledger_append("framework_verify", {"framework": framework, "passed": result.get("passed", True)})

    return {
        **result,
        "fingerprint": fp,
        "timestamp": timestamp,
        "engine": ENGINE
    }

# ═══════════════════════════════════════════════════════════════════════════
# GROUNDING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/ground")
async def ground_claim(request: GroundRequest):
    """
    Verify a claim against external sources.

    Returns a confidence score and verification status based on
    cross-referencing the query against trusted sources.

    Confidence scores:
    - 0-2: VERIFIED (strong evidence)
    - 2-5: LIKELY (moderate evidence)
    - 5-8: UNCERTAIN (weak evidence)
    - 8-10: UNVERIFIED (no evidence)
    """
    query = request.query.strip()

    if not query or len(query) < 3:
        raise HTTPException(status_code=400, detail="Query required (min 3 characters)")

    # Run verification
    result = grounding_engine.verify_claim(query)

    # Log to ledger
    ledger_append("grounding_check", {
        "query": query,
        "confidence_score": result["confidence_score"],
        "status": result["status"],
        "source_count": len(result["sources"])
    })

    return {
        "query": request.query,
        "result": result,
        "verified": result["status"] == "VERIFIED",
        "engine": ENGINE
    }

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
