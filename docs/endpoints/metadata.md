# Metadata Endpoints

**January 3, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Metadata endpoints provide system information and available options.

## /health

Check system status and version.

### Request

**GET** `/health`

### Response

```json
{
  "status": "ok",
  "version": "3.0.0",
  "engine": "Newton OS 3.0.0",
  "timestamp": 1735689600,
  "auth_enabled": true,
  "ledger_entries": 1247
}
```

| Field | Description |
|-------|-------------|
| `status` | `ok` or `error` |
| `version` | Newton OS version |
| `engine` | Full engine identifier |
| `timestamp` | Current Unix timestamp |
| `auth_enabled` | Whether authentication is required |
| `ledger_entries` | Number of entries in audit ledger |

### Example

```bash
curl https://api.parcri.net/health
```

### Use Cases

- Health checks for load balancers
- Version verification
- Uptime monitoring

---

## /constraints

List available content constraints.

### Request

**GET** `/constraints`

### Response

```json
{
  "constraints": {
    "harm": {
      "name": "No Harm",
      "description": "Blocks violence, self-harm, weapons, exploitation",
      "patterns": 4
    },
    "medical": {
      "name": "Medical Bounds",
      "description": "Blocks diagnostic claims, treatment advice, prescriptions",
      "patterns": 3
    },
    "legal": {
      "name": "Legal Bounds",
      "description": "Blocks tax evasion, money laundering, forgery",
      "patterns": 3
    },
    "security": {
      "name": "Security",
      "description": "Blocks hacking, phishing, malware, credential theft",
      "patterns": 2
    }
  },
  "total": 4
}
```

### Constraint Details

#### harm

Patterns that block:
- Weapon/bomb creation instructions
- Violence and murder planning
- Self-harm encouragement
- Exploitation

#### medical

Patterns that block:
- Medication/dosage advice
- Diagnosis requests
- Prescription requests

#### legal

Patterns that block:
- Tax evasion guidance
- Money laundering instructions
- Forgery/counterfeiting

#### security

Patterns that block:
- Hacking/cracking tutorials
- Password theft
- Phishing/malware creation

### Example

```bash
curl https://api.parcri.net/constraints
```

---

## /methods

List available anomaly detection methods.

### Request

**GET** `/methods`

### Response

```json
{
  "methods": {
    "zscore": {
      "name": "Z-Score",
      "default_threshold": 3.0,
      "min_data_points": 2,
      "description": "Standard deviation-based anomaly detection. Best for normally distributed data."
    },
    "iqr": {
      "name": "Interquartile Range",
      "default_threshold": 1.5,
      "min_data_points": 4,
      "description": "Quartile-based outlier detection. Best for non-normal distributions."
    },
    "mad": {
      "name": "Median Absolute Deviation",
      "default_threshold": 3.0,
      "min_data_points": 2,
      "description": "Robust median-based detection. Best when data contains extreme outliers."
    },
    "all": {
      "name": "All Methods",
      "description": "Run all detection methods and compare results."
    }
  },
  "total": 4
}
```

### Method Comparison

| Method | Best For | Threshold Meaning |
|--------|----------|-------------------|
| Z-score | Normal distributions | Standard deviations from mean |
| IQR | Skewed distributions | IQR multiplier for bounds |
| MAD | Robust detection | MAD multiplier from median |

### Choosing a Method

1. **Z-score**: Use when data is roughly normally distributed
2. **IQR**: Use when data is skewed or has a non-normal distribution
3. **MAD**: Use when you need robustness to extreme outliers
4. **all**: Use when you want comprehensive analysis

### Example

```bash
curl https://api.parcri.net/methods
```

---

## /frameworks

List available frameworks for verification.

### Request

**GET** `/frameworks`

### Response

```json
{
  "frameworks": {
    "apple": {
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
      "auth": ["AuthenticationServices", "LocalAuthentication"]
    },
    "web": ["react", "nodejs", "django", "flask"],
    "ml": ["tensorflow", "pytorch"]
  }
}
```

### Example

```bash
curl https://api.parcri.net/frameworks
```

---

## /frameworks/constraints

List framework-specific constraints.

### Request

**GET** `/frameworks/constraints`

### Response

```json
{
  "framework_constraints": {
    "healthkit": {
      "name": "HealthKit Medical Constraints",
      "patterns": 3,
      "warnings": [
        "HealthKit data is sensitive - implement proper encryption",
        "Medical apps may require FDA approval",
        "Always include medical disclaimer"
      ]
    },
    "swiftui": {
      "name": "SwiftUI Accessibility Constraints",
      "patterns": 3,
      "required_features": [
        "Dynamic Type support",
        "VoiceOver labels",
        "Semantic colors"
      ]
    },
    "react": {
      "name": "React Security & Accessibility",
      "patterns": 3,
      "security_requirements": [
        "Sanitize all user inputs before rendering",
        "Use Content Security Policy headers",
        "Avoid dangerouslySetInnerHTML with untrusted content"
      ]
    },
    "pytorch": {
      "name": "PyTorch ML Safety Constraints",
      "patterns": 4,
      "security_requirements": [
        "Never load untrusted pickle files",
        "Use weights_only=True for torch.load",
        "Validate model checksums"
      ]
    }
  }
}
```

### Example

```bash
curl https://api.parcri.net/frameworks/constraints
```
