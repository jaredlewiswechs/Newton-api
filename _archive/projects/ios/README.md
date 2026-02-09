# Newton iOS

**Verified computation at your fingertips.**

Native iOS client for the Newton Supercomputer API. Built with SwiftUI and Apple Human Interface Guidelines 2026.

## Features

- **Dashboard** — Real-time system health monitoring with pull-to-refresh
- **Verify** — Content safety verification with cryptographic proofs
- **Calculate** — Verified arithmetic operations with audit trail
- **Settings** — Server configuration and dark mode support

## Requirements

- iOS 17.0+
- Xcode 15.2+
- Apple Developer account (for TestFlight deployment)

## Architecture

```
Newton/
├── Sources/
│   ├── NewtonApp.swift      # App entry point
│   ├── ContentView.swift    # Tab navigation
│   ├── NewtonModels.swift   # API response models
│   ├── NewtonAPI.swift      # Network client
│   ├── DashboardView.swift  # System health dashboard
│   ├── VerifyView.swift     # Content verification
│   ├── CalculateView.swift  # Verified calculator
│   └── SettingsView.swift   # Configuration
├── Resources/
│   └── Info.plist
└── Assets.xcassets/
```

## Design

- **Liquid Glass** — iOS 26 translucent material design
- **SF Symbols** — Native iconography
- **Haptic Feedback** — Success/error tactile responses
- **Dark Mode** — Full system integration

## No-Mac Development Workflow

This project is designed for cloud-based iOS development:

1. **Edit code** in this repository (GitHub, Codespaces, or any editor)
2. **Push to GitHub** to trigger the build workflow
3. **GitHub Actions** builds on `macos-latest` runners
4. **TestFlight** receives the build automatically
5. **Install on your iPhone** via the TestFlight app

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `APPLE_TEAM_ID` | Your 10-character Apple Developer Team ID |
| `APP_STORE_CONNECT_API_KEY_ID` | App Store Connect API Key ID |
| `APP_STORE_CONNECT_ISSUER_ID` | App Store Connect Issuer ID |
| `APP_STORE_CONNECT_API_KEY` | Base64-encoded .p8 API key file |
| `CERTIFICATE_P12` | Base64-encoded distribution certificate |
| `CERTIFICATE_PASSWORD` | Certificate password |
| `PROVISIONING_PROFILE` | Base64-encoded provisioning profile |

### Setting Up Secrets

1. **Create App Store Connect API Key:**
   - Go to [App Store Connect](https://appstoreconnect.apple.com) → Users and Access → Keys
   - Generate a new key with "App Manager" access
   - Download the .p8 file and note the Key ID and Issuer ID

2. **Export Distribution Certificate:**
   ```bash
   # On a Mac with your certificate in Keychain:
   security find-identity -v -p codesigning
   # Export from Keychain Access as .p12
   base64 -i certificate.p12 | pbcopy
   ```

3. **Get Provisioning Profile:**
   - Create at [Apple Developer Portal](https://developer.apple.com)
   - Download and base64 encode:
   ```bash
   base64 -i profile.mobileprovision | pbcopy
   ```

## Local Development (if you have a Mac)

```bash
# Open in Xcode
open ios/Newton.xcodeproj

# Build from command line
xcodebuild -project ios/Newton.xcodeproj -scheme Newton -configuration Debug
```

## API Endpoints Used

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System status check |
| `/verify` | POST | Content safety verification |
| `/calculate` | POST | Verified arithmetic |

## Verified by Newton

This app was specified and verified using Newton's Rosetta Compiler:

```
Fingerprint: 965D37E215C6
Verified: true
Elapsed: 3.5ms
```

---

---

## Learning Resources

For a comprehensive guide to Swift, SwiftUI, and Swift Playgrounds with Newton integration, see the [Swift & SwiftUI Combinatorial Guide](../docs/frameworks/SWIFT_SWIFTUI_GUIDE.md).

---

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
