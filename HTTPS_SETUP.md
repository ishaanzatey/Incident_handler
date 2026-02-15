# HTTPS Setup Guide for Incident Handler

This guide shows you how to enable HTTPS for your Incident Handler application.

## Prerequisites

- Domain name pointing to your server (e.g., `incidents.yourdomain.com`)
- Linux server with Docker and Docker Compose installed
- Ports 80 and 443 open on firewall

## Option 1: Using Nginx Reverse Proxy with Let's Encrypt (Recommended)

This is the easiest and most secure method using free SSL certificates.

### Step 1: Install Nginx and Certbot

```bash
# Update package list
sudo apt update

# Install Nginx
sudo apt install nginx -y

# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
```

### Step 2: Configure Nginx

Create Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/incident-handler
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your actual domain

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 3: Enable the Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/incident-handler /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Step 4: Get SSL Certificate

```bash
# Obtain and install SSL certificate
sudo certbot --nginx -d your-domain.com

# Follow the prompts:
# - Enter your email
# - Agree to terms
# - Choose to redirect HTTP to HTTPS (option 2)
```

Certbot will automatically:
- Get a free SSL certificate
- Configure Nginx for HTTPS
- Set up auto-renewal

### Step 5: Open Firewall Ports

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# You can now close port 8000 (optional)
sudo ufw delete allow 8000/tcp
```

### Step 6: Access Your Application

Your application is now available at:
```
https://your-domain.com
```

### Step 7: Auto-Renewal

Certbot automatically renews certificates. Test renewal:

```bash
sudo certbot renew --dry-run
```

---

## Option 2: Using Docker Compose with Nginx Container

This method keeps everything in Docker.

### Step 1: Create Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream incident_handler {
        server dashboard:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://incident_handler;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws {
            proxy_pass http://incident_handler;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### Step 2: Update docker-compose.yml

Add Nginx service:

```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: incident_handler_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - dashboard
    networks:
      - incident_network

  dashboard:
    # ... existing configuration ...
    # Remove the ports section or change to:
    expose:
      - "8000"
```

### Step 3: Generate SSL Certificate

For production, use Let's Encrypt. For testing, create self-signed:

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate self-signed certificate (for testing only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/CN=your-domain.com"
```

### Step 4: Deploy

```bash
docker-compose down
docker-compose up -d
```

---

## Option 3: Using Traefik (Advanced)

Traefik automatically handles SSL certificates with Let's Encrypt.

### docker-compose.yml with Traefik

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    container_name: traefik
    restart: unless-stopped
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=your-email@example.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-ssl:/letsencrypt
    networks:
      - incident_network

  dashboard:
    # ... existing configuration ...
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.dashboard.entrypoints=websecure"
      - "traefik.http.routers.dashboard.tls.certresolver=myresolver"
      - "traefik.http.services.dashboard.loadbalancer.server.port=8000"

volumes:
  traefik-ssl:
```

---

## Recommendation

**For most users:** Use **Option 1** (Nginx + Certbot)
- ✅ Easiest to set up
- ✅ Free SSL certificates
- ✅ Auto-renewal
- ✅ Well documented
- ✅ Industry standard

## Testing HTTPS

After setup, test your HTTPS configuration:

```bash
# Test SSL certificate
curl -I https://your-domain.com

# Check SSL rating
# Visit: https://www.ssllabs.com/ssltest/
```

## Troubleshooting

### Certificate Not Working

```bash
# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Verify certificate
sudo certbot certificates
```

### WebSocket Issues

Ensure Nginx has WebSocket support in the `/ws` location block.

### Mixed Content Warnings

Update your application to use relative URLs instead of hardcoded `http://`.

---

## Summary

1. **Get a domain name** pointing to your server
2. **Install Nginx and Certbot** on your Linux server
3. **Configure Nginx** as reverse proxy
4. **Run Certbot** to get SSL certificate
5. **Access via HTTPS** at `https://your-domain.com`

Your application will now be secure with HTTPS! 🔒
