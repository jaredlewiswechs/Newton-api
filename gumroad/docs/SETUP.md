# Newton for iOS - Setup Guide

**Installation Time: 2 minutes**  
**No technical knowledge required**

```
╭──────────────────────────────────────────────────────────────╮
│   🍎 Newton for iOS - Quick Setup                            │
│   From download to first verification in 2 minutes          │
╰──────────────────────────────────────────────────────────────╯
```

## What You Need

- ✅ iPhone or iPad running **iOS 17 or later**
- ✅ **Files app** (built into iOS)
- ✅ **Internet connection** (for API verification)

## Step 1: Download (30 seconds) 📥

1. Download `newton_ios.zip` from Gumroad
2. File will appear in your **Downloads** folder
3. Tap the ZIP file to unzip it automatically
4. You'll see a folder called `newton_ios`

## Step 2: Install Shortcut (45 seconds) ⚡

1. **Open the `newton_ios` folder** in Files app
2. **Navigate to** `shortcuts/` folder
3. **Tap `Newton.shortcut`**
4. iOS will ask "Add Shortcut?" → **Tap "Add Shortcut"**

**⚠️ If you see "Shortcuts Not Allowed":**
- Go to **Settings** → **Shortcuts**
- Turn ON **"Allow Untrusted Shortcuts"**
- Go back and tap `Newton.shortcut` again

## Step 3: Enable in Share Sheet (30 seconds) 📤

1. **Open any app** with text (Notes, Messages, Safari, etc.)
2. **Select some text**
3. **Tap the Share button** (square with arrow pointing up)
4. **Scroll down** to "Actions" section
5. **Find "Newton"** in the list (it's alphabetical)
6. **Tap to run** for the first time

## Step 4: First Verification (15 seconds) ✨

**Test Newton with this sample text:**

Copy this into Notes:
```
You should take 500mg of aspirin twice daily for your headaches.
```

1. **Select the text**
2. **Tap Share → Newton**
3. **Watch for result:**
   - ❌ **BLOCKED** - Newton correctly detects medical advice!
   - Violation message will appear
   - Content is prevented from executing

**Try a safe text:**
```
The weather in Houston is usually warm and humid.
```

1. **Select and share to Newton**
2. **Watch for result:**
   - ✅ **VERIFIED** - Newton allows safe content
   - Green checkmark appears
   - Original content is shown

## Congratulations! 🎉

Newton is now protecting you from unverified AI claims.

---

## Choosing Which Constraints to Use

Newton includes three constraint categories:

| Category | Detects | Use When |
|----------|---------|----------|
| **Medical** | Drug advice, diagnoses, treatment claims | Verifying health information |
| **Legal** | Legal advice, jurisdiction claims, rights statements | Verifying legal information |
| **Epistemic** | Logical fallacies, contradictions, missing sources | Verifying any factual claims |

**Default**: All three are enabled. This provides maximum protection.

**To customize** which constraints run:
1. Open **Shortcuts app**
2. Find **Newton** shortcut
3. Tap the **⋯** button (three dots)
4. Tap **Edit**
5. Find the "constraints" array in the API call
6. Remove constraint names you don't want to check

Example: To only check medical claims:
```json
"constraints": ["medical"]
```

**More details**: See `CUSTOMIZATION.md`

---

## What Newton Does

```
┌─────────────────────────────────────────────────┐
│  1. You share text to Newton                    │
│     ↓                                            │
│  2. Newton sends to verification API            │
│     ↓                                            │
│  3. API checks against active constraints       │
│     ↓                                            │
│  4. Result returned in <1 second                │
│     ↓                                            │
│  5a. ✅ VERIFIED → Show content                 │
│  5b. ❌ BLOCKED → Show violations               │
└─────────────────────────────────────────────────┘
```

**Fast**: Verification completes in under 1 second  
**Deterministic**: Same input always gives same result  
**Private**: Only the text you share is sent to API

---

## Common Setup Questions

### "I can't find the Shortcuts app"
- It's built into iOS 17+
- Look for blue icon with white squares
- If deleted, re-download from App Store (free)

### "The shortcut won't install"
1. Check iOS version (Settings → General → About)
2. Make sure iOS 17+ is installed
3. Enable "Allow Untrusted Shortcuts" (see Step 2)

### "Newton doesn't appear in Share Sheet"
1. Make sure shortcut is installed (open Shortcuts app)
2. Try restarting your device
3. Some apps don't support Share Sheet - try Notes first

### "Verification is slow"
- Check internet connection
- API is hosted on free tier - may have cold start (~2-3 seconds first time)
- Subsequent verifications are fast (<1 second)

### "Every check says BLOCKED"
- This might be correct! Try verifying safe content first
- Check constraint configuration (see CUSTOMIZATION.md)
- Verify API endpoint is reachable

**More troubleshooting**: See `TROUBLESHOOTING.md`

---

## Next Steps

### 📖 **Learn More**
- Read `WHITEPAPER_SIMPLE.md` to understand how Newton works
- No math required - explained with analogies

### 🛠️ **Customize**
- Create your own constraints (profanity, tone, style)
- See `CUSTOMIZATION.md` for CDL syntax guide

### 🎯 **Use Cases**
- Verify AI chatbot responses before acting
- Check medical information before sharing
- Validate legal claims before trusting
- Screen content for logical consistency

---

## Privacy & Data

**What leaves your device:**
- Only the text you explicitly share to Newton
- Sent to: `https://newton-api.onrender.com/verify`
- Used for: Constraint verification only
- Stored: Not stored - verification only

**What stays local:**
- Your constraint configurations
- Which shortcuts you run
- Everything else

**No tracking, no analytics, no ads.**

---

## Support

**Having issues?** See `TROUBLESHOOTING.md`

**Want to customize?** See `CUSTOMIZATION.md`

**Technical details?** See main `WHITEPAPER.md` in repository

**Found a bug?** Report on GitHub: https://github.com/jaredlewiswechs/Newton-api

---

## Version

Newton for iOS v1.0.0 - January 2026

**Updates**: Check Gumroad product page for new versions

---

**You're protected. Start verifying AI content with confidence.**

```
1 == 1
```
