# Newton for iOS - Customization Guide

**Create your own constraints - no coding required (mostly)**

```
╭──────────────────────────────────────────────────────────────╮
│   🛠️ Make Newton Your Own                                    │
│   Custom constraints, adjusted sensitivity, personal rules  │
╰──────────────────────────────────────────────────────────────╯
```

---

## What You Can Customize

Newton comes with three pre-built constraint libraries:
1. **Medical** - Health/drug advice
2. **Legal** - Legal advice/claims
3. **Epistemic** - Logic/reasoning

**But you can**:
- ✅ Turn categories on/off
- ✅ Adjust which rules run
- ✅ Create entirely new constraints
- ✅ Share constraints with others

---

## Quick Customizations (No JSON Editing)

### Turn Off Constraint Categories

**Default**: All three categories enabled
```json
"constraints": ["medical", "legal", "epistemic"]
```

**To disable epistemic** (only check medical and legal):
1. Open **Shortcuts** app
2. Find **Newton** shortcut
3. Tap **⋯** (three dots) → **Edit**
4. Find the "Get contents of URL" action
5. Find the JSON: `"constraints": [...]`
6. Delete `"epistemic"` from the array

**Result**:
```json
"constraints": ["medical", "legal"]
```

**Or just one**:
```json
"constraints": ["medical"]
```

**Save** and test!

### Change Shortcut Name

Want to call it something else?
1. Shortcuts app → Newton
2. Tap **⋯** → **Rename**
3. Type new name
4. Still works the same!

---

## CDL Syntax Basics

**CDL** = Constraint Definition Language

Think of it like a recipe:
- **Rule**: What to check
- **Operator**: How to check it
- **Value**: What to look for
- **Action**: What to do if found

### Constraint Structure

```json
{
  "id": "unique_rule_name",
  "operator": "contains",
  "field": "content",
  "value": ["word1", "word2"],
  "action": "DENY",
  "severity": "HIGH",
  "message": "Explanation shown to user"
}
```

**Required fields**:
- `id`: Unique name (no spaces)
- `operator`: How to match (see below)
- `field`: What to check (usually "content")
- `action`: DENY, WARN, LOG, FLAG
- `severity`: CRITICAL, HIGH, MEDIUM, LOW

**Optional**:
- `message`: Custom text to show user
- `examples`: Test cases
- `pattern_type`: keyword, regex, semantic

---

## Available Operators

### Comparison Operators

```json
// Equals
{"operator": "eq", "value": "exact text"}

// Not equals
{"operator": "ne", "value": "this text"}

// Greater than / Less than (for numbers)
{"operator": "gt", "value": 100}
{"operator": "lt", "value": 50}
```

### String Operators

```json
// Contains (case-insensitive by default)
{"operator": "contains", "value": ["aspirin", "ibuprofen"]}

// Matches regex pattern
{"operator": "matches", "value": "\\d+ mg"}

// In list
{"operator": "in", "value": ["safe", "allowed", "ok"]}

// Not in list
{"operator": "not_in", "value": ["dangerous", "blocked"]}
```

### Existence Operators

```json
// Field exists
{"operator": "exists", "field": "metadata.source"}

// Field is empty
{"operator": "empty", "field": "citations"}
```

---

## Example Custom Constraints

### 1. Profanity Filter

**Goal**: Block profanity

```json
{
  "id": "profanity_block",
  "operator": "contains",
  "field": "content",
  "value": ["damn", "hell", "crap", "shit", "fuck"],
  "action": "DENY",
  "severity": "MEDIUM",
  "message": "⚠️ Profanity detected. Content blocked."
}
```

**How to add**:
1. Copy this JSON
2. Create file: `profanity_constraints.json`
3. Wrap in full constraint library format (see schema)
4. Modify shortcut to load this file

### 2. Marketing Spam Detection

**Goal**: Detect pushy sales language

```json
{
  "id": "marketing_spam",
  "operator": "contains",
  "field": "content",
  "value": [
    "act now",
    "limited time",
    "order today",
    "click here",
    "buy now",
    "special offer",
    "don't miss out"
  ],
  "action": "WARN",
  "severity": "LOW",
  "message": "⚠️ Marketing language detected. Be skeptical of urgency claims."
}
```

### 3. Political Bias Detection

**Goal**: Flag strong political language

```json
{
  "id": "political_bias",
  "operator": "contains",
  "field": "content",
  "value": [
    "libtard",
    "conservatard",
    "sheeple",
    "wake up",
    "mainstream media lies",
    "deep state"
  ],
  "action": "WARN",
  "severity": "MEDIUM",
  "message": "⚠️ Politically charged language detected. Consider source bias."
}
```

### 4. Financial Advice Detection

**Goal**: Catch investment recommendations

