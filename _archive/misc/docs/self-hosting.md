# Self-Hosting Guide

**January 6, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Deploy Newton OS on your own infrastructure.

## Requirements

- Python 3.8+
- pip package manager
- 512MB RAM minimum
- Network access (for claim grounding)

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python newton_os_server.py
```

Server runs at `http://localhost:8000`

---

## Docker Deployment

### Build Image

```bash
docker build -t newton-os .
```

### Run Container

```bash
docker run -p 8000:8000 newton-os
```

### With Environment Variables

```bash
docker run -p 8000:8000 \
  -e NEWTON_AUTH_ENABLED=true \
  -e NEWTON_ENTERPRISE_KEY=your-secret-key \
  -e NEWTON_LEDGER_PATH=/data/ledger.json \
  -v /path/to/data:/data \
  newton-os
```

### Docker Compose

```yaml
version: '3.8'
services:
  newton:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NEWTON_AUTH_ENABLED=true
      - NEWTON_ENTERPRISE_KEY=${NEWTON_ENTERPRISE_KEY}
      - NEWTON_LEDGER_PATH=/data/ledger.json
    volumes:
      - newton-data:/data
    restart: unless-stopped

volumes:
  newton-data:
```

---

## Render Deployment

### 1. Fork the Repository

Fork [Newton-api](https://github.com/jaredlewiswechs/Newton-api) to your GitHub account.

### 2. Create Web Service

1. Log in to [Render.com](https://render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Select your forked repository

### 3. Configure Settings

| Setting | Value |
|---------|-------|
| Name | newton-os |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python newton_os_server.py` |
| Plan | Starter or higher |

### 4. Set Environment Variables

In the Render dashboard, add:

| Variable | Value |
|----------|-------|
| `NEWTON_AUTH_ENABLED` | `true` |
| `NEWTON_ENTERPRISE_KEY` | Your secret key |
| `NEWTON_LEDGER_PATH` | `/opt/render/project/src/ledger.json` |

### 5. Deploy

Click **Create Web Service**. Render will build and deploy automatically.

---

## Production Configuration

### Enable Authentication

```bash
export NEWTON_AUTH_ENABLED=true
```

### Configure API Keys

#### Single Enterprise Key

```bash
export NEWTON_ENTERPRISE_KEY=your-secret-enterprise-key
```

#### Multiple API Keys

```bash
export NEWTON_API_KEYS='{
  "key-abc123": {"owner": "client-a", "tier": "pro", "rate_limit": 1000},
  "key-def456": {"owner": "client-b", "tier": "free", "rate_limit": 60}
}'
```

### Persistent Ledger

```bash
export NEWTON_LEDGER_PATH=/var/newton/ledger.json
```

Ensure the directory exists and is writable.

---

## Nginx Reverse Proxy

### Configuration

```nginx
upstream newton {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://newton;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### With SSL (Let's Encrypt)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://newton;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Systemd Service

### Create Service File

```bash
sudo nano /etc/systemd/system/newton.service
```

```ini
[Unit]
Description=Newton OS API Server
After=network.target

[Service]
Type=simple
User=newton
WorkingDirectory=/opt/newton
Environment=NEWTON_AUTH_ENABLED=true
Environment=NEWTON_LEDGER_PATH=/var/newton/ledger.json
ExecStart=/usr/bin/python3 newton_os_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable newton
sudo systemctl start newton
```

### Check Status

```bash
sudo systemctl status newton
```

---

## Health Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

### Example Response

```json
{
  "status": "ok",
  "version": "3.0.0",
  "engine": "Newton OS 3.0.0",
  "timestamp": 1735689600
}
```

### Monitoring with curl

```bash
# Simple health check
curl -sf http://localhost:8000/health > /dev/null && echo "OK" || echo "FAIL"
```

### Integration with Uptime Monitoring

Use services like:
- UptimeRobot
- Pingdom
- Better Uptime

Point them at your `/health` endpoint.

---

## Scaling

### Horizontal Scaling

Run multiple Newton instances behind a load balancer:

```
                    ┌─────────────┐
                    │   Load      │
    Requests ──────▶│  Balancer   │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐
      │ Newton 1 │  │ Newton 2 │  │ Newton 3 │
      └──────────┘  └──────────┘  └──────────┘
```

### Shared Ledger

For horizontal scaling with shared audit trail, configure a shared ledger path:

```bash
# All instances write to the same path
export NEWTON_LEDGER_PATH=/shared/storage/ledger.json
```

Note: For high-volume deployments, consider migrating to a database-backed ledger.

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Permission Denied (Ledger)

```bash
# Create directory and set permissions
sudo mkdir -p /var/newton
sudo chown $(whoami) /var/newton
```

### Module Not Found

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Google Search Issues (Grounding)

If claim grounding returns "Search unavailable":

1. Check network connectivity
2. The `googlesearch-python` library may be rate-limited
3. Consider using the hosted API for grounding
