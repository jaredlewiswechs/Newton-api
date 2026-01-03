# Newton for iOS - Gumroad Product Package

```
╭──────────────────────────────────────────────────────────────╮
│                                                              │
│   🍎 Newton for iOS                                          │
│   Local-First AI Safety Layer                               │
│                                                              │
│   One-time purchase: $9                                     │
│   No subscription. No data collection. Pure verification.   │
│                                                              │
╰──────────────────────────────────────────────────────────────╯
```

## What Is This?

Newton for iOS is an **Apple Shortcuts-based AI safety layer** that runs entirely on your iPhone (iOS 17+). It verifies AI-generated content against deterministic constraints before you act on it.

**The Problem**: AI hallucinates. It generates confident-sounding medical advice, legal claims, and logical contradictions without verification.

**The Solution**: Newton checks `1 == 1` before execution. If a constraint fails, the content is blocked.

## What's Included

### 📱 Shortcuts
- **Newton.shortcut** - Full verification with all constraint categories
- **NewtonVerify.shortcut** - Lightweight verify-only version

### 🛡️ Pre-Built Constraint Libraries
- **Medical** - Detects unverified medical claims, dosage recommendations, diagnoses
- **Legal** - Detects unlicensed legal advice, jurisdiction-specific claims
- **Epistemic** - Detects logical contradictions, unfalsifiable claims, missing citations

### 📚 Documentation
- **SETUP.md** - 2-minute installation guide (no technical knowledge required)
- **WHITEPAPER_SIMPLE.md** - How Newton works (explained with analogies, not calculus)
- **TROUBLESHOOTING.md** - Common issues and fixes
- **CUSTOMIZATION.md** - Create your own custom constraints

### 🎨 Assets
- Demo video script
- Product screenshots
- Newton branding icons

## How It Works

```
1. You receive text from an AI (ChatGPT, Claude, etc.)
2. Share it to Newton via iOS Share Sheet
3. Newton verifies against your chosen constraints
4. ✅ Verified → Show content with green checkmark
5. ❌ Blocked → Show violations with red X, prevent execution
```

**Verification happens in <1 second** (network + compute).
**All constraints are deterministic** (same input → same output).
**Your data never leaves your device** unless you explicitly verify against the remote API.

## The Newton Difference

| Traditional AI Safety | Newton |
|----------------------|--------|
| Hope the model behaves | **Define constraints first** |
| Test after generation | **Verify before execution** |
| Probabilistic | **Deterministic** |
| Black box | **Glass box** |
| Subscription SaaS | **One-time purchase** |

## Installation (30 Seconds)

1. Download `newton_ios.zip`
2. Unzip and tap `Newton.shortcut`
3. Allow Shortcut installation in Settings
4. Share any text to Newton to verify

**Full setup guide**: See `docs/SETUP.md`

## Why Local-First?

**Privacy**: Your data never leaves your device unless you explicitly call the verification API.

**Ownership**: One-time purchase, no subscription. You own it forever.

**Speed**: Shortcuts run instantly. No waiting for cloud processing.

**Transparency**: All constraints are readable JSON. No black boxes.

## Technical Details

- **Platform**: iOS 17+ (iPhone, iPad)
- **Requirements**: Internet connection for API verification (optional for local-only mode)
- **API Endpoint**: `https://newton-api.onrender.com/verify`
- **Verification Time**: <1 second (median 2.31ms API latency)
- **Constraint Language**: CDL 3.0 (Constraint Definition Language)

## Build From Source

Generate the Shortcuts programmatically:

```bash
# Install dependencies
pip install -r requirements.txt

# Build shortcuts
python gumroad/build_shortcut.py --output gumroad/shortcuts/

# Generate ZIP package
python gumroad/build_shortcut.py --package
```

See `build_shortcut.py` for full CLI options.

## Support

- **Setup Issues**: See `docs/TROUBLESHOOTING.md`
- **Custom Constraints**: See `docs/CUSTOMIZATION.md`
- **API Documentation**: See main README.md at repository root
- **Technical Whitepaper**: See `WHITEPAPER.md` at repository root

## License

**Single user, unlimited devices**. This license permits use on all devices you own. Commercial use requires separate licensing.

## About Newton

Newton is a verified computation system where:
- The **constraint** IS the instruction
- The **verification** IS the computation
- The **network** IS the processor

Built by Jared Lewis · Ada Computing Company · Houston, Texas

> "1 == 1. The cloud is weather. We're building shelter."

---

## Version

**v1.0.0** - January 2026 - Initial Gumroad Release

## Repository

Full source code: https://github.com/jaredlewiswechs/Newton-api

---

**Ready to verify?** Install Newton and never trust unverified AI output again.
