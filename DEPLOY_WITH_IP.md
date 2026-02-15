# Production Deployment Guide - Nginx Reverse Proxy

## 🎯 Architecture

```
Browser
   ↓
Nginx (Port 443 HTTPS / Port 80 HTTP)
   ↓
Application Container (Port 8000 - INTERNAL ONLY)
   ↓
PostgreSQL Container
```

**Key Point:** The application is **NOT directly accessible**. You can ONLY access it through Nginx.

---

## 🚀 Quick Deployment

### One-Command Deployment

```bash
./deploy-production.sh
```

The script will:
1. Detect your server IP
2. Ask about SSL certificates (use existing or generate self-signed)
3. Configure firewall
4. Start all services
5. Verify deployment

---

## 🔐 SSL Certificate Options

### Option 1: Use Your Own Certificates (Recommended for Production)

If you have SSL certificates (from Let's Encrypt, commercial CA, etc.):

```bash
# Place your certificates in the certs directory
mkdir -p certs
cp /path/to/your/fullchain.pem certs/
cp /path/to/your/privkey.pem certs/

# Run deployment
./deploy-production.sh
# Choose option 1 when asked
```

### Option 2: Self-Signed Certificate (Testing Only)

For testing without a domain:

```bash
# Run deployment
./deploy-production.sh
# Choose option 2 when asked
```

The script will generate a self-signed certificate automatically.

---

## 📋 Pre-Deployment Checklist

- [ ] `.env` file configured with ServiceNow credentials
- [ ] Docker and Docker Compose installed
- [ ] Ports 80 and 443 available
- [ ] SSL certificates ready (if using option 1)

---

## 🌐 Accessing Your Application

After deployment:

**HTTPS (Main):**
```
https://YOUR_SERVER_IP
```

**HTTP (Redirects to HTTPS):**
```
http://YOUR_SERVER_IP
```

**Examples:**
- `https://192.168.1.100`
- `https://10.0.0.50`

---

## ⚠️ Important Notes

### 1. Application is NOT Directly Accessible

The application container does NOT expose port 8000 to the host. You **cannot** access:
- ❌ `http://YOUR_SERVER_IP:8000`
- ❌ Direct container access

You **must** access through Nginx:
- ✅ `https://YOUR_SERVER_IP` (port 443)
- ✅ `http://YOUR_SERVER_IP` (port 80, redirects to 443)

### 2. Self-Signed Certificate Warning

If using self-signed certificates, browsers will show a security warning. This is normal.

**To proceed:**
- Chrome/Edge: Click "Advanced" → "Proceed to [IP] (unsafe)"
- Firefox: Click "Advanced" → "Accept the Risk and Continue"

---

## 🔧 Manual Deployment

If you prefer manual deployment:

### Step 1: Prepare SSL Certificates

**Option A: Use existing certificates**
```bash
mkdir -p certs
cp /path/to/fullchain.pem certs/
cp /path/to/privkey.pem certs/
```

**Option B: Generate self-signed**
```bash
mkdir -p certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/privkey.pem \
  -out certs/fullchain.pem \
  -subj "/CN=$(hostname -I | awk '{print $1}')"
```

### Step 2: Configure Firewall

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Step 3: Deploy

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Step 4: Verify

```bash
docker-compose -f docker-compose.prod.yml ps
curl -k https://localhost/api/health
```

---

## 🛠️ Common Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f app

# Stop services
docker-compose -f docker-compose.prod.yml down

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Check Nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

---

## 🔍 Verification

### Check Services are Running

```bash
docker-compose -f docker-compose.prod.yml ps
```

Expected output:
```
NAME                      STATUS
incident_handler_app      Up
incident_handler_db       Up
incident_handler_nginx    Up
```

### Test HTTPS Access

```bash
# From server
curl -k https://localhost

# Check health endpoint
curl -k https://localhost/api/health
```

### Verify App is NOT Directly Accessible

```bash
# This should FAIL (connection refused)
curl http://localhost:8000
```

This confirms the app is only accessible through Nginx.

---

## 🆘 Troubleshooting

### Can't Access from Browser

```bash
# Check firewall
sudo ufw status

# Verify Nginx is running
docker-compose -f docker-compose.prod.yml ps nginx

# Check Nginx logs
docker-compose -f docker-compose.prod.yml logs nginx
```

### SSL Certificate Errors

```bash
# Verify certificates exist
ls -la certs/

# Check certificate details
openssl x509 -in certs/fullchain.pem -text -noout

# Restart Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Application Not Responding

```bash
# Check app logs
docker-compose -f docker-compose.prod.yml logs app

# Verify app is healthy
docker-compose -f docker-compose.prod.yml exec app python -c "import requests; print(requests.get('http://localhost:8000/api/health').json())"

# Check database connection
docker-compose -f docker-compose.prod.yml logs postgres
```

---

## 📁 File Structure

```
Incident_Handler/
├── docker-compose.prod.yml    # Production config (app NOT exposed)
├── nginx.conf                  # Nginx reverse proxy config
├── deploy-production.sh        # Automated deployment script
├── certs/                      # SSL certificates directory
│   ├── fullchain.pem          # SSL certificate
│   └── privkey.pem            # Private key
├── .env                        # Environment variables
└── ... (other files)
```

---

## ✅ Success Criteria

After deployment, verify:

- ✅ Can access `https://YOUR_SERVER_IP` in browser
- ✅ HTTP redirects to HTTPS
- ✅ Dashboard loads successfully
- ✅ Connection status shows "Connected"
- ✅ Database mode shows "postgres"
- ✅ Cannot access `http://YOUR_SERVER_IP:8000` (app not exposed)
- ✅ All services running: `docker-compose -f docker-compose.prod.yml ps`

---

## 🔒 Security Features

- ✅ Application not directly exposed (only through Nginx)
- ✅ HTTPS encryption
- ✅ HTTP to HTTPS redirect
- ✅ Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- ✅ Modern SSL/TLS configuration
- ✅ WebSocket support for real-time updates
- ✅ Network isolation (backend network)

---

**Ready to deploy! Just run `./deploy-production.sh` and follow the prompts.** 🚀
