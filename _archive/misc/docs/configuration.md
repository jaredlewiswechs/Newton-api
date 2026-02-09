# Configuration

**January 6, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Newton OS is configured through environment variables.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEWTON_AUTH_ENABLED` | Enable API key authentication | `false` |
| `NEWTON_ENTERPRISE_KEY` | Enterprise API key | None |
| `NEWTON_API_KEYS` | JSON object of custom API keys | `{}` |
| `NEWTON_LEDGER_PATH` | Path to persistent ledger file | `.newton_ledger.json` |

---

## Authentication

### Disable Authentication (Development)

```bash
# Authentication is disabled by default
export NEWTON_AUTH_ENABLED=false
```

All requests are allowed with a default rate limit of 100 requests/minute.

### Enable Authentication (Production)

```bash
export NEWTON_AUTH_ENABLED=true
```

When enabled, all requests must include a valid `X-API-Key` header.

---

## API Keys

### Enterprise Key

Set a single enterprise-tier API key:

```bash
export NEWTON_ENTERPRISE_KEY=your-secret-key-here
```

This key automatically gets:
- `tier`: enterprise
- `rate_limit`: 10,000 requests/minute

### Custom API Keys

Configure multiple API keys with custom tiers and rate limits:

```bash
export NEWTON_API_KEYS='{
  "client-a-key": {
    "owner": "Client A",
    "tier": "pro",
    "rate_limit": 1000
  },
  "client-b-key": {
    "owner": "Client B",
    "tier": "free",
    "rate_limit": 60
  },
  "internal-key": {
    "owner": "Internal Service",
    "tier": "enterprise",
    "rate_limit": 10000
  }
}'
```

### API Key Structure

| Field | Type | Description |
|-------|------|-------------|
| `owner` | string | Identifier for the key owner |
| `tier` | string | `free`, `pro`, or `enterprise` |
| `rate_limit` | int | Requests per minute |

### Default Public Key

Newton includes a default public demo key:

```json
{
  "newton-public-demo": {
    "owner": "public",
    "tier": "free",
    "rate_limit": 60
  }
}
```

---

## Rate Limiting

### Rate Limit Tiers

| Tier | Default Rate Limit |
|------|-------------------|
| Free | 60/minute |
| Pro | 1,000/minute |
| Enterprise | 10,000/minute |

### Rate Limit Window

Rate limits are enforced on a rolling 60-second window.

### Rate Limit Response

When exceeded:

```json
{
  "detail": "Rate limit exceeded. Max 60 requests per minute."
}
```

HTTP Status: `429 Too Many Requests`

---

## Ledger Configuration

### Default Path

```bash
# Current directory
export NEWTON_LEDGER_PATH=.newton_ledger.json
```

### Production Path

```bash
# Dedicated directory
export NEWTON_LEDGER_PATH=/var/newton/ledger.json
```

### Maximum Entries

The ledger is limited to 10,000 entries. When exceeded:
- Oldest entries are rotated out
- Chain integrity is maintained

---

## Server Configuration

### Host and Port

The server runs on:
- Host: `0.0.0.0` (all interfaces)
- Port: `8000`

To change the port, modify `newton_os_server.py`:

```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### CORS

CORS is enabled by default for all origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, restrict to your domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)
```

---

## Example Configurations

### Development

```bash
# No authentication, local ledger
export NEWTON_AUTH_ENABLED=false
python newton_os_server.py
```

### Production (Simple)

```bash
export NEWTON_AUTH_ENABLED=true
export NEWTON_ENTERPRISE_KEY=my-secret-production-key
export NEWTON_LEDGER_PATH=/var/newton/ledger.json
python newton_os_server.py
```

### Production (Multi-tenant)

```bash
export NEWTON_AUTH_ENABLED=true
export NEWTON_API_KEYS='{
  "client-a": {"owner": "Client A Inc", "tier": "pro", "rate_limit": 1000},
  "client-b": {"owner": "Client B LLC", "tier": "pro", "rate_limit": 1000},
  "internal": {"owner": "Internal Services", "tier": "enterprise", "rate_limit": 10000}
}'
export NEWTON_LEDGER_PATH=/var/newton/ledger.json
python newton_os_server.py
```

### Docker

```bash
docker run -p 8000:8000 \
  -e NEWTON_AUTH_ENABLED=true \
  -e NEWTON_ENTERPRISE_KEY=my-docker-secret \
  -e NEWTON_LEDGER_PATH=/data/ledger.json \
  -v newton-data:/data \
  newton-os
```

---

## Configuration Best Practices

1. **Never commit secrets** - Use environment variables or secrets management
2. **Enable auth in production** - Always set `NEWTON_AUTH_ENABLED=true`
3. **Use strong API keys** - Generate cryptographically random keys
4. **Persist the ledger** - Use a durable storage location
5. **Monitor rate limits** - Track usage to adjust limits as needed
6. **Restrict CORS** - In production, limit allowed origins
