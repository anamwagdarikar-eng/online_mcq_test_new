# 🚀 Deployment Guide

This guide covers deploying the MCQ Test System to production environments.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Database Migration](#database-migration)
5. [SSL/TLS Setup](#ssltls-setup)
6. [Performance Optimization](#performance-optimization)
7. [Monitoring & Logging](#monitoring--logging)

---

## Local Development

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip, virtualenv

### Setup Steps

1. **Create Virtual Environment**
```bash
cd d:\online_mcq_test
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup Environment Variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Initialize Database**
```bash
python init_db.py
```

5. **Seed Sample Data (Optional)**
```bash
python seed_data.py
```

6. **Run Application**
```bash
streamlit run main.py
```

Access at: `http://localhost:8501`

---

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Quick Start with Docker Compose

```bash
# Navigate to project directory
cd d:\online_mcq_test

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f app

# Initialize database
docker-compose exec app python init_db.py

# Seed sample data
docker-compose exec app python seed_data.py

# Stop services
docker-compose down
```

### Access Points
- **Application**: http://localhost:8501
- **pgAdmin**: http://localhost:5050
  - Email: admin@college.edu
  - Password: pgAdmin123!

### Manual Docker Build

```bash
# Build image
docker build -t mcq-test:latest .

# Run container with PostgreSQL
docker run -d \
  --name mcq-app \
  -p 8501:8501 \
  --env-file .env \
  mcq-test:latest
```

---

## Cloud Deployment

### Heroku Deployment

1. **Install Heroku CLI**
```bash
# Windows: choco install heroku
# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Create Procfile**
```
web: streamlit run main.py --logger.level=error --client.showErrorDetails=false
```

3. **Create requirements file (if not exists)**
```bash
pip freeze > requirements.txt
```

4. **Initialize Heroku**
```bash
heroku login
heroku create mcq-test-system
```

5. **Add PostgreSQL Add-on**
```bash
heroku addons:create heroku-postgresql:standard-0
```

6. **Set Environment Variables**
```bash
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set COLLEGE_NAME="Your College Name"
heroku config:set ENABLE_HTTPS="True"
```

7. **Deploy**
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

8. **Initialize Database**
```bash
heroku run python init_db.py
```

9. **View Application**
```bash
heroku open
```

### Railway.app Deployment

1. **Connect GitHub Repository**
   - Go to railway.app
   - Create new project
   - Select "Deploy from GitHub"
   - Select this repository

2. **Add PostgreSQL Database**
   - In Railway console
   - Add service → PostgreSQL
   - Connect to application

3. **Set Environment Variables**
   - In Railway console → Variables
   - Add: `DATABASE_URL`, `SECRET_KEY`, etc.

4. **Deploy**
   - Push to GitHub
   - Railway auto-deploys

### AWS Deployment (ECS)

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name mcq-test
```

2. **Build and Push Image**
```bash
docker build -t mcq-test:latest .
docker tag mcq-test:latest {aws_account_id}.dkr.ecr.{region}.amazonaws.com/mcq-test:latest
docker push {aws_account_id}.dkr.ecr.{region}.amazonaws.com/mcq-test:latest
```

3. **Create RDS PostgreSQL Database**
```bash
aws rds create-db-instance \
  --db-instance-identifier mcq-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --allocated-storage 20
```

4. **Deploy with ECS/Fargate**
   - Use AWS CloudFormation/CDK
   - Configure task definition
   - Set environment variables
   - Deploy

### DigitalOcean App Platform

1. **Connect Repository**
   - DigitalOcean App Platform
   - Create new app
   - Select GitHub repository

2. **Configure**
   - Set build command: `pip install -r requirements.txt`
   - Set run command: `streamlit run main.py`
   - Add PostgreSQL database

3. **Deploy**
   - Set environment variables
   - Deploy

---

## Database Migration

### PostgreSQL Backup

```bash
# Backup database
pg_dump -h localhost -U mcq_user -d mcq_db > backup.sql

# Restore database
psql -h localhost -U mcq_user -d mcq_db < backup.sql
```

### NeonDB Connection

```bash
# In .env
NEON_CONNECTION_STRING=postgresql://user:password@ep-xxx.neon.tech/mcq_db

# Test connection
psql "postgresql://user:password@ep-xxx.neon.tech/mcq_db"

# Run migrations
python init_db.py
```

---

## SSL/TLS Setup

### Using Let's Encrypt with Nginx

1. **Install Certbot**
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. **Get Certificate**
```bash
sudo certbot certonly --nginx -d your-domain.com
```

3. **Configure Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **Auto-renewal**
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Performance Optimization

### Database Optimization

1. **Connection Pooling**
```python
# Install pgbouncer
sudo apt-get install pgbouncer

# Configure /etc/pgbouncer/pgbouncer.ini
[databases]
mcq_db = host=localhost dbname=mcq_db

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

2. **Query Optimization**
- Ensure all indexes are created (done by init_db.py)
- Use EXPLAIN ANALYZE for slow queries
- Archive old test attempts

### Caching

1. **Redis Integration**
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

2. **Session Caching**
```python
# Add to utils/session_cache.py
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)

# Cache sessions
cache.set(f"session:{token}", user_id, ex=3600)
```

### Load Balancing

```nginx
upstream mcq_backend {
    server localhost:8501;
    server localhost:8502;
    server localhost:8503;
    least_conn;
}

server {
    location / {
        proxy_pass http://mcq_backend;
    }
}
```

---

## Monitoring & Logging

### Logging Setup

1. **Rotate Logs**
```bash
# /etc/logrotate.d/mcq-test
/var/log/mcq-test/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0600 www-data www-data
    sharedscripts
}
```

2. **Centralized Logging** (ELK Stack)
```yaml
# docker-compose with ELK
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  
  logstash:
    image: docker.elastic.co/logstash/logstash:8.0.0
  
  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
```

### Health Checks

```bash
# Health check endpoint
curl http://localhost:8501/_stcore/health

# Database health
curl http://localhost:8501/api/health

# Uptime monitoring
ping -c 1 http://your-domain.com
```

### Monitoring Tools

1. **Prometheus + Grafana**
```bash
docker run -d --name prometheus prom/prometheus
docker run -d --name grafana grafana/grafana
```

2. **Application Performance Monitoring**
   - New Relic
   - DataDog
   - Sentry (for error tracking)

---

## Security Checklist

- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Setup firewall rules
- [ ] Regular database backups
- [ ] Update dependencies regularly
- [ ] Enable audit logging
- [ ] Setup VPN for admin access
- [ ] Configure rate limiting
- [ ] Setup DDoS protection
- [ ] Enable 2FA for admin users

---

## Troubleshooting Deployment

### Database Connection Issues
```bash
# Test connection
psql "postgresql://user:password@host/db"

# Check if PostgreSQL is running
systemctl status postgresql

# Restart PostgreSQL
systemctl restart postgresql
```

### Streamlit Port Conflicts
```bash
# Check if port 8501 is in use
lsof -i :8501

# Use different port
streamlit run main.py --server.port 8502
```

### Memory Issues
```bash
# Check memory usage
free -h
docker stats

# Increase swap if needed
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in /path/to/cert.pem -text -noout

# Renew certificate
certbot renew --force-renewal
```

---

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Test database connectivity
4. Review firewall rules
5. Check application status

---

**Last Updated**: 2024
**Version**: 1.0.0
