# README - Incident Handler

## 🎯 Quick Start

### Development (Local Testing)
```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Update ServiceNow credentials

# 2. Start application
docker-compose up -d

# 3. Access
http://localhost:8000
```

### Production (Linux Server)
```bash
# 1. Transfer files to server
scp -r Incident_Handler user@server:/home/user/

# 2. SSH and deploy
ssh user@server
cd Incident_Handler
./deploy-production.sh

# 3. Access
https://YOUR_SERVER_IP
```

---

## 📁 Project Structure

```
Incident_Handler/
├── Configuration Files
│   ├── .env                      # Environment variables (update ServiceNow credentials)
│   ├── docker-compose.yml        # Development setup (direct access)
│   ├── docker-compose.prod.yml   # Production setup (Nginx reverse proxy)
│   └── nginx.conf                # Nginx configuration (production only)
│
├── Application Code
│   ├── main.py                   # Core automation logic
│   ├── api_server.py             # FastAPI server
│   ├── run_dashboard.py          # Application entry point
│   ├── database_manager.py       # Database operations
│   ├── servicenow_client.py      # ServiceNow integration
│   └── event_emitter.py          # WebSocket events
│
├── Frontend
│   ├── frontend/index.html       # Dashboard UI
│   ├── frontend/app.js           # Frontend logic
│   └── frontend/styles.css       # Styling
│
├── Deployment
│   ├── Dockerfile                # Container image
│   ├── deploy-production.sh      # Automated deployment
│   └── requirements.txt          # Python dependencies
│
└── Documentation
    ├── README.md                 # This file
    ├── CONFIGURATION_GUIDE.md    # Configuration alignment guide
    ├── QUICK_START.md            # Quick reference
    ├── DEPLOY_WITH_IP.md         # Production deployment guide
    └── HTTPS_SETUP.md            # HTTPS configuration
```

---

## 🔧 Configuration

### Environment Variables (.env)

**Update these:**
- `SN_url` - Your ServiceNow instance URL
- `SN_username` - ServiceNow username
- `SN_password` - ServiceNow password
- `ASSIGNMENT_GROUP_SYS_ID` - Assignment group ID

**Don't change these:**
- `PG_HOST=postgres` (required for Docker)
- `PG_PORT=5432`
- `PG_DB=incident_automation`
- `PG_USER=incident_bot`
- `PG_PASSWORD` (can change if needed)

---

## 🚀 Deployment Options

### Option 1: Development (Local)

**Purpose:** Testing on your local machine

**Setup:**
```bash
docker-compose up -d
```

**Access:**
```
http://localhost:8000
```

**Architecture:**
```
Browser → App (port 8000) → PostgreSQL
```

---

### Option 2: Production (Linux Server)

**Purpose:** Production deployment with HTTPS

**Setup:**
```bash
./deploy-production.sh
```

**Access:**
```
https://YOUR_SERVER_IP
```

**Architecture:**
```
Browser → Nginx (port 443) → App (internal) → PostgreSQL
```

**Key Difference:** App is NOT directly accessible, only through Nginx.

---

## 📊 Features

- ✅ Real-time incident monitoring
- ✅ Automated incident processing
- ✅ ServiceNow integration
- ✅ PostgreSQL database with fallback to in-memory
- ✅ WebSocket for live updates
- ✅ HTTPS support with Nginx reverse proxy
- ✅ Docker containerization
- ✅ Health monitoring and error handling

---

## 🔒 Security

### Development
- HTTP only (localhost)
- Direct port access

### Production
- HTTPS with SSL certificates
- Nginx reverse proxy
- Application not directly exposed
- Security headers
- Network isolation

---

## 📋 Common Commands

### Development
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build
```

### Production
```bash
# Start
docker-compose -f docker-compose.prod.yml up -d

# Stop
docker-compose -f docker-compose.prod.yml down

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Rebuild
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🆘 Troubleshooting

### Can't access application

**Development:**
```bash
# Check services
docker-compose ps

# Check logs
docker-compose logs app
```

**Production:**
```bash
# Check services
docker-compose -f docker-compose.prod.yml ps

# Check Nginx logs
docker-compose -f docker-compose.prod.yml logs nginx

# Check app logs
docker-compose -f docker-compose.prod.yml logs app
```

### Database connection failed

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify .env settings
cat .env
```

### SSL certificate issues (Production)

```bash
# Verify certificates exist
ls -la certs/

# Check Nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

---

## 📚 Documentation

- **CONFIGURATION_GUIDE.md** - Complete configuration alignment guide
- **QUICK_START.md** - Quick reference for deployment
- **DEPLOY_WITH_IP.md** - Production deployment with IP address
- **HTTPS_SETUP.md** - HTTPS configuration options

---

## 🎯 Next Steps

1. **Configure:** Update `.env` with your ServiceNow credentials
2. **Test Locally:** Run `docker-compose up -d`
3. **Deploy to Production:** Run `./deploy-production.sh` on Linux server

---

## 📞 Support

For detailed guides, see the documentation files in the project root.

---

**Ready to deploy!** 🚀
