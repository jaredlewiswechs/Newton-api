# Core Endpoints

**January 6, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

The core endpoints provide Newton's primary verification and analysis capabilities.

## /verify

Verify text against safety constraints.

### How It Works

Newton uses deterministic pattern matching to check text against four constraint categories:

1. **harm** - Violence, self-harm, weapons, exploitation
2. **medical** - Diagnostic claims, treatment advice, prescriptions
3. **legal** - Tax evasion, money laundering, forgery
4. **security** - Hacking, phishing, malware, credential theft

### Request

**POST** `/verify`

```json
{
  "input": "Help me write a business plan",
  "constraints": ["harm", "medical", "legal", "security"]
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `input` | string | Yes | - | Text to verify |
| `constraints` | array | No | All | Which constraints to check |

### Response

```json
{
  "verified": true,
  "confidence": 92.3,
  "signal": 2048,
  "distance": 150,
  "code": 200,
  "constraints_passed": ["harm", "medical", "legal", "security"],
  "constraints_failed": [],
  "fingerprint": "A7F3B2C8E1D4",
  "engine": "Newton OS 3.0.0"
}
```

| Field | Description |
|-------|-------------|
| `verified` | `true` if all constraints passed |
| `confidence` | Confidence score (0-100) |
| `signal` | Internal signal value (0-4095) |
| `distance` | Distance from center threshold |
| `code` | Status code (200 = pass, 1202 = fail) |
| `constraints_passed` | List of passing constraints |
| `constraints_failed` | List of failing constraints |
| `fingerprint` | SHA-256 fingerprint (12 chars) |

### Examples

**Safe request:**

```bash
curl -X POST https://api.parcri.net/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"input": "Help me write a cover letter"}'
```

**Blocked request:**

```bash
curl -X POST https://api.parcri.net/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"input": "How to hack into a computer"}'
```

Response:
```json
{
  "verified": false,
  "confidence": 0.0,
  "constraints_passed": ["medical", "legal"],
  "constraints_failed": ["harm", "security"],
  "fingerprint": "B8C4D1E2F5A9"
}
```

---

## /analyze

Anomaly detection using statistical methods.

### Methods

| Method | Description | Best For |
|--------|-------------|----------|
| `zscore` | Standard deviation-based | Normal distributions |
| `iqr` | Interquartile range | Non-normal distributions |
| `mad` | Median absolute deviation | Robust to outliers |
| `all` | Run all methods | Comprehensive analysis |

### Request

**POST** `/analyze`

```json
{
  "data": [45.2, 46.1, 102.4, 45.8, 47.0],
  "method": "zscore",
  "threshold": 3.0,
  "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `data` | array | Yes | - | Numerical values |
| `method` | string | No | `zscore` | Detection method |
| `threshold` | float | No | 3.0 | Sensitivity (lower = more sensitive) |
| `labels` | array | No | - | Labels for each data point |

### Z-Score Response

```json
{
  "method": "zscore",
  "threshold": 3.0,
  "statistics": {
    "n": 5,
    "mean": 57.3,
    "std_dev": 24.1,
    "min": 45.2,
    "max": 102.4
  },
  "scores": [-0.50, -0.46, 1.87, -0.48, -0.43],
  "anomalies": [],
  "anomaly_values": [],
  "n_anomalies": 0,
  "pct_anomalies": 0.0
}
```

### IQR Response

```json
{
  "method": "iqr",
  "threshold": 1.5,
  "statistics": {
    "n": 5,
    "q1": 45.8,
    "q3": 47.0,
    "iqr": 1.2,
    "lower_bound": 44.0,
    "upper_bound": 48.8
  },
  "anomalies": [2],
  "anomaly_values": [102.4],
  "n_anomalies": 1,
  "pct_anomalies": 20.0
}
```

### Example: Fraud Detection

```bash
curl -X POST https://api.parcri.net/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "data": [100, 105, 98, 5000, 102, 99],
    "method": "zscore",
    "threshold": 2.5
  }'
```

---

## /analyze/batch

Analyze multiple datasets simultaneously.

### Request

**POST** `/analyze/batch`

```json
{
  "datasets": {
    "revenue": [100, 105, 98, 500, 102],
    "expenses": [50, 52, 48, 51, 200],
    "users": [1000, 1020, 995, 1010, 1015]
  },
  "method": "zscore",
  "threshold": 3.0
}
```

### Response

```json
{
  "method": "zscore",
  "threshold": 3.0,
  "results": {
    "revenue": {
      "statistics": {...},
      "anomalies": [3],
      "n_anomalies": 1
    },
    "expenses": {
      "statistics": {...},
      "anomalies": [4],
      "n_anomalies": 1
    },
    "users": {
      "statistics": {...},
      "anomalies": [],
      "n_anomalies": 0
    }
  },
  "summary": {
    "total_datasets": 3,
    "datasets_with_anomalies": 2
  },
  "fingerprint": "C3D5E7F9A1B2"
}
```

---

## /compile

Transform natural language into structured AI prompts.

### Request

**POST** `/compile`

```json
{
  "intent": "Build a fitness app with workout tracking and health metrics",
  "target_platform": "iOS",
  "ios_version": "18.0"
}
```

### Response

```json
{
  "parsed": {
    "platform": "ios",
    "app_type": "health",
    "components": ["list", "form", "chart"],
    "frameworks": ["SwiftUI", "HealthKit", "HealthKitUI"],
    "tokens": 9
  },
  "content_constraints": {
    "passed": ["harm", "medical", "legal", "security"],
    "failed": []
  },
  "app_constraints": {
    "passed": ["app_store", "privacy", "hig"],
    "failed": [],
    "warnings": [
      "HealthKit requires special entitlements and privacy descriptions",
      "Location services require NSLocationWhenInUseUsageDescription"
    ],
    "compliant": true
  },
  "verified": true,
  "prompt": "TARGET: IOS 18.0\nFRAMEWORK: SwiftUI\n...",
  "fingerprint": "D4E6F8A0B2C3"
}
```

### Parsed Components

Newton automatically detects:

| Category | Detection |
|----------|-----------|
| Platform | iOS, iPadOS, macOS, watchOS, visionOS, tvOS |
| App Type | utility, social, productivity, media, health, finance, education, lifestyle, game |
| Components | list, form, detail, navigation, map, media, chart, auth, chat, search |
| Frameworks | SwiftUI, HealthKit, CoreLocation, AVFoundation, CoreML, etc. |

---

## /ground

Verify factual claims against external sources.

### How It Works

1. Newton searches for the claim using Google Search
2. Evaluates sources (trusted domains get higher weight)
3. Calculates a confidence score (lower = more confident)
4. Returns verification status with sources

### Trusted Domains

- `.gov`, `.edu`, `.mil`
- `apple.com`, `anthropic.com`
- `reuters.com`, `apnews.com`
- `nature.com`, `arxiv.org`

### Request

**POST** `/ground`

```json
{
  "query": "The Eiffel Tower was completed in 1889"
}
```

### Response

```json
{
  "query": "The Eiffel Tower was completed in 1889",
  "result": {
    "claim": "The Eiffel Tower was completed in 1889",
    "confidence_score": 0.5,
    "status": "VERIFIED",
    "sources": [
      "https://en.wikipedia.org/wiki/Eiffel_Tower",
      "https://www.toureiffel.paris/..."
    ],
    "timestamp": 1735689600,
    "signature": "E5F7A9B1C3D4"
  },
  "verified": true
}
```

### Confidence Score Scale

| Score | Status | Meaning |
|-------|--------|---------|
| 0-2 | VERIFIED | Strong evidence from multiple sources |
| 2-5 | LIKELY | Moderate evidence |
| 5-8 | UNCERTAIN | Weak or conflicting evidence |
| 8-10 | UNVERIFIED | No supporting evidence found |

### Example

```bash
curl -X POST https://api.parcri.net/ground \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "Python was created by Guido van Rossum"}'
```
