# tinyTalk Curriculum Ideas
## Progressive Learning Path

---

## Philosophy: English First, Code Second

tinyTalk should feel like writing rules in English, not programming.

**Traditional Programming Mindset:**
"I need to write an if statement that checks conditions"

**tinyTalk Mindset:**
"I need to describe when something is allowed"

---

## Level 1: Single Conditions

### Concept: The Simplest Rule

```tinytalk
when button_clicked
fin show_menu
```

"When button is clicked, then show menu"

**Key Learning:**
- `when` = trigger
- `fin` = result
- That's it. That's the pattern.

### Practice Examples:
```tinytalk
when door_opened
fin ring_bell

when timer_done
fin play_sound

when page_loaded
fin show_content
```

---

## Level 2: Adding AND Conditions

### Concept: Multiple Things Must Be True

```tinytalk
when login_attempted
  and password_correct
  and account_active
fin access_granted
```

"When login is attempted AND password is correct AND account is active, then access is granted"

**Key Learning:**
- Indent conditions under `when`
- All `and` conditions must be true
- Read it like a checklist

### Practice Examples:
```tinytalk
when purchase_requested
  and item_in_stock
  and payment_valid
  and shipping_available
fin order_placed

when comment_posted
  and user_verified
  and content_clean
  and not_spam
fin comment_visible
```

---

## Level 3: Using NOT

### Concept: Something Must NOT Be True

```tinytalk
when post_submitted
  and user_verified
  and not_banned
  and not_rate_limited
fin post_published
```

**Key Learning:**
- `not_` prefix means condition must be false
- Often used for blocklist/denylist patterns
- Negative conditions are just as important

### Practice Examples:
```tinytalk
when withdrawal_requested
  and sufficient_balance
  and not_frozen
  and not_suspicious
fin withdrawal_approved

when message_sent
  and recipient_exists
  and not_blocked
  and not_muted
fin message_delivered
```

---

## Level 4: Comparisons

### Concept: Checking Values

```tinytalk
when token_check
  and f < g
  and remaining > 0
fin usage_allowed
```

**Key Learning:**
- `f < g` = current value less than limit
- `remaining > 0` = positive remaining
- Compare numbers, not just true/false

### Operators:
- `<` less than
- `>` greater than
- `<=` less than or equal
- `>=` greater than or equal
- `=` equals

### Practice Examples:
```tinytalk
when storage_upload
  and file_size < max_size
  and used_space < total_space
fin upload_allowed

when game_action
  and energy > 0
  and cooldown = 0
fin action_allowed
```

---

## Level 5: Variables and References

### Concept: Using Dynamic Values

```tinytalk
rule rate_limit
  f: current_requests
  g: max_requests
  when api_call
    and f < g
  fin request_allowed
```

**Key Learning:**
- `f:` and `g:` define what we're comparing
- Variables can come from user, system, or context
- Same rule, different values

### Practice Examples:
```tinytalk
rule quota_check
  f: messages_sent
  g: daily_limit
  when send_message
    and f < g
  fin message_queued

rule balance_check
  f: current_balance
  g: withdrawal_amount
  when withdraw
    and f >= g
  fin withdrawal_processed
```

---

## Level 6: Multiple Rules

### Concept: Rules Work Together

```tinytalk
rule auth_check
  when access_requested
    and token_valid
    and not_expired
  fin user_authenticated

rule permission_check
  when action_requested
    and user_authenticated
    and has_permission
  fin action_allowed

rule rate_limit
  when action_allowed
    and requests < limit
  fin action_executed
```

**Key Learning:**
- Rules can reference each other
- Build complex systems from simple rules
- Each rule has one job

---

## Level 7: The Three Operations

### Division (Proportional Check)
```tinytalk
when resource_check
  and f / g < 0.8
fin within_budget
```
"Using less than 80% of limit"

### Subtraction (Difference Check)
```tinytalk
when resource_check
  and g - f > 10
fin buffer_available
```
"At least 10 units remaining"

### Multiply by Zero (Emergency Stop)
```tinytalk
when system_check
  and active * threat_level = 0
fin system_safe
```
"If threat detected, everything stops"

---

## Common Patterns

### Pattern: Permission Gate
```tinytalk
when action
  and authenticated
  and authorized
  and not_blocked
fin allowed
```

### Pattern: Resource Limit
```tinytalk
when consume_resource
  and current < limit
  and remaining > 0
fin consumption_ok
```

### Pattern: Time Window
```tinytalk
when scheduled_action
  and current_time >= start_time
  and current_time <= end_time
fin in_window
```

### Pattern: Cascading Checks
```tinytalk
rule basic_check
  when request
    and valid_input
  fin basic_ok

rule auth_check
  when basic_ok
    and user_valid
  fin auth_ok

rule final_check
  when auth_ok
    and permission_ok
  fin approved
```

---

## Anti-Patterns (What NOT to Do)

### Anti-Pattern: Contradicting Conditions
```tinytalk
# BAD - can never be true
when action
  and is_admin
  and not_admin
fin impossible
```

### Anti-Pattern: Redundant Checks
```tinytalk
# BAD - second check is redundant
when action
  and count > 10
  and count > 5
fin redundant
```

### Anti-Pattern: Missing Negative
```tinytalk
# BAD - forgot to check if banned
when post
  and user_verified
  # Should also check: and not_banned
fin risky
```

---

## Assessment Rubric

### Level 1-2: Basic Syntax
- [ ] Uses `when...fin` correctly
- [ ] Indents `and` conditions
- [ ] Rules make logical sense

### Level 3-4: Logic
- [ ] Uses `not_` appropriately
- [ ] Comparisons are correct
- [ ] No contradictions

### Level 5-6: Structure
- [ ] Variables clearly defined
- [ ] Rules work together
- [ ] No redundancy

### Level 7: Advanced
- [ ] Chooses correct operation (/, -, ×0)
- [ ] Understands performance implications
- [ ] Can optimize existing rules

---

## Project Progression

### Week 1-2: Login System
- Single condition auth
- Add password check
- Add account status
- Add rate limiting

### Week 3-4: Social Media Rules
- Post permissions
- Comment moderation
- User blocking
- Content filtering

### Week 5-6: Game Engine
- Player actions
- Resource limits
- Turn management
- Win conditions

### Week 7-8: Final Project
- Student choice
- Real-world application
- Presentation
