# Deployment Guide

This document explains how to deploy the Telegraph project to production and development environments.

## Local Development

### Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

This starts:
- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:8080

Press `Ctrl+C` to stop all services.

### Manual Setup

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
python -m backend.app

# Terminal 2: Frontend
cd realtime-morse-frontend
npm install
npm run dev
```

## Production Deployment

### Using Docker (Recommended)

1. **Build images**:
```bash
docker build -t telegraph-backend ./backend
docker build -t telegraph-frontend ./realtime-morse-frontend
```

2. **Run containers**:
```bash
docker run -d -p 5000:5000 telegraph-backend
docker run -d -p 8080:8080 telegraph-frontend
```

### Using Heroku

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create telegraph-decoder

# Deploy backend
git subtree push --prefix backend heroku main

# Deploy frontend
git subtree push --prefix realtime-morse-frontend heroku main
```

### Using AWS

1. **Backend (Elastic Beanstalk)**:
```bash
# Install EB CLI
pip install --upgrade awsebcli

# Initialize
eb init -p python-3.10 telegraph-backend

# Create environment
eb create telegraph-backend-env

# Deploy
eb deploy
```

2. **Frontend (Amplify/S3 + CloudFront)**:
```bash
# Build frontend
cd realtime-morse-frontend
npm run build

# Deploy to S3
aws s3 sync dist/ s3://telegraph-frontend-bucket/

# Invalidate CloudFront
aws cloudfront create-invalidation --distribution-id <ID> --paths "/*"
```

### Using Railway

```bash
# Create project on railway.app
# Link repository
# Set environment variables:
#   - VITE_API_URL=https://your-backend.railway.app/api
# Deploy!
```

## Environment Variables

### Backend (.env)

```
FLASK_ENV=production
DEBUG=False
API_PORT=5000
CORS_ORIGINS=https://your-frontend.com
```

### Frontend (.env)

```
VITE_API_URL=https://your-backend.com/api
```

## Scaling Considerations

### Horizontal Scaling

- **Backend**: Stateless Flask app, can run multiple instances behind a load balancer
  - Use Gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
  - Add Redis for caching (optional)
  - Use PostgreSQL for persistent model storage

- **Frontend**: Static assets, served via CDN
  - Build: `npm run build`
  - Serve from S3 + CloudFront, Azure Blob Storage, or Netlify

### Database Layer

For multi-user support, consider:
```sql
-- Store calibrated models per user
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255),
  email VARCHAR(255),
  model_path VARCHAR(255)
);

-- Store message history
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  input_mode VARCHAR(20),
  input_text TEXT,
  decoded_text TEXT,
  timestamp TIMESTAMP
);
```

### Performance Optimization

1. **Backend**:
   - Use async views with `async def`
   - Cache Morse dictionary in memory
   - Pre-load ML model on startup
   - Use connection pooling for database

2. **Frontend**:
   - Code splitting for components
   - Lazy load audio/video features
   - Service worker for offline support
   - Compress assets

## Monitoring & Logging

### Backend Logging

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Model trained with accuracy: 0.94")
```

### Frontend Error Tracking

```typescript
// Add Sentry for error tracking
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: "production",
});
```

### Monitoring

- **Backend**: Prometheus + Grafana
- **Frontend**: Datadog Real User Monitoring (RUM)
- **Uptime**: Pingdom or UptimeRobot

## Backup & Recovery

```bash
# Backup ML model
cp tap_model.pkl tap_model.pkl.backup

# Backup database (if using PostgreSQL)
pg_dump telegraph_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Troubleshooting

### Port Already in Use

```bash
# macOS/Linux
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### CORS Issues

Ensure `flask-cors` is installed and backend has correct `CORS_ORIGINS` set.

### Frontend Not Loading API

Check:
1. `VITE_API_URL` in `.env` matches backend URL
2. Backend is running and accessible
3. Browser DevTools Network tab for failed requests

## Maintenance

- Monitor error logs weekly
- Update dependencies monthly
- Retrain ML model quarterly (if new data available)
- Test disaster recovery procedures quarterly

## Support

See [INTEGRATION.md](../INTEGRATION.md) for more details on the architecture.
