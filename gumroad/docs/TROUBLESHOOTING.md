# Newton for iOS - Troubleshooting Guide

**Common issues and their solutions**

```
╭──────────────────────────────────────────────────────────────╮
│   🔧 Newton Troubleshooting                                  │
│   Quick fixes for common problems                           │
╰──────────────────────────────────────────────────────────────╯
```

---

## Installation Issues

### ❌ "Shortcut Won't Install"

**Symptoms**: Tapping `Newton.shortcut` does nothing or shows error

**Causes & Solutions**:

1. **iOS version too old**
   - Requirement: iOS 17 or later
   - Check: Settings → General → About → iOS Version
   - Solution: Update iOS if possible

2. **"Untrusted Shortcuts" disabled**
   - Settings → Shortcuts → "Allow Untrusted Shortcuts" → Turn ON
   - You'll need to enter your passcode
   - This is normal for shortcuts outside App Store

3. **Corrupt download**
   - Re-download `newton_ios.zip` from Gumroad
   - Delete old version first
   - Make sure file completely downloads (check file size)

4. **Storage full**
   - Shortcuts need minimal space (~1MB) but iOS might block if storage critical
   - Check: Settings → General → iPhone Storage
   - Free up space if needed

### ❌ "Can't Unzip File"

**Symptoms**: ZIP file won't extract

**Solutions**:
1. Try **Files app** → tap ZIP → "Uncompress"
2. If that fails, try third-party unzip app (iZip, WinZip)
3. Verify file downloaded completely (should be ~2-5MB)
4. Re-download if corrupted

---

## Shortcut Not Appearing

### ❌ "Newton Not in Share Sheet"

**Symptoms**: Can't find Newton when sharing text

**Solutions**:

1. **Verify installation**
   - Open **Shortcuts app**
   - Look for "Newton" in "My Shortcuts"
   - If not there, reinstall

2. **Shortcut not enabled for Share Sheet**
   - Open **Shortcuts app**
   - Long press **Newton** shortcut
   - Check "Show in Share Sheet" is ON
   - If not visible, tap shortcut → Details → Toggle ON

3. **App doesn't support Share Sheet**
   - Some apps don't support sharing
   - Try **Notes app** first (always works)
   - Then try in other apps

4. **iOS cache issue**
   - **Restart iPhone** (fixes 90% of Share Sheet issues)
   - Power off completely, wait 10 seconds, power on

---

## Verification Problems

### ❌ "Verification Always Fails"

**Symptoms**: Every check shows "BLOCKED" or "ERROR"

**Debugging Steps**:

1. **Test with known-safe content**
   ```
   The weather in Houston is warm.
   ```
   - If this is BLOCKED, constraints are misconfigured

2. **Check internet connection**
   - Open Safari → visit https://newton-api.onrender.com/health
   - Should show: `{"status": "healthy"}`
   - If not, API is down or internet issue

3. **Constraint configuration**
   - Open Shortcuts app → Newton → Edit
   - Find the "constraints" parameter
   - Default: `["medical", "legal", "epistemic"]`
   - Try just: `["medical"]` to isolate issue

4. **API endpoint**
   - Shortcut should call: `https://newton-api.onrender.com/verify`
   - If different URL, it's misconfigured
   - Re-install shortcut

### ❌ "Verification Always Passes"

**Symptoms**: Even problematic content shows "VERIFIED"

**Causes**:

1. **No constraints enabled**
   - Check constraint array isn't empty: `[]`
   - Should have at least: `["medical"]`

2. **Wrong API endpoint**
   - Might be calling `/health` instead of `/verify`
   - Edit shortcut, check URL

3. **Content field not passed**
   - Verify "input" field contains the text
   - Shortcut should pass: `{"input": "{{text}}", "constraints": [...]}`

### ❌ "Verification Too Slow"

**Symptoms**: Takes >5 seconds to get result

**Causes & Solutions**:

1. **Cold start (first use)**
   - Free tier API "sleeps" when unused
   - First verification may take 3-5 seconds
   - Subsequent ones are fast (<1 second)
   - **Solution**: This is normal, wait for first response

2. **Poor internet connection**
   - Check WiFi/cellular strength
   - Try different network
   - API timeout is 30 seconds

3. **Complex constraints**
   - More constraints = slightly longer verification
   - Still should be <2 seconds total
   - If not, report as bug

4. **API overload**
   - Rare: many users at once
   - Wait 30 seconds and retry
   - Check status: https://newton-api.onrender.com/health

---

## Error Messages

### ❌ "Network Error"

**Meaning**: Can't reach verification API

**Solutions**:
1. Check internet connection
2. Try cellular if on WiFi (or vice versa)
3. Check if API is down: visit /health endpoint in Safari
4. Try again in 30 seconds (might be cold start)

### ❌ "Invalid Response"

**Meaning**: API returned unexpected format

**Solutions**:
1. Update shortcut (might be old version)
2. Re-download from Gumroad
3. Check API endpoint is correct
4. Report as bug if persists

### ❌ "Timeout"

**Meaning**: Verification took >30 seconds

