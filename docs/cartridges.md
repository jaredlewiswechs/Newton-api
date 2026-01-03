# Newton Cartridges

**January 3, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Newton's constraint engine extends to any domain with definable bounds through Cartridges. Generate verified specifications for media content—all constraint-checked before generation.

## Overview

| Cartridge | Input | Output | Use Case |
|-----------|-------|--------|----------|
| Visual | Design intent | SVG specification | UI components, diagrams, logos |
| Sound | Audio intent | Audio specification | Sound effects, music, ambient |
| Sequence | Animation intent | Video specification | Animations, videos, slideshows |
| Data | Report intent | Report specification | Reports, analytics, dashboards |
| Rosetta | App intent | Code generation prompt | iOS, macOS, web apps |
| Document Vision | Expense document | Structured expense data | Receipts, invoices, bills |
| Auto | Any intent | Auto-detected specification | Automatic type detection |

All cartridges verify content against both standard safety constraints and domain-specific rules.

---

## Quick Start

```bash
# Visual cartridge - generate SVG spec
curl -X POST http://localhost:8000/cartridge/visual \
  -H "Content-Type: application/json" \
  -d '{"intent": "Create a modern logo with circles and text"}'

# Rosetta compiler - generate code prompt
curl -X POST http://localhost:8000/cartridge/rosetta \
  -H "Content-Type: application/json" \
  -d '{"intent": "Build an iOS fitness app with HealthKit"}'

# Auto-detect cartridge type
curl -X POST http://localhost:8000/cartridge/auto \
  -H "Content-Type: application/json" \
  -d '{"intent": "Create an image with geometric shapes"}'

# Get cartridge info
curl http://localhost:8000/cartridge/info
```

---

## /cartridge/visual

Generate SVG specifications with dimension constraints.

### Request

**POST** `/cartridge/visual`

```json
{
  "intent": "Create a dashboard with progress indicators",
  "width": 800,
  "height": 600,
  "max_elements": 100,
  "color_palette": ["#3b82f6", "#10b981", "#f59e0b"]
}
```

| Field | Type | Required | Default | Max | Description |
|-------|------|----------|---------|-----|-------------|
| `intent` | string | Yes | - | - | Design description |
| `width` | int | No | 800 | 4096 | Canvas width in pixels |
| `height` | int | No | 600 | 4096 | Canvas height in pixels |
| `max_elements` | int | No | 100 | 1000 | Maximum SVG elements |
| `color_palette` | array | No | - | 256 | Color hex codes |

### Response

```json
{
  "verified": true,
  "constraints": {
    "content": {
      "passed": ["harm", "medical", "legal", "security"],
      "failed": []
    },
    "visual": {
      "passed": true,
      "violations": []
    },
    "bounds": {
      "width": 800,
      "height": 600,
      "max_elements": 100
    }
  },
  "spec": {
    "type": "svg",
    "viewBox": "0 0 800 600",
    "width": 800,
    "height": 600,
    "elements": ["rect", "text", "circle"],
    "style": {
      "background": "#ffffff",
      "stroke": "#000000",
      "fill": "#e0e0e0"
    }
  }
}
```

### Visual Constraints

| Constraint | Limit |
|------------|-------|
| Width | 1 - 4096 px |
| Height | 1 - 4096 px |
| Max elements | 1000 |
| Color palette | 256 colors |

### Blocked Patterns

- Offensive/inappropriate imagery
- Logo/trademark plagiarism

### Example

```bash
curl -X POST https://api.parcri.net/cartridge/visual \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "intent": "Create a bar chart showing monthly sales",
    "width": 600,
    "height": 400
  }'
```

---

## /cartridge/sound

Generate audio specifications with frequency and duration limits.

### Request

**POST** `/cartridge/sound`

```json
{
  "intent": "Create a notification chime",
  "duration_ms": 500,
  "min_frequency": 440.0,
  "max_frequency": 880.0,
  "sample_rate": 44100
}
```

