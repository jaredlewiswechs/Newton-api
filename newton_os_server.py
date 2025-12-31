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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import hashlib
import time
import re
import statistics

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

DW_AXIS = 2048
THRESHOLD = 1024
VERSION = "2.2.0"
ENGINE = f"Newton OS {VERSION}"

# Append-only ledger for audit trail
LEDGER = []
MAX_LEDGER_SIZE = 10000

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

def ledger_append(entry_type: str, payload: dict) -> dict:
    """Append entry to immutable ledger."""
    global LEDGER

    timestamp = int(time.time())
    entry_id = len(LEDGER)

    # Create entry with cryptographic chain
    prev_hash = LEDGER[-1]["hash"] if LEDGER else "GENESIS"

    entry = {
        "id": entry_id,
        "type": entry_type,
        "payload": payload,
        "timestamp": timestamp,
        "prev_hash": prev_hash,
    }

    # Generate hash of this entry
    entry_str = f"{entry_id}{entry_type}{payload}{timestamp}{prev_hash}"
    entry["hash"] = hashlib.sha256(entry_str.encode()).hexdigest()[:16].upper()

    # Append (immutable - never modify existing entries)
    if len(LEDGER) < MAX_LEDGER_SIZE:
        LEDGER.append(entry)
    else:
        # Rotate: remove oldest, keep recent
        LEDGER = LEDGER[1:] + [entry]

    return entry

