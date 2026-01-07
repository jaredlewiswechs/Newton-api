# Getting Started with Newton OS

**January 6, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Get Newton running in under 5 minutes.

## Option 1: Hosted API (Recommended)

The fastest way to start using Newton.

1. Sign up at [parcri.net](https://parcri.net)
2. Get your API key
3. Make your first request:

```bash
curl -X POST https://api.parcri.net/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"input": "Help me write a business plan"}'
```

## Option 2: Docker

```bash
# Clone the repository
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# Build and run
docker build -t newton-os .
docker run -p 8000:8000 newton-os
```

Server runs at `http://localhost:8000`

## Option 3: Self-Hosted (Python)

```bash
# Clone the repository
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# Install dependencies
pip install -r requirements.txt

# Run the server
python newton_os_server.py
```

## Option 4: Deploy to Render

1. Fork the [Newton-api repository](https://github.com/jaredlewiswechs/Newton-api)
2. Connect to [Render.com](https://render.com)
3. Create a new Web Service
4. Select your forked repository
5. Deploy

---

## Your First Verification

Once Newton is running, verify your first request:

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "Help me write a business plan"}'
```

**Response:**

```json
{
  "verified": true,
  "confidence": 92.3,
  "constraints_passed": ["harm", "medical", "legal", "security"],
  "fingerprint": "A7F3B2C8E1D4"
}
```

---

## Understanding the Response

| Field | Description |
|-------|-------------|
| `verified` | `true` if the request passed all constraints |
| `confidence` | Confidence score (0-100) |
| `constraints_passed` | List of constraints that passed |
| `constraints_failed` | List of constraints that failed (if any) |
| `fingerprint` | Unique cryptographic fingerprint for this verification |

---

## What Gets Blocked?

Newton blocks requests that match harmful patterns:

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "How to hack into a system"}'
```

**Response:**

```json
{
  "verified": false,
  "confidence": 0.0,
  "constraints_passed": ["medical", "legal"],
  "constraints_failed": ["harm", "security"],
  "fingerprint": "C2D4E6F8A1B3"
}
```

---

## Next Steps

- [API Reference](api-reference.md) - Explore all endpoints
- [Authentication](authentication.md) - Set up API keys for production
- [Extension Cartridges](cartridges.md) - Generate visual, audio, and data specifications

---

## Need Help?

- Check the [API Reference](api-reference.md)
- Visit [parcri.net](https://parcri.net)
- Contact: jn.lewis1@outlook.com