| Field | Type | Required | Default | Limits | Description |
|-------|------|----------|---------|--------|-------------|
| `intent` | string | Yes | - | - | Audio description |
| `duration_ms` | int | No | 5000 | 1-300000 | Duration in milliseconds |
| `min_frequency` | float | No | 20.0 | 1+ | Minimum frequency (Hz) |
| `max_frequency` | float | No | 20000.0 | 22050 max | Maximum frequency (Hz) |
| `sample_rate` | int | No | 44100 | 22050, 44100, 48000, 96000 | Sample rate |

### Response

```json
{
  "verified": true,
  "constraints": {
    "content": {
      "passed": ["harm", "medical", "legal", "security"],
      "failed": []
    },
    "sound": {
      "passed": true,
      "violations": []
    },
    "bounds": {
      "duration_ms": 500,
      "frequency_range": [440.0, 880.0]
    }
  },
  "spec": {
    "type": "audio",
    "duration_ms": 500,
    "sample_rate": 44100,
    "frequency_range": {
      "min": 440.0,
      "max": 880.0
    },
    "characteristics": ["tone"],
    "format": "wav",
    "channels": 2
  }
}
```

### Sound Constraints

| Constraint | Limit |
|------------|-------|
| Duration | 1ms - 5 minutes |
| Frequency | 1 - 22050 Hz |
| Sample rates | 22050, 44100, 48000, 96000 |

### Blocked Patterns

- Subliminal messages
- Harmful frequencies

### Example

```bash
curl -X POST https://api.parcri.net/cartridge/sound \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "intent": "Create ambient background music",
    "duration_ms": 30000,
    "sample_rate": 48000
  }'
```

---

## /cartridge/sequence

Generate video/animation specifications with frame constraints.

### Request

**POST** `/cartridge/sequence`

```json
{
  "intent": "Create a product demo animation",
  "duration_seconds": 15.0,
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "max_scenes": 5
}
```

| Field | Type | Required | Default | Limits | Description |
|-------|------|----------|---------|--------|-------------|
| `intent` | string | Yes | - | - | Animation description |
| `duration_seconds` | float | No | 30.0 | 0.1-600 | Duration in seconds |
| `fps` | int | No | 30 | 1-120 | Frames per second |
| `width` | int | No | 1920 | 7680 max | Resolution width |
| `height` | int | No | 1080 | 4320 max | Resolution height |
| `max_scenes` | int | No | 10 | 50 | Maximum scene count |

### Response

```json
{
  "verified": true,
  "constraints": {
    "content": {
      "passed": ["harm", "medical", "legal", "security"],
      "failed": []
    },
    "sequence": {
      "passed": true,
      "violations": []
    },
    "bounds": {
      "duration": 15.0,
      "fps": 30,
      "resolution": "1920x1080"
    }
  },
  "spec": {
    "type": "animation",
    "duration_seconds": 15.0,
    "fps": 30,
    "total_frames": 450,
    "resolution": {
      "width": 1920,
      "height": 1080
    },
    "max_scenes": 5,
    "format": "mp4",
    "codec": "h264"
  }
}
```

### Sequence Constraints

| Constraint | Limit |
|------------|-------|
| Duration | 0.1s - 10 minutes |
| FPS | 1 - 120 |
| Resolution | Up to 8K (7680x4320) |
| Scenes | 50 max |

### Blocked Patterns

- Seizure/epilepsy-inducing content
- Rapid strobing/flashing

### Example

```bash
curl -X POST https://api.parcri.net/cartridge/sequence \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "intent": "Create a slideshow presentation",
    "duration_seconds": 60,
    "fps": 24,
    "max_scenes": 10
  }'
```

---

## /cartridge/data

Generate report specifications with statistical bounds.

### Request

**POST** `/cartridge/data`

