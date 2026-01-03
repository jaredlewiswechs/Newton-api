# Setting Up Gumroad for Newton Supercomputer

**January 3, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Welcome to selling Newton access! This guide will walk you through everything as a first-time business owner.

## What is Gumroad?

Gumroad is a simple platform for selling digital products. They handle:
- Payment processing (credit cards, PayPal)
- License key generation
- Customer emails
- Refunds and disputes
- Tax collection (if needed)

**Cost**: Gumroad takes 10% + $0.50 per sale. So for a $5 sale, you keep ~$4.00.

---

## Step 1: Create Your Gumroad Account

1. Go to [gumroad.com](https://gumroad.com) and click "Start selling"
2. Sign up with your email
3. Verify your email address
4. Connect a payment method (bank account or PayPal) to receive payouts

---

## Step 2: Create Your Newton Product

1. Click "New Product" in your dashboard
2. Fill in:
   - **Name**: `Newton Supercomputer Access`
   - **Price**: `$5` (you can change this later)
   - **Description**: See sample below

### Sample Product Description

```
Access to the Newton Verified Computation Supercomputer

Newton is a constraint-based computation engine where:
- The constraint IS the instruction
- The verification IS the computation
- Every calculation is proven before execution

What you get:
- Full API access to Newton
- Verified computation engine (Turing complete, bounded)
- Constraint evaluation (CDL 3.0)
- Content safety verification (Forge)
- Encrypted storage (Vault)
- Immutable audit trail (Ledger)
- Education module (TEKS-aligned lesson planning)
- Interface Builder for verified UIs

How it works:
1. Purchase to receive your license key
2. Verify your license at: POST /license/verify
3. Get your API key
4. Use your API key in X-API-Key header for all requests

During beta - $5 one-time payment
Full documentation at: https://your-docs-url.com
```

3. Under "More options":
   - Enable "Generate a unique license key"
   - This is critical - customers need license keys!

4. Click "Publish"

---

## Step 3: Get Your API Credentials

### Get Your Product ID

1. Go to your product page
2. Look at the URL: `gumroad.com/l/XXXXX`
3. The `XXXXX` part is your product ID

### Get Your Access Token

1. Go to [Gumroad Settings > Advanced](https://app.gumroad.com/settings/advanced)
2. Scroll to "Applications"
3. Click "Create Application"
4. Fill in:
   - Name: `Newton API`
   - Redirect URI: `https://your-domain.com/callback` (or localhost for testing)
5. Copy the "Access Token" that appears

---

## Step 4: Set Up Webhooks (Optional but Recommended)

Webhooks notify your server when someone buys, gets a refund, etc.

1. Go to your product settings
2. Find "Ping" or "Webhooks" section
3. Add your webhook URL: `https://your-domain.com/webhooks/gumroad`
4. (Optional) Set a webhook secret for security

---

## Step 5: Configure Newton

Create a `.env` file in your Newton directory:

```bash
# Copy the example
cp .env.example .env

# Edit with your values
nano .env
```

Add your credentials:

```
GUMROAD_PRODUCT_ID=your_product_id_here
GUMROAD_ACCESS_TOKEN=your_access_token_here
GUMROAD_WEBHOOK_SECRET=your_webhook_secret_here
```

---

## Step 6: Test It!

### Test License Verification

For development, you can use test license keys that start with `TEST_`:

```bash
curl -X POST http://localhost:8000/license/verify \
  -H "Content-Type: application/json" \
  -d '{"license_key": "TEST_abc123"}'
```

### Make a Real Test Purchase

1. Go to your Gumroad product page
2. Buy your own product (you can refund yourself later)
3. Get the license key from your email
4. Test verification:

```bash
curl -X POST http://localhost:8000/license/verify \
  -H "Content-Type: application/json" \
  -d '{"license_key": "YOUR_REAL_LICENSE_KEY"}'
```

---

## How Customers Use Newton

1. Customer visits your Gumroad page
2. Pays $5
3. Receives license key via email
4. Verifies license:
   ```
   POST /license/verify
   {"license_key": "THEIR_LICENSE_KEY"}
   ```
5. Gets their API key in response
6. Uses API key in all requests:
   ```
   curl -X POST https://your-api.com/ask \
     -H "X-API-Key: newton_xxxxx" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is 2+2?"}'
   ```

---

## Collecting Feedback

Customers can send feedback anytime:

```bash
curl -X POST https://your-api.com/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "message": "This is amazing!",
    "rating": 5,
    "category": "praise"
  }'
```

View feedback summary:
```bash
curl https://your-api.com/feedback/summary
```

---

## New API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/license/info` | GET | Pricing info & how to buy |
| `/license/verify` | POST | Verify license, get API key |
| `/webhooks/gumroad` | POST | Webhook receiver (Gumroad calls this) |
| `/feedback` | POST | Submit feedback |
| `/feedback/summary` | GET | View all feedback |
| `/gumroad/stats` | GET | Sales & verification stats |

---

## First-Time Business Owner Tips

### Taxes
- Gumroad can collect sales tax for you (enable in settings)
- Keep records of all sales for tax purposes
- Consider consulting a tax professional

### Customer Service
- Respond to customer emails promptly
- Be generous with refunds during testing
- Use feedback to improve

### Pricing
- $5 is a great testing price
- You can raise it later as you add features
- Consider offering discounts for early supporters

### Growing
- Share on Twitter/X, Reddit, Hacker News
- Write blog posts about what Newton does
- Collect testimonials from happy customers

---

## Troubleshooting

### "Invalid license key"
- Check GUMROAD_PRODUCT_ID is correct
- Check GUMROAD_ACCESS_TOKEN is valid
- Make sure customer has a real Gumroad purchase

### Webhooks not working
- Verify your webhook URL is publicly accessible
- Check webhook secret matches in both places
- Look at server logs for errors

### Can't verify test licenses
- Test licenses (TEST_xxx) only work when Gumroad credentials aren't set
- For production, use real Gumroad licenses

---

## Need Help?

- Check `/docs` for API documentation
- Submit feedback via `/feedback` endpoint
- Open an issue on GitHub

---

© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company · Houston, Texas

Good luck with your business!