```json
{
  "id": "investment_advice",
  "operator": "matches",
  "field": "content",
  "value": "\\b(buy|sell|invest in|short|hold)\\b.{0,50}\\b(stock|crypto|bitcoin|shares|options)",
  "action": "DENY",
  "severity": "CRITICAL",
  "message": "⚠️ BLOCKED: Financial advice detected. Consult licensed financial advisor."
}
```

### 5. Tone Policing

**Goal**: Detect aggressive tone

```json
{
  "id": "aggressive_tone",
  "operator": "matches",
  "field": "content",
  "value": "\\b(you always|you never|you're wrong|that's stupid|obviously|clearly you)\\b",
  "action": "FLAG",
  "severity": "LOW",
  "message": "ℹ️ Aggressive tone detected. Consider rephrasing more constructively."
}
```

---

## Regex Patterns (Advanced)

**Regular expressions** are powerful for pattern matching.

### Common Regex Patterns

```regex
// Any number
\\d+

// Email address
[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}

// Phone number (US)
\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}

// URL
https?://[^\\s]+

// Dollar amount
\\$\\d+(\\.\\d{2})?

// Date (MM/DD/YYYY)
\\d{2}/\\d{2}/\\d{4}
```

### Regex Operators

```regex
// One or more: +
\\d+     // matches "123", "4", "56789"

// Zero or more: *
\\d*     // matches "", "123", "4"

// Optional: ?
https?   // matches "http" or "https"

// Word boundary: \\b
\\bcat\\b  // matches "cat" but not "category"

// Or: |
cat|dog  // matches "cat" or "dog"

// Character class: []
[a-z]    // any lowercase letter
[0-9]    // any digit
```

### Test Your Regex

**Before adding to constraint:**
1. Visit https://regex101.com/
2. Select "Python" flavor
3. Paste your regex
4. Test with example text
5. Verify matches

---

## Creating a Full Constraint Library

### Step 1: Create JSON File

File: `custom_constraints.json`

```json
{
  "name": "custom_constraints",
  "description": "My personal custom constraints",
  "version": "1.0.0",
  "domain": "custom",
  "rules": [
    {
      "id": "my_first_rule",
      "operator": "contains",
      "field": "content",
      "value": ["test", "example"],
      "action": "WARN",
      "severity": "LOW",
      "message": "This is my custom rule!"
    }
  ],
  "metadata": {
    "author": "Your Name",
    "created": "2026-01-03T00:00:00Z",
    "tags": ["custom", "personal"]
  }
}
```

### Step 2: Validate JSON

1. Copy your JSON
2. Visit https://jsonlint.com/
3. Paste and click "Validate JSON"
4. Fix any errors shown

### Step 3: Validate Against Schema

Check against `constraint_schema.json`:
- All required fields present?
- Operators valid? (see schema for list)
- Actions valid? (DENY, WARN, LOG, FLAG)
- Severity valid? (CRITICAL, HIGH, MEDIUM, LOW)

### Step 4: Test Locally

Before adding to shortcut, test with API:

```bash
curl -X POST https://newton-api-1.onrender.com/verify \
  -H "Content-Type: application/json" \
  -d '{
    "input": "test text here",
    "constraints": ["custom"]
  }'
```