```json
{
  "intent": "Generate a financial summary report",
  "data": {
    "revenue": [100000, 120000, 115000, 130000],
    "expenses": [80000, 85000, 82000, 90000]
  },
  "format": "json",
  "max_rows": 1000,
  "include_statistics": true
}
```

| Field | Type | Required | Default | Limits | Description |
|-------|------|----------|---------|--------|-------------|
| `intent` | string | Yes | - | - | Report description |
| `data` | object | No | - | - | Data to include |
| `format` | string | No | `json` | json, csv, markdown, html | Output format |
| `max_rows` | int | No | 1000 | 100000 | Maximum row count |
| `include_statistics` | bool | No | true | - | Include statistical analysis |

### Response

```json
{
  "verified": true,
  "constraints": {
    "content": {
      "passed": ["harm", "medical", "legal", "security"],
      "failed": []
    },
    "data": {
      "passed": true,
      "violations": []
    },
    "bounds": {
      "max_rows": 1000,
      "format": "json"
    }
  },
  "spec": {
    "type": "report",
    "report_type": "financial",
    "format": "json",
    "max_rows": 1000,
    "include_statistics": true,
    "sections": ["header", "summary", "data", "footer"],
    "data_provided": true,
    "statistics": {
      "count": 8,
      "sum": 802000,
      "mean": 100250,
      "min": 80000,
      "max": 130000
    }
  }
}
```

### Report Types

Automatically detected from intent:

| Type | Keywords |
|------|----------|
| financial | financial, revenue, profit, expense, budget |
| analytics | analytics, metrics, kpi, performance |
| summary | summary, overview, report, digest |
| comparison | comparison, compare, versus, vs |
| trend | trend, growth, change, over time |

### Data Constraints

| Constraint | Limit |
|------------|-------|
| Rows | 100,000 max |
| Columns | 1,000 max |
| Formats | json, csv, markdown, html |

### Blocked Patterns

- Data fabrication/falsification
- Metric manipulation

### Example

```bash
curl -X POST https://api.parcri.net/cartridge/data \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "intent": "Create a user analytics report",
    "data": {"users": [1000, 1500, 2000], "sessions": [5000, 7500, 10000]},
    "format": "markdown",
    "include_statistics": true
  }'
```

---

## /cartridge/rosetta

Generate verified code generation prompts for apps.

### Request

**POST** `/cartridge/rosetta`

```json
{
  "intent": "Build an iOS fitness app with HealthKit integration",
  "target_platform": "ios",
  "version": "18.0",
  "language": "swift"
}
```

| Field | Type | Required | Default | Options | Description |
|-------|------|----------|---------|---------|-------------|
| `intent` | string | Yes | - | - | App description |
| `target_platform` | string | No | `ios` | ios, ipados, macos, watchos, visionos, tvos, web, android | Target platform |
| `version` | string | No | `18.0` | - | Platform version |
| `language` | string | No | `swift` | swift, python, typescript | Output language |

### Response

```json
{
  "verified": true,
  "cartridge_type": "rosetta",
  "constraints": {
    "safety": {
      "passed": true,
      "violations": []
    },
    "security": {
      "passed": true,
      "violations": []
    },
    "app_store": {
      "passed": true,
      "violations": []
    }
  },
  "spec": {
    "type": "code_prompt",
    "format": "swift_prompt",
    "platform": "ios",
    "version": "18.0",
    "language": "swift",
    "parsed": {
      "platform": "ios",
      "app_type": "health",
      "components": ["list", "detail", "chart"],
      "frameworks": ["SwiftUI", "HealthKit", "HealthKitUI"]
    },
    "prompt": "TARGET: IOS 18.0\nFRAMEWORK: SwiftUI\n...",
    "frameworks": ["SwiftUI", "HealthKit", "HealthKitUI"],
    "warnings": [
      "HealthKit requires special entitlements and privacy descriptions"
    ]
  },
  "fingerprint": "A7F3B2C8E1D4",
  "elapsed_us": 142,
  "timestamp": 1735689600000,
  "engine": "Newton Supercomputer 1.0.0"
}
```

