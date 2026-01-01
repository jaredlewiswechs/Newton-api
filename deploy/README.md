# Newton Supercomputer Deployment

Deployment configurations for Newton Supercomputer.

## Quick Start

### Local Development

```bash
cd Newton-api
pip install -r requirements.txt
python newton_supercomputer.py
```

Server runs at `http://localhost:8000`

### Docker

```bash
# Build and run
docker build -t newton-supercomputer .
docker run -p 8000:8000 newton-supercomputer

# Or with docker-compose (includes persistent storage)
docker-compose -f deploy/docker-compose.yml up -d
```

### Render.com

1. Fork the repository
2. Connect to Render.com
3. Create new Web Service from repo
4. Render will auto-detect `render.yaml`

Or use the Deploy button:
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Server port |
| `NEWTON_STORAGE` | /tmp/newton | Storage directory |
| `NEWTON_AUTH_ENABLED` | false | Enable API key authentication |
| `NEWTON_API_KEYS` | - | Comma-separated API keys |
| `PYTHONPATH` | - | Python module path |
| `PYTHONUNBUFFERED` | 1 | Disable output buffering |

### Files

| File | Purpose |
|------|---------|
| `../Dockerfile` | Container build configuration |
| `../render.yaml` | Render.com deployment |
| `docker-compose.yml` | Docker Compose with volumes |

## Health Check

All deployments should verify the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "operational",
  "version": "1.0.0",
  "glass_box": {
    "policy_engine": "active",
    "negotiator": "active",
    "merkle_scheduler": "active"
  }
}
```

## Production Considerations

1. **Enable Authentication**: Set `NEWTON_AUTH_ENABLED=true` and provide API keys
2. **Persistent Storage**: Use volumes for ledger and vault data
3. **HTTPS**: Always use HTTPS in production (Render.com provides this automatically)
4. **Monitoring**: Monitor `/metrics` endpoint for performance data
5. **Backups**: Regular backup of `/data/newton` and `/app/ledger` directories

---

© 2025-2026 Ada Computing Company · Houston, Texas