(You'll need to load your custom constraints to the API first)

### Step 5: Add to Shortcut

**Option A: Embed in Shortcut**
1. Open Shortcuts → Newton → Edit
2. Find the JSON request body
3. Add your rules inline

**Option B: Load from File** (requires file access)
1. Save `custom_constraints.json` to iCloud Drive
2. Add "Get File" action in Shortcut
3. Parse JSON
4. Merge with constraints array

---

## Advanced: Combining Constraints

### AND Logic (All must match)

Check for multiple conditions:

```json
{
  "id": "medical_and_dosage",
  "operator": "contains",
  "field": "content",
  "value": ["prescription", "dosage"],
  "action": "DENY",
  "severity": "HIGH",
  "message": "Medical dosage advice detected"
}
```

**Limitation**: CDL evaluates each rule independently.  
For complex AND logic, use regex.

### OR Logic (Any can match)

Already built-in:

```json
{
  "operator": "contains",
  "value": ["option1", "option2", "option3"]
}
```

If ANY value matches, rule triggers.

### NOT Logic (Inverse)

Use `not_in`:

```json
{
  "operator": "not_in",
  "value": ["safe", "verified", "approved"]
}
```

---

## Action Types Explained

### DENY
- **Behavior**: Block content, show error
- **Use for**: Critical safety issues
- **Example**: Medical advice, legal recommendations

### WARN
- **Behavior**: Show content with warning
- **Use for**: Potentially problematic but not dangerous
- **Example**: Missing citations, biased language

### LOG
- **Behavior**: Note in logs, show content normally
- **Use for**: Informational tracking
- **Example**: Positive safety advice ("call 911")

### FLAG
- **Behavior**: Mark for review, show content
- **Use for**: Needs human judgment
- **Example**: Ambiguous tone, subjective quality issues

---

## Severity Levels Explained

### CRITICAL
- Immediate danger
- Always block
- **Example**: Drug dosages, financial scams

### HIGH
- Serious but not immediate danger
- Usually block
- **Example**: Legal advice, medical diagnoses

### MEDIUM
- Problematic but manageable
- Warn user
- **Example**: Logical fallacies, missing sources

### LOW
- Minor issues
- Informational
- **Example**: Tone issues, formatting

---

## False Positive Mitigation

### Problem: Safe content gets blocked

**Example**:
> "Don't take aspirin without consulting a doctor"

Triggers medical constraint but is actually **good advice**.

### Solution 1: Context Words

Add exclusions:

```json
{
  "id": "medical_advice",
  "operator": "contains",
  "value": ["take aspirin"],
  "false_positive_mitigation": {
    "context_words": ["don't", "never", "avoid", "consult doctor"],
    "exclusion_patterns": ["consult.*doctor", "talk.*physician"]
  }
}
```

### Solution 2: More Specific Patterns

Instead of:
```json
{"value": ["take aspirin"]}
```

Use:
```json
{"value": ["you should take aspirin", "take aspirin daily"]}
```

### Solution 3: Lower Severity

If blocking safe content:
- Change `DENY` to `WARN`
- Change `CRITICAL` to `HIGH`
- Let user see it with warning

---

## Testing Your Constraints

### Test Cases

Create examples for each rule:

**Pass cases** (should not trigger):
```
"The weather is nice today"
"I like chocolate ice cream"
"This is a safe, normal sentence"
```

**Fail cases** (should trigger):
```
"Take 500mg of aspirin"  // Medical
"You should sue them"    // Legal
"Studies show this works" // Epistemic (no citation)
```

### Testing Process

1. **Start simple**: One rule at a time
2. **Test pass cases**: Should get ✅ VERIFIED
3. **Test fail cases**: Should get ❌ BLOCKED
4. **Iterate**: Adjust patterns if wrong
5. **Share**: Post working constraints to community

---

## Sharing Your Constraints

### On GitHub
1. Fork repository
2. Add your JSON to `/gumroad/constraints/`
3. Submit pull request
4. Maintainers review and merge

### On Gumroad
1. Create `.json` file
2. Zip it
3. Share in product comments
4. Others can download and use

### Best Practices
- **Document**: Explain what your constraint does
- **Test**: Verify it works before sharing
- **Examples**: Include test cases
- **License**: Specify usage terms

---

## Common Mistakes

### ❌ Invalid JSON
```json
{
  "id": "test",
  "value": "test",  // Missing comma at end
  "action": "DENY"
}
```

**Fix**: Use JSON validator

### ❌ Missing Required Fields
```json
{
  "operator": "contains",
  "value": "test"
  // Missing: id, field, action, severity
}
```

**Fix**: Check schema, add all required fields

### ❌ Regex Not Escaped
```json
{"value": "\d+"}  // Wrong - needs double backslash
```

**Fix**:
```json
{"value": "\\d+"}  // Correct
```

### ❌ Too Broad Pattern
```json
{"value": ["the", "a", "is"]}  // Triggers on everything!
```

**Fix**: Be more specific, use longer phrases

### ❌ Wrong Operator
```json
{"operator": "contains", "value": 50}  // Contains needs string/array
```

**Fix**: Use `eq`, `gt`, `lt` for numbers

---

## Performance Tips

### Keep It Fast

**Newton is fast (<1 second) because**:
- Constraints are simple pattern matching
- No AI processing
- Deterministic checks

**To keep it fast**:
1. **Fewer rules** = faster
2. **Simple patterns** = faster
3. **Short regex** = faster

**Avoid**:
- Very complex regex (causes backtracking)
- Hundreds of rules (check 10-20 max)
- Regex with many alternations (use separate rules instead)

### Optimization

Instead of:
```json
{"value": "word1|word2|word3|word4|word5|..."}  // Slow regex
```

Use:
```json
{"value": ["word1", "word2", "word3", "word4", "word5"]}  // Fast array
```

---

## Getting Help

### Resources
1. **Schema**: `constraint_schema.json` - Full specification
2. **Examples**: Pre-built constraints in `/constraints/`
3. **Regex Tester**: https://regex101.com/
4. **JSON Validator**: https://jsonlint.com/

### Community
- **GitHub Issues**: Ask questions, share constraints
- **Gumroad Comments**: Discuss with other users
- **Documentation**: Read WHITEPAPER.md for technical details

---

## Summary Checklist

**To create custom constraint**:
- [ ] Define what you want to detect
- [ ] Choose appropriate operator
- [ ] Write pattern (keyword or regex)
- [ ] Test with examples
- [ ] Validate JSON syntax
- [ ] Check against schema
- [ ] Add to shortcut or file
- [ ] Test in real usage
- [ ] Iterate and refine
- [ ] Share with community (optional)

---

## Version

v1.0.0 - January 2026

---

**Your Newton. Your rules. Your safety.**

```
1 == 1
```
