# Framework Verification

**January 6, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Newton v3.0 includes safety constraints for 10+ frameworks across Apple, Web, and ML ecosystems.

## Overview

Framework verification checks AI-generated code against framework-specific security and safety patterns.

### Supported Categories

| Category | Frameworks |
|----------|------------|
| Apple | HealthKit, SwiftUI, ARKit, CoreML |
| Web | React, Node.js, Django, Flask |
| ML/AI | TensorFlow, PyTorch |

---

## /frameworks/verify

Verify intent against framework-specific constraints.

### Request

**POST** `/frameworks/verify?intent=YOUR_INTENT&framework=FRAMEWORK`

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `intent` | string | Yes | The intent to verify |
| `framework` | string | Yes | Target framework |

### Response

```json
{
  "framework": "pytorch",
  "found": true,
  "name": "PyTorch ML Safety Constraints",
  "passed": true,
  "violations": [],
  "warnings": [
    "torch.load can execute arbitrary code - only load trusted models",
    "ML models can perpetuate biases in training data",
    "Monitor for adversarial inputs in production"
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
  }
}
```

### Example

```bash
curl -X POST "https://api.parcri.net/frameworks/verify?intent=Build+an+app+with+torch.load&framework=pytorch" \
  -H "X-API-Key: your-api-key"
```

---

## Apple Frameworks

### HealthKit

Medical and health data constraints.

**Patterns Blocked:**
- Diagnosing diseases without professional oversight
- Replacing medical professionals
- Medical advice without disclaimers

**Requirements:**
- Entitlement: `com.apple.developer.healthkit`
- Privacy descriptions required
- Medical disclaimer mandatory

**Warnings:**
- HealthKit data requires encryption
- Medical apps may need FDA approval
- Always include medical disclaimers

### SwiftUI

Accessibility constraints for UI.

**Patterns Blocked:**
- Ignoring accessibility/VoiceOver
- Fixed small text sizes
- Color-only indicators

**Required Features:**
- Dynamic Type support
- VoiceOver labels
- Semantic colors

**Warnings:**
- All interactive elements need accessibility labels
- Support Dynamic Type for text sizing
- Don't rely on color alone for information

### ARKit

Augmented reality safety constraints.

**Patterns Blocked:**
- Obscuring real-world view
- Full screen immersion without exit
- Extreme/disorienting motion

**Safety Requirements:**
- Clear exit mechanism
- Physical movement warnings
- Boundary detection

**Warnings:**
- Users must maintain awareness of surroundings
- Avoid rapid camera movements (motion sickness)
- Provide clear safe play area boundaries

### CoreML

Machine learning epistemic constraints.

**Patterns Blocked:**
- Claims of 100% accuracy
- Replacing human judgment for critical decisions
- Autonomous critical/life decisions

**Epistemic Bounds:**
- Always show prediction confidence
- Acknowledge model limitations
- Human oversight for critical decisions

**Warnings:**
- ML predictions have inherent uncertainty
- Display confidence scores to users
- Never claim 100% accuracy

---

## Web Frameworks

### React

Security and accessibility for React apps.

**Patterns Blocked:**
- `dangerouslySetInnerHTML` with user input
- Disabling security/sanitization
- `eval()` with dynamic content

**Security Requirements:**
- Sanitize all user inputs before rendering
- Use Content Security Policy headers
- Avoid `dangerouslySetInnerHTML` with untrusted content

**Accessibility Requirements:**
- Include ARIA labels on interactive elements
- Ensure keyboard navigation support
- Maintain focus management for modals/dialogs

**Warnings:**
- XSS vulnerabilities from unsanitized HTML
- Always escape user-provided content
- Use React's built-in XSS protections

### Node.js

Server-side security constraints.

**Patterns Blocked:**
- `eval()` or `vm.runIn` with user input
- `child_process` with unsanitized input
- SQL string concatenation

**Security Requirements:**
- Parameterized queries for databases
- Sanitize all user inputs
- Rate limiting on API endpoints
- Use helmet.js for security headers

**Warnings:**
- Command injection via unsanitized child_process
- SQL injection via string concatenation
- Prototype pollution vulnerabilities

### Django

Django-specific security patterns.

**Patterns Blocked:**
- `raw()` or `RawSQL` with user input
- `mark_safe()` with untrusted content
- `DEBUG=True` in production

**Security Requirements:**
- Use Django ORM instead of raw SQL
- Enable CSRF protection on all forms
- Set `DEBUG=False` in production
- Use secure cookie settings

**Warnings:**
- SQL injection via `raw()` with user input
- XSS via `mark_safe()` with untrusted content
- Always use Django's built-in protections

### Flask

Flask-specific security patterns.

**Patterns Blocked:**
- `render_template_string()` with user input
- `Markup` or `safe` with untrusted content
- `debug=True` in production
- Hardcoded `secret_key`

**Security Requirements:**
- Use `render_template()` not `render_template_string()` with user input
- Set strong `SECRET_KEY` from environment
- Disable debug mode in production
- Implement CSRF protection with Flask-WTF

**Warnings:**
- SSTI vulnerability via `render_template_string`
- Session hijacking with weak secret key
- Debug mode exposes sensitive information

---

## ML Frameworks

### TensorFlow

ML safety and epistemic constraints.

**Patterns Blocked:**
- Claims of guaranteed accuracy
- Autonomous critical decisions
- Training on private data without consent
- Deepfake identity creation

**Epistemic Bounds:**
- Always expose prediction confidence scores
- Use proper uncertainty estimation methods
- Human oversight for critical decisions
- Test for demographic and selection bias

**Data Requirements:**
- Document training data sources and licenses
- Implement data privacy protections
- Maintain model versioning and lineage

**Warnings:**
- ML models can perpetuate biases
- Never deploy without validation on held-out test set
- Monitor for distribution drift in production
- Document model limitations and failure modes

### PyTorch

PyTorch-specific security and safety.

**Patterns Blocked:**
- Claims of guaranteed accuracy
- Autonomous critical decisions
- `torch.load` with untrusted files
- Deepfake identity creation

**Security Requirements:**
- Never load untrusted pickle files (arbitrary code execution risk)
- Use `weights_only=True` for `torch.load` when possible
- Validate model checksums before loading

**Epistemic Bounds:**
- Always expose prediction confidence scores
- Use MC Dropout or ensembles for uncertainty
- Human oversight for critical decisions

**Warnings:**
- `torch.load` can execute arbitrary code - only load trusted models
- ML models can perpetuate biases in training data
- Monitor for adversarial inputs in production

---

## Integration Example

```python
import requests

def verify_code_intent(intent: str, framework: str) -> dict:
    """Verify AI coding intent against framework constraints."""
    response = requests.post(
        "https://api.parcri.net/frameworks/verify",
        params={"intent": intent, "framework": framework},
        headers={"X-API-Key": "your-api-key"}
    )
    return response.json()

# Example: Check if PyTorch code is safe
result = verify_code_intent(
    intent="Load a model from user-uploaded file",
    framework="pytorch"
)

if not result["passed"]:
    print("Security violations detected:")
    for v in result["violations"]:
        print(f"  - {v}")
```
