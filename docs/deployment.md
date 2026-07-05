# Deployment Guide

This guide covers deploying OmniForge in various environments.

## Local Development

### Manual Setup

```bash
# Clone and install
git clone https://github.com/lanekingkong/omniforge.git
cd omniforge
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Start CLI
omniforge version
```

### IDE Integration

**VS Code:**
1. Open project folder
2. Install Python extension
3. Select virtual environment
4. Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY omniforge/ omniforge/
COPY cli.py .

# Install package
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m omniforge
USER omniforge

EXPOSE 8520

CMD ["omniforge", "dashboard"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  omniforge:
    build: .
    ports:
      - "8520:8520"
    volumes:
      - ./data:/home/omniforge/.omniforge
      - ./projects:/home/omniforge/projects
    environment:
      - OMNIFORGE_CONFIG=/home/omniforge/.omniforge/config.yaml
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8520/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### Build and Run

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Check logs
docker-compose logs -f omniforge

# Stop
docker-compose down
```

## Cloud Deployment

### AWS EC2

```bash
# Launch EC2 instance (Amazon Linux 2)
ssh -i key.pem ec2-user@instance-ip

# Install Python and Git
sudo yum update -y
sudo yum install python3.11 git -y

# Clone and setup
git clone https://github.com/lanekingkong/omniforge.git
cd omniforge
python3.11 -m venv venv
source venv/bin/activate
pip install -e .

# Start dashboard
omniforge dashboard --host 0.0.0.0 --port 8520
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/omniforge

# Deploy
gcloud run deploy omniforge \
    --image gcr.io/PROJECT_ID/omniforge \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8520
```

### Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway login
railway init
railway up
```

## Production Configuration

### config.yaml

```yaml
omniforge:
  environment: production
  log_level: INFO
  data_dir: /var/lib/omniforge

server:
  host: 0.0.0.0
  port: 8520
  workers: 4
  timeout: 300

security:
  cors_origins:
    - "https://yourdomain.com"
  jwt_secret: "${JWT_SECRET}"
  session_timeout: 3600

database:
  type: postgresql
  url: "${DATABASE_URL}"
  pool_size: 20

cache:
  type: redis
  url: "${REDIS_URL}"
  ttl: 3600

integrations:
  github:
    enabled: true
    token: "${GITHUB_TOKEN}"
  notion:
    enabled: false
  slack:
    enabled: false

monitoring:
  enabled: true
  prometheus_port: 9090
  health_check_interval: 30
```

### Environment Variables

```bash
# Required
OMNIFORGE_CONFIG=/etc/omniforge/config.yaml
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET=your-jwt-secret

# Optional
GITHUB_TOKEN=ghp_xxxxx
NOTION_TOKEN=secret_xxxxx
OPENAI_API_KEY=sk-xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Monitoring
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
DATADOG_API_KEY=xxxxx
```

## Performance Tuning

### Optimization Tips

1. **Use Redis cache** for frequently accessed data
2. **Increase worker count** for high-traffic scenarios
3. **Enable response compression** (gzip/brotli)
4. **Use connection pooling** for database
5. **Profile slow operations** with built-in profiler
6. **Pre-warm the knowledge graph** for faster retrieval
7. **Configure rate limits** appropriately

### Resource Recommendations

| Scale | CPU | RAM | Storage | Workers |
|-------|-----|-----|---------|---------|
| Personal | 2 vCPU | 4 GB | 20 GB | 2 |
| Small Team | 4 vCPU | 8 GB | 50 GB | 4 |
| Enterprise | 8+ vCPU | 16+ GB | 200+ GB | 8+ |

## Monitoring

### Health Endpoint

```
GET /health
Response: {"status": "healthy", "uptime": 86400, "version": "1.0.0"}
```

### Metrics Endpoint

```
GET /metrics
Response: Prometheus-formatted metrics
```

### Logging

```python
import logging
from omniforge import OmniForge

forge = OmniForge(
    project_name="production",
    config={
        "log_level": "INFO",
        "log_format": "json",
        "log_file": "/var/log/omniforge/app.log"
    }
)
```

## Backup and Recovery

### Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/backups/omniforge"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
pg_dump omniforge > "$BACKUP_DIR/db_$DATE.sql"

# Backup config and data
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" \
    /var/lib/omniforge \
    /etc/omniforge

# Clean old backups
find "$BACKUP_DIR" -mtime +30 -delete
```

### Recovery

```bash
# Restore database
psql omniforge < backup.sql

# Restore data
tar -xzf data_backup.tar.gz -C /
```

## Security Checklist

- [ ] Use HTTPS in production (reverse proxy with nginx)
- [ ] Set strong JWT secret
- [ ] Restrict CORS origins
- [ ] Enable rate limiting
- [ ] Run regular security scans (`omniforge security`)
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets
- [ ] Enable audit logging
- [ ] Regular backups configured
- [ ] Health monitoring alerts set up

## Troubleshooting

### Common Issues

**Dashboard won't start:**
```bash
# Check port availability
netstat -an | findstr 8520

# Try different port
omniforge dashboard --port 8521
```

**Slow performance:**
```bash
# Enable profiling
omniforge profile my_project

# Check resource usage
omniforge dashboard --metrics
```

**Integration failures:**
```bash
# Test individual integration
omniforge test-integration github

# Check token validity
omniforge validate-tokens
```