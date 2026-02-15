# Configuration Files Alignment Guide

This document explains all configuration files and how they work together.

---

## 📁 File Overview

### Development Files (Local Testing)
- `docker-compose.yml` - Development setup with direct port access
- `.env` - Environment variables (same for dev and prod)

### Production Files (Linux Server)
- `docker-compose.prod.yml` - Production with Nginx reverse proxy
- `nginx.conf` - Nginx reverse proxy configuration
- `deploy-production.sh` - Automated deployment script

### Application Files
- `Dockerfile` - Container image definition
- `run_dashboard.py` - Application entry point
- `api_server.py` - FastAPI server
- `config.py` - Configuration loader

---

## 🔄 How Files Work Together

### Development Setup (Local)

```
docker-compose.yml
    ↓
  Reads .env
    ↓
  Builds Dockerfile
    ↓
  Runs run_dashboard.py
    ↓
  Starts api_server.py on port 8000
    ↓
  Access: http://localhost:8000
```

### Production Setup (Linux Server)

```
docker-compose.prod.yml
    ↓
  Reads .env
    ↓
  Builds Dockerfile
    ↓
  Runs run_dashboard.py (port 8000 internal)
    ↓
  Nginx (nginx.conf) proxies to app:8000
    ↓
  Access: https://SERVER_IP (port 443)
```

---

## 📝 File Details

### 1. `.env` (Environment Variables)

**Purpose:** Store credentials and configuration
**Used by:** Both development and production

```env
# ServiceNow - UPDATE WITH YOUR CREDENTIALS
SN_url=https://service-now.com
SN_username=int_servicenow
SN_password=Coeadmin
ASSIGNMENT_GROUP_SYS_ID=3Dc797091a40d9e110

# Database - KEEP AS-IS
PG_HOST=postgres
PG_PORT=5432
PG_DB=incident_automation
PG_USER=incident_bot
PG_PASSWORD=Kashmir2025$
```

**✅ No changes needed** - Works for both dev and prod

---

### 2. `docker-compose.yml` (Development)

**Purpose:** Local development with direct access
**When to use:** Testing on your local machine

**Key Features:**
- ✅ App exposed on port 8000 (direct access)
- ✅ Database exposed on port 5432
- ✅ No Nginx (simpler for development)

**Access:**
```
http://localhost:8000
```

**✅ No changes needed** - Keep for local development

---

### 3. `docker-compose.prod.yml` (Production)

**Purpose:** Production deployment with Nginx
**When to use:** Deploying to Linux server

**Key Differences from dev:**
- ❌ App NOT exposed (no ports section)
- ✅ Nginx container added (ports 80, 443)
- ✅ App only accessible through Nginx

**Access:**
```
https://SERVER_IP
```

**Network:**
```
Browser → Nginx (443) → App (8000 internal) → PostgreSQL
```

**✅ Already configured** - Ready to use

---

### 4. `nginx.conf` (Nginx Configuration)

**Purpose:** Reverse proxy configuration
**Used by:** Production only (docker-compose.prod.yml)

**What it does:**
- Listens on ports 80 (HTTP) and 443 (HTTPS)
- Redirects HTTP to HTTPS
- Proxies requests to `app:8000` (internal)
- Handles WebSocket connections
- Adds security headers

**Key Configuration:**
```nginx
location / {
    proxy_pass http://app:8000;  # Internal Docker network
}
```

**✅ Already configured** - Ready to use

---

### 5. `Dockerfile` (Container Image)

**Purpose:** Defines how to build the application container
**Used by:** Both development and production

**What it does:**
- Uses Python 3.13
- Installs dependencies
- Copies application code
- Exposes port 8000
- Runs `run_dashboard.py`

**✅ No changes needed** - Works for both

---

### 6. `deploy-production.sh` (Deployment Script)

**Purpose:** Automated production deployment
**When to use:** Deploying to Linux server

**What it does:**
1. Detects server IP
2. Asks about SSL certificates
3. Configures firewall
4. Runs `docker-compose.prod.yml`
5. Verifies deployment

**Usage:**
```bash
./deploy-production.sh
```

**✅ Already configured** - Ready to use

---

## 🎯 Deployment Scenarios

### Scenario 1: Local Development

**Files used:**
- `docker-compose.yml`
- `.env`
- `Dockerfile`

**Commands:**
```bash
docker-compose up -d
```

**Access:**
```
http://localhost:8000
```

---

### Scenario 2: Production (Linux Server)

**Files used:**
- `docker-compose.prod.yml`
- `nginx.conf`
- `.env`
- `Dockerfile`
- `deploy-production.sh`

**Commands:**
```bash
./deploy-production.sh
```

**Access:**
```
https://SERVER_IP
```

---

## 🔍 Configuration Alignment

### Port Configuration

| Component | Development | Production |
|-----------|-------------|------------|
| App | 8000 (exposed) | 8000 (internal only) |
| Nginx | N/A | 80, 443 (exposed) |
| PostgreSQL | 5432 (exposed) | 5432 (internal only) |

### Network Configuration

| Setup | Network Type | Access |
|-------|--------------|--------|
| Development | Bridge | Direct to app:8000 |
| Production | Bridge | Through Nginx only |

### Environment Variables

| Variable | Development | Production |
|----------|-------------|------------|
| PG_HOST | postgres | postgres |
| PG_PORT | 5432 | 5432 |
| SN_url | From .env | From .env |
| All others | From .env | From .env |

**✅ Same .env file works for both!**

---

## 📋 Checklist: What You Need to Update

### Before Development
- [ ] Update `.env` with ServiceNow credentials
- [ ] Run `docker-compose up -d`

### Before Production Deployment
- [ ] Update `.env` with ServiceNow credentials (same file)
- [ ] Transfer entire folder to Linux server
- [ ] Run `./deploy-production.sh`
- [ ] Choose SSL certificate option

**That's it! No other changes needed.**

---

## 🚫 What NOT to Change

### Don't change these in `.env`:
- ❌ `PG_HOST=postgres` (must be "postgres" for Docker)
- ❌ `PG_PORT=5432`
- ❌ `PG_DB=incident_automation`
- ❌ `PG_USER=incident_bot`

### Don't change these files:
- ❌ `Dockerfile` - Works for both dev and prod
- ❌ `docker-compose.yml` - Keep for local development
- ❌ `nginx.conf` - Already configured for any IP

---

## 🔄 File Relationships

```
.env (credentials)
  ↓
  ├─→ docker-compose.yml (development)
  │     ↓
  │   Dockerfile → run_dashboard.py → api_server.py
  │     ↓
  │   Access: http://localhost:8000
  │
  └─→ docker-compose.prod.yml (production)
        ↓
      Dockerfile → run_dashboard.py → api_server.py
        ↓
      nginx.conf (reverse proxy)
        ↓
      Access: https://SERVER_IP
```

---

## ✅ Summary

### Files That Work As-Is (No Changes)
1. ✅ `.env` - Just update ServiceNow credentials
2. ✅ `docker-compose.yml` - For development
3. ✅ `docker-compose.prod.yml` - For production
4. ✅ `nginx.conf` - For production
5. ✅ `Dockerfile` - For both
6. ✅ `deploy-production.sh` - For production

### What You Need to Do
1. Update `.env` with your ServiceNow credentials
2. For development: `docker-compose up -d`
3. For production: `./deploy-production.sh`

**Everything is aligned and ready to use!** 🚀
