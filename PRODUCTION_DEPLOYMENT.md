# Production HTTPS Deployment Guide

## Quick Start

This guide helps you deploy the Incident Handler with HTTPS using Docker Compose.

## Prerequisites

- Domain name pointing to your server
- Linux server with Docker and Docker Compose installed
- Ports 80 and 443 open on firewall

---

## Step 1: Update Configuration

### 1.1 Edit nginx.conf

Replace `_` with your actual domain name:

```bash
nano nginx.conf
```

Change:
```nginx
server_name _;
```

To:
```nginx
server_name incidents.yourdomain.com;
```

Do this in **both** server blocks (HTTP and HTTPS).

### 1.2 Verify .env file

Ensure your `.env` file has all required variables:

```bash
cat .env
```

Should contain:
```env
SN_url=https://your-instance.service-now.com
SN_username=your_username
SN_password=your_password
ASSIGNMENT_GROUP_SYS_ID=your_group_id

PG_HOST=postgres
PG_PORT=5432
PG_DB=incident_automation
PG_USER=incident_bot
PG_PASSWORD=Kashmir2025$
```

---

## Step 2: Get SSL Certificates

### Option A: Using Let's Encrypt (Recommended - Free)

```bash
# Create certs directory
mkdir -p certs

# Install Certbot
sudo apt update
sudo apt install certbot -y

# Get certificate (standalone mode)
sudo certbot certonly --standalone \
  -d your-domain.com \
  --agree-tos \
  --email your-email@example.com

# Copy certificates to project
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem certs/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem certs/
sudo chmod 644 certs/*.pem
```

### Option B: Self-Signed Certificate (Testing Only)

```bash
# Create certs directory
mkdir -p certs

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/privkey.pem \
  -out certs/fullchain.pem \
  -subj "/CN=your-domain.com"
```

---

## Step 3: Deploy with Docker Compose

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

Expected output:
```
NAME                      STATUS          PORTS
incident_handler_app      Up 30 seconds   
incident_handler_db       Up 30 seconds   
incident_handler_nginx    Up 30 seconds   0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

---

## Step 4: Open Firewall Ports

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verify
sudo ufw status
```

---

## Step 5: Access Your Application

Open browser and navigate to:
```
https://your-domain.com
```

You should see:
- ✅ HTTPS padlock in browser
- ✅ Dashboard loads successfully
- ✅ No certificate warnings (if using Let's Encrypt)

---

## Certificate Renewal (Let's Encrypt)

Certificates expire every 90 days. Set up auto-renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
sudo crontab -e
```

Add this line:
```cron
0 0 * * * certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/*.pem /path/to/Incident_Handler/certs/ && docker-compose -f /path/to/Incident_Handler/docker-compose.prod.yml restart nginx
```

---

## Common Commands

```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Stop services
docker-compose -f docker-compose.prod.yml down

# Restart services
docker-compose -f docker-compose.prod.yml restart

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Check Nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

---

## Troubleshooting

### Certificate Errors

```bash
# Check certificate files exist
ls -la certs/

# Verify certificate
openssl x509 -in certs/fullchain.pem -text -noout

# Check Nginx logs
docker-compose -f docker-compose.prod.yml logs nginx
```

### Can't Access HTTPS

```bash
# Check if ports are open
sudo ufw status

# Test from server
curl -k https://localhost

# Check DNS
nslookup your-domain.com
```

### WebSocket Issues

```bash
# Check Nginx config
docker-compose -f docker-compose.prod.yml exec nginx cat /etc/nginx/conf.d/default.conf

# Test WebSocket
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" https://your-domain.com/ws
```

---

## Security Checklist

- ✅ Using HTTPS with valid SSL certificate
- ✅ HTTP automatically redirects to HTTPS
- ✅ Security headers enabled (HSTS, X-Frame-Options, etc.)
- ✅ Strong SSL ciphers configured
- ✅ Firewall configured (only ports 80, 443 open)
- ✅ Environment variables in `.env` (not hardcoded)
- ✅ Database password changed from default

---

## File Structure

After setup, your directory should look like:

```
Incident_Handler/
├── docker-compose.prod.yml    # Production Docker Compose
├── nginx.conf                  # Nginx configuration
├── certs/                      # SSL certificates
│   ├── fullchain.pem
│   └── privkey.pem
├── .env                        # Environment variables
├── Dockerfile
└── ... (other application files)
```

---

## Success Criteria

✅ Application accessible at `https://your-domain.com`  
✅ HTTPS padlock shows in browser  
✅ HTTP redirects to HTTPS  
✅ WebSocket connection works  
✅ Database connected (not in-memory mode)  
✅ No certificate warnings  

---

**You're all set! Your application is now running securely with HTTPS.** 🔒🚀