def ledger_verify_chain() -> dict:
    """Verify integrity of ledger chain."""
    if not LEDGER:
        return {"valid": True, "entries": 0, "message": "Ledger empty"}

    for i, entry in enumerate(LEDGER):
        if i == 0:
            if entry["prev_hash"] != "GENESIS":
                return {"valid": False, "broken_at": i, "message": "Genesis block corrupted"}
        else:
            if entry["prev_hash"] != LEDGER[i-1]["hash"]:
                return {"valid": False, "broken_at": i, "message": "Chain broken"}

    return {"valid": True, "entries": len(LEDGER), "message": "Chain intact"}

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
    <title>Newton OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            min-height: 100vh;
            padding: 48px 24px;
        }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { font-size: 32px; font-weight: 600; margin-bottom: 8px; }
        .tagline { color: #00875a; font-size: 18px; margin-bottom: 8px; }
        .subtitle { color: #666; font-size: 14px; margin-bottom: 48px; }
        .section { margin-bottom: 40px; }
        .section-title {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #222;
        }
        .endpoint {
            background: #111;
            border: 1px solid #222;
            padding: 20px;
            margin-bottom: 12px;
        }
        .method {
            display: inline-block;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 600;
            border-radius: 3px;
            margin-right: 12px;
        }
        .post { background: #00875a; color: #000; }
        .get { background: #2d5a9e; color: #fff; }
        .path { font-family: 'SF Mono', monospace; font-size: 14px; }
        .desc { color: #888; font-size: 13px; margin-top: 8px; }
        pre {
            background: #161616;
            border: 1px solid #222;
            padding: 16px;
            font-family: 'SF Mono', monospace;
            font-size: 12px;
            overflow-x: auto;
            margin-top: 12px;
        }
        .try-section { margin-top: 48px; }
        input, select {
            width: 100%;
            padding: 12px 16px;
            font-size: 14px;
            background: #111;
            border: 1px solid #333;
            color: #e0e0e0;
            font-family: inherit;
            margin-bottom: 12px;
        }
        textarea {
            width: 100%;
            padding: 12px 16px;
            font-size: 13px;
            font-family: 'SF Mono', monospace;
            background: #111;
            border: 1px solid #333;
            color: #e0e0e0;
            min-height: 100px;
            margin-bottom: 12px;
        }
        button {
            background: #00875a;
            color: #000;
            border: none;
            padding: 12px 32px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
        }
        button:hover { background: #00a06a; }
        #result {
            margin-top: 20px;
            padding: 20px;
            background: #111;
            border: 1px solid #222;
            font-family: 'SF Mono', monospace;
            font-size: 12px;
            white-space: pre-wrap;
            display: none;
        }
        footer {
            margin-top: 64px;
            padding-top: 24px;
            border-top: 1px solid #222;
            font-size: 12px;
            color: #444;
        }
        .tabs { display: flex; gap: 0; margin-bottom: 20px; }
        .tab {
            padding: 10px 20px;
            background: #111;
            border: 1px solid #222;
            color: #666;
            cursor: pointer;
            font-size: 13px;
        }
        .tab.active { background: #00875a; color: #000; border-color: #00875a; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Newton OS</h1>
        <p class="tagline">The free verification layer. 1 == 1</p>
        <p class="subtitle">Ada speaks. Tahoe remembers. THIA sees.</p>

        <div class="section">
            <div class="section-title">Capabilities</div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/verify</span>
                <p class="desc">Intent verification with constraint checking</p>
                <pre>{ "input": "text to verify", "constraints": ["harm", "medical", "legal", "security"] }</pre>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/analyze</span>
                <p class="desc">THIA anomaly detection for numerical data</p>
                <pre>{ "data": [45.2, 46.1, 102.4, 45.8], "method": "zscore", "threshold": 3.0 }</pre>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/health</span>
                <p class="desc">System status and engine version</p>
            </div>
        </div>

        <div class="section try-section">
            <div class="section-title">Try It</div>

            <div class="tabs">
                <div class="tab active" onclick="switchTab('verify')">Verify</div>
                <div class="tab" onclick="switchTab('analyze')">Analyze</div>
            </div>

            <div id="verify-form">
                <input type="text" id="verify-input" placeholder="Enter text to verify...">
                <button onclick="runVerify()">Verify</button>
            </div>

            <div id="analyze-form" style="display: none;">
                <textarea id="analyze-input" placeholder="Enter comma-separated numbers...&#10;Example: 45.2, 46.1, 44.8, 102.4, 45.8, 0.0, 65.2">45.2, 46.1, 44.8, 45.5, 45.9, 46.2, 45.1, 44.9, 45.3, 102.4, 45.7, 46.0, 0.0, 45.8, 65.2, 66.1</textarea>
                <select id="analyze-method">
                    <option value="zscore">Z-Score (default)</option>
                    <option value="iqr">IQR</option>
                    <option value="mad">MAD</option>
                    <option value="all">All Methods</option>
                </select>
                <button onclick="runAnalyze()">Analyze</button>
            </div>

            <div id="result"></div>
        </div>

        <footer>
            © 2025 Ada Computing Company · Houston
        </footer>
    </div>

    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('verify-form').style.display = tab === 'verify' ? 'block' : 'none';
            document.getElementById('analyze-form').style.display = tab === 'analyze' ? 'block' : 'none';
            document.getElementById('result').style.display = 'none';
        }

        async function runVerify() {
            const input = document.getElementById('verify-input').value;
            if (!input) return;

            const res = await fetch('/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input })
            });
            const data = await res.json();
            document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            document.getElementById('result').style.display = 'block';
        }

        async function runAnalyze() {
            const input = document.getElementById('analyze-input').value;
            const method = document.getElementById('analyze-method').value;
            if (!input) return;

            const data = input.split(',').map(x => parseFloat(x.trim())).filter(x => !isNaN(x));

            const res = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data, method })
            });
            const result = await res.json();
            document.getElementById('result').textContent = JSON.stringify(result, null, 2);
            document.getElementById('result').style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "engine": ENGINE,
        "capabilities": [
            "verify", "analyze", "compile",
            "cartridge/visual", "cartridge/sound", "cartridge/sequence", "cartridge/data",
            "ledger", "sign",
            "frameworks/verify"
        ],
        "ledger_entries": len(LEDGER),
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
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