### Detected Frameworks

Rosetta automatically detects required frameworks from intent:

| Category | Keywords | Frameworks |
|----------|----------|------------|
| Health | health, fitness, workout, steps | HealthKit, HealthKitUI |
| Location | map, location, gps, directions | CoreLocation, MapKit |
| Media | photo, video, camera, music | AVFoundation, PhotosUI, MusicKit |
| ML | ml, ai, recognize, detect, classify | CoreML, Vision, NaturalLanguage |
| AR | ar, augmented, 3d, spatial | ARKit, RealityKit |
| Payments | payment, purchase, subscription | StoreKit, PassKit |
| Auth | login, auth, face id, touch id | AuthenticationServices, LocalAuthentication |
| Data | save, store, sync, cloud | CoreData, SwiftData, CloudKit |

### App Types

Automatically detected from intent:

| Type | Keywords |
|------|----------|
| utility | utility, tool, calculator, converter |
| social | social, community, share, friends |
| productivity | productivity, task, todo, notes |
| media | photo, video, music, podcast |
| health | health, fitness, wellness, meditation |
| finance | finance, budget, expense, investment |
| education | education, learn, study, course |
| lifestyle | lifestyle, recipe, travel, weather |
| game | game, play, puzzle, arcade |

### Security Constraints

Rosetta blocks:
- Malware, virus, trojan, backdoor patterns
- Data exfiltration intent
- Security bypass intent
- Keylogger/spyware without consent

### App Store Constraints

Rosetta blocks:
- Real-money gambling/casino
- Cryptocurrency mining
- Adult/explicit content

### Example

```bash
curl -X POST https://api.parcri.net/cartridge/rosetta \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "intent": "Create a meditation app with timer and ambient sounds",
    "target_platform": "ios",
    "language": "swift"
  }'
```

---

## /cartridge/document-vision

Process expense documents (receipts, invoices, bills) with AI vision and verified extraction.

### Request

**POST** `/cartridge/document-vision`

