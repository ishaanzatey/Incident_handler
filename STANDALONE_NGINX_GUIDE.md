# Standalone Nginx Deployment Guide

## 🎯 Overview

This setup installs **Nginx directly on your Ubuntu server** (not in Docker) and uses it as a reverse proxy to your Docker containers.

### Architecture

```
Browser
   ↓
Nginx (Ubuntu Server - Port 443)
   ↓
Docker App Container (localhost:8000)
   ↓
PostgreSQL Container
```

**Benefits:**
- ✅ Better performance (Nginx runs natively)
- ✅ Easier SSL certificate management
- ✅ Standard production setup
- ✅ Can use Let's Encrypt easily
- ✅ Nginx manages multiple apps on same server

---

## 🚀 Quick Deployment

### One-Command Deployment

```bash
sudo ./deploy-standalone-nginx.sh
```

This script will:
1. Install Nginx on Ubuntu (if not installed)
2. Deploy Docker containers (app + database)
3. Configure Nginx as reverse proxy
4. Set up SSL certificates
5. Configure firewall

---

## 📋 Manual Deployment Steps

If you prefer manual deployment:

### Step 1: Deploy Docker Containers

```bash
# Start Docker containers (app exposed on localhost:8000)
docker-compose -f docker-compose.prod.yml up -d --build

# Verify containers are running
docker-compose -f docker-compose.prod.yml ps

# Test app is accessible locally
curl http://localhost:8000/api/health
```

### Step 2: Install Nginx

```bash
# Update package list
sudo apt update

# Install Nginx
sudo apt install -y nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx

# Start Nginx
sudo systemctl start nginx
```

### Step 3: Create SSL Certificates

**Option A: Self-Signed (Testing)**

```bash
# Create SSL directory
sudo mkdir -p /etc/nginx/ssl/incident-handler

# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/incident-handler/privkey.pem \
  -out /etc/nginx/ssl/incident-handler/fullchain.pem \
  -subj "/CN=$(hostname -I | awk '{print $1}')"

# Set permissions
sudo chmod 600 /etc/nginx/ssl/incident-handler/*.pem
```

**Option B: Let's Encrypt (Production with Domain)**

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com

# Certbot will automatically configure Nginx
```

### Step 4: Configure Nginx

```bash
# Copy Nginx configuration
sudo cp nginx-standalone.conf /etc/nginx/sites-available/incident-handler

# Create symlink to enable site
sudo ln -s /etc/nginx/sites-available/incident-handler /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 5: Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verify firewall rules
sudo ufw status
```

### Step 6: Verify Deployment

```bash
# Test Docker app
curl http://localhost:8000/api/health

# Test Nginx proxy
curl -k https://localhost/api/health

# Check Nginx status
sudo systemctl status nginx

# Check Docker containers
docker-compose -f docker-compose.prod.yml ps
```

---

## 🔍 Configuration Details

### Docker Compose Changes

The app container is now exposed on `localhost:8000`:

```yaml
app:
  ports:
    - "127.0.0.1:8000:8000"  # Only accessible from localhost
```

**Why `127.0.0.1`?**
- Only accessible from the same server (Nginx)
- Not accessible from outside
- More secure

### Nginx Configuration

Nginx proxies requests to `http://127.0.0.1:8000`:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    # ... proxy headers
}
```

---

## 🛠️ Management Commands

### Nginx Commands

```bash
# Start Nginx
sudo systemctl start nginx

# Stop Nginx
sudo systemctl stop nginx

# Restart Nginx
sudo systemctl restart nginx

# Reload configuration (no downtime)
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# View logs
sudo tail -f /var/log/nginx/incident-handler-error.log
sudo tail -f /var/log/nginx/incident-handler-access.log
```

### Docker Commands

```bash
# Start containers
docker-compose -f docker-compose.prod.yml up -d

# Stop containers
docker-compose -f docker-compose.prod.yml down

# Restart containers
docker-compose -f docker-compose.prod.yml restart

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🆘 Troubleshooting

### Can't Access from Browser

```bash
# Check Nginx is running
sudo systemctl status nginx

# Check firewall
sudo ufw status

# Check Nginx logs
sudo tail -f /var/log/nginx/incident-handler-error.log

# Test Nginx configuration
sudo nginx -t
```

### Nginx Can't Connect to Docker App

```bash
# Verify Docker app is running
docker-compose -f docker-compose.prod.yml ps

# Test Docker app directly
curl http://localhost:8000/api/health

# Check Docker logs
docker-compose -f docker-compose.prod.yml logs app

# Verify port binding
netstat -tlnp | grep 8000
```

### SSL Certificate Issues

```bash
# Check certificate files exist
sudo ls -la /etc/nginx/ssl/incident-handler/

# Verify certificate
sudo openssl x509 -in /etc/nginx/ssl/incident-handler/fullchain.pem -text -noout

# Check Nginx SSL configuration
sudo nginx -t
```

### Port Already in Use

```bash
# Check what's using port 80/443
sudo netstat -tlnp | grep -E ':80|:443'

# Stop conflicting service
sudo systemctl stop apache2  # If Apache is running
```

---

## 🔄 Updating the Application

```bash
# 1. Pull latest code
cd Incident_Handler
git pull  # or transfer new files

# 2. Rebuild Docker containers
docker-compose -f docker-compose.prod.yml up -d --build

# 3. Nginx doesn't need restart (unless config changed)
# If you updated nginx-standalone.conf:
sudo cp nginx-standalone.conf /etc/nginx/sites-available/incident-handler
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📊 Monitoring

### Check Service Status

```bash
# Nginx
sudo systemctl status nginx

# Docker containers
docker-compose -f docker-compose.prod.yml ps

# View all logs
sudo tail -f /var/log/nginx/incident-handler-access.log &
docker-compose -f docker-compose.prod.yml logs -f
```

### Health Checks

```bash
# Check Nginx
curl -I https://localhost

# Check Docker app
curl http://localhost:8000/api/health

# Check through Nginx proxy
curl -k https://localhost/api/health
```

---

## ✅ Success Criteria

After deployment, verify:

- [ ] Nginx is running: `sudo systemctl status nginx`
- [ ] Docker containers running: `docker-compose -f docker-compose.prod.yml ps`
- [ ] App accessible locally: `curl http://localhost:8000/api/health`
- [ ] Nginx proxy works: `curl -k https://localhost/api/health`
- [ ] Accessible from browser: `https://YOUR_SERVER_IP`
- [ ] HTTP redirects to HTTPS
- [ ] WebSocket connections work

---

## 🎯 Summary

**Files:**
- `docker-compose.prod.yml` - Docker containers (app on localhost:8000)
- `nginx-standalone.conf` - Nginx configuration
- `deploy-standalone-nginx.sh` - Automated deployment

**Quick Deploy:**
```bash
sudo ./deploy-standalone-nginx.sh
```

**Access:**
```
https://YOUR_SERVER_IP
```

**This is the recommended production setup!** 🚀
