# Incident Handler - Quick Deployment Guide

## Prerequisites

- Linux server with Docker and Docker Compose installed
- SSH access to the server
- Domain name (optional, for HTTPS)

---

## HTTP Deployment (Quick Start)

### 1. Transfer Files to Server

```bash
# From your local machine
scp -r /path/to/Incident_Handler user@server-ip:/home/user/
```

### 2. Configure Environment

SSH into server and edit `.env`:

```bash
cd ~/Incident_Handler
nano .env
```

Verify these settings:
```env
# ServiceNow (update with your credentials)
SN_url=https://your-instance.service-now.com
SN_username=your_username
SN_password=your_password
ASSIGNMENT_GROUP_SYS_ID=your_group_id

# Database (keep as-is for Docker)
PG_HOST=postgres
PG_PORT=5432
PG_DB=incident_automation
PG_USER=incident_bot
PG_PASSWORD=Kashmir2025$
```

### 3. Deploy

```bash
# Start application
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Open Firewall

```bash
sudo ufw allow 8000/tcp
```

### 5. Access Application

Open browser: `http://YOUR_SERVER_IP:8000`

---

## HTTPS Deployment (Production)

### Prerequisites
- Domain name pointing to your server
- Ports 80 and 443 open

### 1. Install Nginx and Certbot

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y
```

### 2. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/incident-handler
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/incident-handler /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Get SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com
```

Follow prompts and choose to redirect HTTP to HTTPS.

### 5. Open Firewall

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 6. Access Application

Open browser: `https://your-domain.com`

---

## Common Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Update application
docker-compose down
docker-compose up -d --build
```

---

## Troubleshooting

### Can't access from browser
- Check firewall: `sudo ufw status`
- Verify Docker is running: `docker-compose ps`
- Check if port is listening: `netstat -tlnp | grep 8000`

### Database connection failed
- Check logs: `docker-compose logs postgres`
- Verify `.env` settings
- Restart: `docker-compose restart`

### SSL certificate issues
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- Verify domain DNS: `nslookup your-domain.com`
- Renew certificate: `sudo certbot renew`

---

## Support

For detailed documentation, see:
- `HTTPS_SETUP.md` - Complete HTTPS configuration guide
- `LINUX_DEPLOYMENT_CHECKLIST.md` - Detailed deployment steps