```json
{
  "intent": "Process restaurant receipt from business lunch",
  "document_data": {
    "total": 87.50,
    "line_items": [
      {"description": "Lunch entree", "quantity": 2, "unit_price": 28.00, "total": 56.00},
      {"description": "Beverages", "quantity": 2, "unit_price": 8.00, "total": 16.00},
      {"description": "Dessert", "quantity": 1, "unit_price": 12.00, "total": 12.00}
    ],
    "tax": 3.50
  },
  "document_type": "receipt",
  "currency": "USD",
  "max_line_items": 100,
  "expense_policy": {
    "max_meal": 150.00,
    "require_itemization_above": 75.00
  }
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `intent` | string | Yes | - | Description of document or extraction goal |
| `document_data` | object | No | - | Pre-extracted OCR/vision data to validate |
| `document_type` | string | No | `auto` | receipt, invoice, expense_report, bill, statement |
| `currency` | string | No | `USD` | ISO 4217 currency code |
| `max_line_items` | int | No | 100 | Maximum line items (max 500) |
| `expense_policy` | object | No | - | Company expense policy constraints |

### Response

```json
{
  "verified": true,
  "cartridge_type": "document_vision",
  "constraints": {
    "safety": {
      "passed": true,
      "violations": []
    },
    "expense_fraud": {
      "passed": true,
      "violations": []
    },
    "bounds": {
      "max_line_items": 100,
      "currency": "USD",
      "document_type": "receipt"
    }
  },
  "spec": {
    "type": "expense_extraction",
    "format": "receipt_data",
    "document_type": "receipt",
    "currency": "USD",
    "vendor": {
      "type": "restaurant",
      "name": null,
      "address": null,
      "confidence": 0.0
    },
    "category": "meals",
    "max_line_items": 100,
    "extraction_fields": {
      "required": ["date", "total", "subtotal", "tax", "currency", "payment_method"],
      "optional": ["vendor_name", "vendor_address", "line_items", "tip", "change"],
      "computed": ["tax_rate", "total_verified", "category"]
    },
    "validation_rules": {
      "require_date": true,
      "require_total": true,
      "require_vendor": true,
      "max_age_days": 90,
      "duplicate_check": true
    },
    "extracted_data": {
      "raw": { ... },
      "validated": {},
      "line_items": [
        {"description": "Lunch entree", "quantity": 2, "unit_price": 28.00, "total": 56.00, "confidence": 1.0},
        {"description": "Beverages", "quantity": 2, "unit_price": 8.00, "total": 16.00, "confidence": 1.0},
        {"description": "Dessert", "quantity": 1, "unit_price": 12.00, "total": 12.00, "confidence": 1.0}
      ],
      "totals": {"total": 87.50},
      "flags": []
    },
    "warnings": [],
    "expense_categories": ["travel", "meals", "lodging", "transportation", "supplies", "equipment", "software", "services", "utilities", "communication", "entertainment", "medical", "insurance", "taxes", "fees", "other"]
  },
  "fingerprint": "B4C7E2A1F8D9",
  "elapsed_us": 89,
  "timestamp": 1735689600000
}
```

### Document Types

| Type | Description | Auto-Detection Keywords |
|------|-------------|------------------------|
| receipt | Point-of-sale receipts | receipt, purchase, transaction, sale |
| invoice | Business invoices | invoice, bill, balance due, account |
| expense_report | Expense claim forms | expense report, reimbursement, claim |
| bill | Utility/service bills | bill, utility, payment due, amount due |
| statement | Account statements | statement, account, summary, period |

### Expense Categories

Automatically detected based on vendor type:

| Vendor Type | Category |
|-------------|----------|
| Restaurant/Cafe | meals |
| Hotel/Resort | lodging |
| Airline | travel |
| Uber/Lyft/Taxi | transportation |
| Retail Store | supplies |
| Gas Station | transportation |
| Office Supply | supplies |
| Technology/Software | software |
| Subscription | services |

### Supported Currencies

USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR, MXN, BRL, KRW, SGD, HKD, NOK, SEK, DKK, NZD, ZAR, RUB

### Fraud Detection

The Document Vision cartridge detects and blocks:

| Pattern | Description |
|---------|-------------|
| Receipt fabrication | Forged, fake, or fabricated receipts |
| Amount inflation | Inflated, padded, or exaggerated expenses |
| Duplicate claims | Duplicate submissions or double-billing |
| Personal expenses | Personal purchases claimed as business |

### Financial Limits

| Constraint | Default |
|------------|---------|
| Single transaction alert | $100,000 |
| Daily total alert | $500,000 |
| Maximum document size | 50 MB |
| Maximum line items | 500 |

### Expense Policy Integration

Pass custom expense policies to enforce company rules:

```json
{
  "expense_policy": {
    "max_meal": 100.00,
    "max_lodging": 300.00,
    "require_itemization_above": 50.00,
    "max_age_days": 60
  }
}
```

### Example

```bash
# Process a receipt with expense policy validation
curl -X POST https://api.parcri.net/cartridge/document-vision \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "intent": "Scan hotel invoice from business trip to Austin",
    "document_type": "invoice",
    "currency": "USD",
    "expense_policy": {
      "max_lodging": 250.00
    }
  }'
