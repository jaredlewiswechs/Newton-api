# Authentication

**January 3, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Newton uses API key authentication to secure endpoints and enforce rate limits.

## API Key Header

Include your API key in the `X-API-Key` header:

```bash
curl -X POST https://api.parcri.net/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"input": "Your text here"}'
```

## Rate Limits

Rate limits are enforced per API key on a per-minute basis.

| Tier       | Requests/Minute | Requests/Month |
|------------|-----------------|----------------|
| Free       | 60              | 1,000          |
| Pro        | 1,000           | 500,000        |
| Enterprise | 10,000          | Unlimited      |

## Rate Limit Response

When you exceed your rate limit:

```json
{
  "detail": "Rate limit exceeded. Max 60 requests per minute."
}
```

HTTP Status: `429 Too Many Requests`

## Missing API Key

When authentication is enabled and no API key is provided:

```json
{
  "detail": "Missing API key. Include X-API-Key header."
}
```

HTTP Status: `401 Unauthorized`

## Invalid API Key

When an invalid API key is provided:

```json
{
  "detail": "Invalid API key"
}
```

HTTP Status: `403 Forbidden`

---

## Self-Hosted Configuration

### Enable Authentication

By default, authentication is disabled for development. Enable it with:

```bash
export NEWTON_AUTH_ENABLED=true
```

### Configure API Keys

#### Enterprise Key

Set a single enterprise API key:

```bash
export NEWTON_ENTERPRISE_KEY=your-secret-enterprise-key
```

#### Custom API Keys

Configure multiple API keys with tiers and rate limits:

```bash
export NEWTON_API_KEYS='{
  "key-1": {"owner": "user1", "tier": "pro", "rate_limit": 1000},
  "key-2": {"owner": "user2", "tier": "free", "rate_limit": 60}
}'
```

### API Key Format

Each API key configuration includes:

| Field | Description |
|-------|-------------|
| `owner` | Identifier for the key owner |
| `tier` | `free`, `pro`, or `enterprise` |
| `rate_limit` | Requests per minute |

---

## Development Mode

For local development, authentication is disabled by default. All requests are treated as:

```json
{
  "owner": "anonymous",
  "tier": "free",
  "rate_limit": 100
}
```

To enable authentication in development:

```bash
NEWTON_AUTH_ENABLED=true python newton_os_server.py
```

---

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Rotate keys regularly** - Especially for production
3. **Use HTTPS** - Always use encrypted connections
4. **Monitor usage** - Watch for unusual patterns
5. **Use appropriate tiers** - Match rate limits to your needs

---

## Getting an API Key

### Hosted API

1. Sign up at [parcri.net](https://parcri.net)
2. Navigate to your dashboard
3. Generate a new API key

### Self-Hosted

Configure keys using environment variables as described above.