**Solutions**:
1. Check internet connection (might be very slow)
2. Try shorter text (very long text takes longer)
3. Reduce number of constraints
4. Report as bug if happens with short text

### ❌ "Constraint Parse Error"

**Meaning**: Constraint format invalid

**Solutions**:
1. Don't modify constraint JSON manually unless experienced
2. Re-download original shortcut
3. See CUSTOMIZATION.md for proper constraint syntax
4. Validate JSON: https://jsonlint.com/

---

## Performance Issues

### 🐌 "Shortcut Runs Slowly"

**Expected Performance**:
- First run after API sleep: 2-5 seconds
- Subsequent runs: <1 second
- Local processing: ~100ms
- Network latency: varies by connection

**If Slower**:
1. Check network speed (not Newton issue)
2. Reduce number of constraints
3. Use shorter input text
4. Restart iPhone (clears background tasks)

### 🔋 "Battery Drain"

Newton uses minimal battery:
- Single verification: ~0.01% battery
- Network request only when you use it
- No background activity

**If draining**:
- Not Newton - check other apps
- Shortcuts don't run in background
- Only uses power when you trigger it

---

## Constraint Issues

### ❌ "Too Many False Positives"

**Symptoms**: Safe content gets blocked

**Solutions**:

1. **Use fewer constraints**
   - Start with just `["medical"]`
   - Add others as needed

2. **Constraint too aggressive**
   - Medical constraints are strict by design
   - This is intentional for safety
   - See CUSTOMIZATION.md to adjust

3. **Context not understood**
   - Constraints use pattern matching, not AI
   - They don't understand intent
   - Example: "don't take aspirin" triggers medical constraint
   - **This is correct behavior** - it's medical advice (negative advice is still advice)

### ❌ "False Negatives"

**Symptoms**: Problematic content not caught

**Causes**:
1. **Constraints are pattern-based**
   - They match specific phrases/patterns
   - Novel phrasings might slip through
   - This is a limitation of deterministic systems

2. **Constraint gap**
   - Pattern not in library
   - You can add it! See CUSTOMIZATION.md

**Reporting**: If you find consistent gap, report on GitHub with examples

---

## Customization Problems

### ❌ "Custom Constraint Won't Work"

See **CUSTOMIZATION.md** for detailed guide.

**Common mistakes**:
1. Invalid JSON syntax
2. Wrong operator for data type
3. Missing required fields
4. Regex syntax error

**Validation**:
1. Check JSON: https://jsonlint.com/
2. Test regex: https://regex101.com/
3. Verify against constraint_schema.json

---

## Privacy & Security

### ❓ "What data is sent?"

**Only**:
- The text you explicitly share to Newton
- Your chosen constraint categories

**Never**:
- Device information
- Location
- Other apps' data
- Browsing history
- Contacts

### ❓ "Is my data stored?"

**No**. API endpoint:
- Receives text
- Verifies constraints
- Returns result
- **Does not store anything**

Verification is stateless and ephemeral.

### ❓ "Can I use offline?"

**Currently: No**. Newton requires:
- Internet connection
- API call to verification server

**Future**: Local-only mode planned for v2.0

---

## Getting Help

### 📧 Support Channels

1. **This guide**: Most issues covered here
2. **CUSTOMIZATION.md**: For constraint questions
3. **GitHub Issues**: Bug reports and feature requests
   - https://github.com/jaredlewiswechs/Newton-api/issues
4. **Gumroad Comments**: Community discussion

### 🐛 Reporting Bugs

**Include**:
1. iOS version (Settings → General → About)
2. Exact error message (screenshot helpful)
3. Steps to reproduce
4. Example text that causes issue (if not sensitive)

**Don't include**:
- Sensitive personal information
- API keys (if you have one)
- Medical/legal details

### 💡 Feature Requests

Open GitHub issue with:
1. Clear use case
2. Proposed behavior
3. Why existing features don't work

---

## Known Limitations

### Current Version (v1.0.0)

**By Design**:
1. **Pattern-based, not AI-based**
   - Fast and deterministic
   - But can miss novel phrasings

2. **Requires internet**
   - API call needed for verification
   - Local-only mode coming in v2.0

3. **English only**
   - Constraints written for English text
   - Other languages may work partially

4. **False positives possible**
   - Safety-first approach
   - Better to block safe content than miss dangerous content

**Not Limitations**:
- Speed: <1 second is expected
- Accuracy: Pattern matching is intentional design choice
- Privacy: Only shared text sent to API

---

## Still Stuck?

**Emergency Checklist**:
- [ ] iOS 17+ installed
- [ ] "Allow Untrusted Shortcuts" enabled
- [ ] Internet connection working
- [ ] Shortcut appears in Shortcuts app
- [ ] Tested with simple safe text first
- [ ] API health check passes (visit /health)
- [ ] Restarted iPhone

**90%** of issues solved by restart + reinstall.

**Still not working?**
- Open GitHub issue with full details
- Community will help troubleshoot
- Updates released regularly

---

## Version

v1.0.0 - January 2026

Check Gumroad for updates.

---

**Newton works. If it doesn't, we'll fix it.**

```
1 == 1
```