```

---

## /cartridge/auto

Automatically detect cartridge type and compile.

### Request

**POST** `/cartridge/auto`

```json
{
  "intent": "Create a colorful logo with geometric shapes"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `intent` | string | Yes | Natural language description |

### Response

Returns the same response format as the detected cartridge type, with an additional `cartridge_type` field indicating which cartridge was used.

### Detection Patterns

| Cartridge | Trigger Keywords |
|-----------|------------------|
| Visual | image, picture, graphic, svg, visual, icon, logo, illustration |
| Sound | sound, audio, music, tone, melody, beep, voice, sfx |
| Sequence | video, animation, movie, clip, slideshow, motion |
| Rosetta | app, application, code, build, create, develop, program |
| Data | report, data, analytics, statistics, chart, graph, table |

### Example

```bash
# This will auto-detect as Visual
curl -X POST https://api.parcri.net/cartridge/auto \
  -H "Content-Type: application/json" \
  -d '{"intent": "Design a minimalist icon"}'

# This will auto-detect as Rosetta
curl -X POST https://api.parcri.net/cartridge/auto \
  -H "Content-Type: application/json" \
  -d '{"intent": "Build a weather app for iPhone"}'

# This will auto-detect as Sound
curl -X POST https://api.parcri.net/cartridge/auto \
  -H "Content-Type: application/json" \
  -d '{"intent": "Create a notification chime"}'
```

---

## /cartridge/info

Get information about available cartridges.

### Request

**GET** `/cartridge/info`

### Response

```json
{
  "cartridges": [
    {
      "name": "visual",
      "endpoint": "/cartridge/visual",
      "description": "Generate SVG/image specifications",
      "constraints": {
        "max_width": 4096,
        "max_height": 4096,
        "max_elements": 1000,
        "max_colors": 256
      }
    },
    {
      "name": "sound",
      "endpoint": "/cartridge/sound",
      "description": "Generate audio specifications",
      "constraints": {
        "max_duration_ms": 300000,
        "frequency_range": "1-22050 Hz",
        "sample_rates": [22050, 44100, 48000, 96000]
      }
    },
    {
      "name": "sequence",
      "endpoint": "/cartridge/sequence",
      "description": "Generate video/animation specifications",
      "constraints": {
        "max_duration_seconds": 600,
        "fps_range": "1-120",
        "max_resolution": "7680x4320 (8K)"
      }
    },
    {
      "name": "data",
      "endpoint": "/cartridge/data",
      "description": "Generate report specifications",
      "constraints": {
        "max_rows": 100000,
        "formats": ["json", "csv", "markdown", "html"]
      }
    },
    {
      "name": "rosetta",
      "endpoint": "/cartridge/rosetta",
      "description": "Generate code generation prompts",
      "constraints": {
        "platforms": ["ios", "ipados", "macos", "watchos", "visionos", "tvos", "web", "android"],
        "languages": ["swift", "python", "typescript"]
      }
    },
    {
      "name": "document_vision",
      "endpoint": "/cartridge/document-vision",
      "description": "Process expense documents with AI vision",
      "constraints": {
        "document_types": ["receipt", "invoice", "expense_report", "bill", "statement"],
        "max_line_items": 500,
        "currencies": ["USD", "EUR", "GBP", "JPY", "..."],
        "max_document_size_mb": 50
      }
    },
    {
      "name": "auto",
      "endpoint": "/cartridge/auto",
      "description": "Auto-detect cartridge type and compile",
      "constraints": {}
    }
  ],
  "engine": "Newton Supercomputer 1.0.0"
}
```

---

## Safety Constraints

All cartridges verify content against these safety patterns before generation:

| Category | Detects |
|----------|---------|
| **Harm** | Violence, weapons, self-harm instructions |
| **Medical** | Unverified medical advice, drug dosages |
| **Legal** | Tax evasion, money laundering, counterfeiting |
| **Security** | Hacking, phishing, malware |

If any safety constraint fails, the cartridge returns `verified: false` with the violations listed.

---

## Ledger Integration

All cartridge operations are recorded in the immutable ledger:

```json
{
  "operation": "cartridge_visual",
  "payload": {
    "intent_hash": "A7F3B2C8E1D4F5A9"
  },
  "result": "pass",
  "metadata": {
    "elapsed_us": 142
  }
}
```

This provides a complete audit trail of all media specification generation.

---

© 2025-2026 Ada Computing Company · Houston, Texas
