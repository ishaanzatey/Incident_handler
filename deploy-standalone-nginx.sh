#!/bin/bash

# Standalone Nginx + Docker Deployment Script
# This script:
# 1. Installs Nginx on Ubuntu server (if not installed)
# 2. Deploys Docker containers (app + database)
# 3. Configures Nginx as reverse proxy to Docker app

set -e

echo "=============================================="
echo "  Incident Handler - Standalone Nginx Setup"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ This script must be run as root or with sudo${NC}"
    echo "Please run: sudo ./deploy-standalone-nginx.sh"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${BLUE}📋 System Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
echo -e "${GREEN}✓${NC} Server IP: ${YELLOW}$SERVER_IP${NC}"
echo ""

# Step 1: Install Nginx
echo -e "${BLUE}📦 Step 1: Installing Nginx${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v nginx &> /dev/null; then
    echo -e "${GREEN}✓${NC} Nginx already installed"
else
    echo -e "${YELLOW}Installing Nginx...${NC}"
    apt update
    apt install -y nginx
    systemctl enable nginx
    echo -e "${GREEN}✓${NC} Nginx installed"
fi
echo ""

# Step 2: SSL Certificate Setup
echo -e "${BLUE}🔐 Step 2: SSL Certificate Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Choose SSL certificate option:"
echo "  1) Use existing certificates"
echo "  2) Generate self-signed certificate"
echo ""
read -p "Enter choice (1 or 2): " SSL_CHOICE

# Create SSL directory
mkdir -p /etc/nginx/ssl/incident-handler

if [ "$SSL_CHOICE" = "1" ]; then
    echo ""
    echo "Please provide paths to your SSL certificates:"
    read -p "Full path to certificate file (fullchain.pem): " CERT_PATH
    read -p "Full path to private key file (privkey.pem): " KEY_PATH
    
    if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
        echo -e "${RED}❌ Certificate files not found${NC}"
        exit 1
    fi
    
    cp "$CERT_PATH" /etc/nginx/ssl/incident-handler/fullchain.pem
    cp "$KEY_PATH" /etc/nginx/ssl/incident-handler/privkey.pem
    chmod 600 /etc/nginx/ssl/incident-handler/*.pem
    echo -e "${GREEN}✓${NC} Certificates copied"
    
elif [ "$SSL_CHOICE" = "2" ]; then
    echo -e "${YELLOW}Generating self-signed certificate...${NC}"
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/incident-handler/privkey.pem \
        -out /etc/nginx/ssl/incident-handler/fullchain.pem \
        -subj "/CN=$SERVER_IP" \
        -addext "subjectAltName=IP:$SERVER_IP" 2>/dev/null
    
    chmod 600 /etc/nginx/ssl/incident-handler/*.pem
    echo -e "${GREEN}✓${NC} Self-signed certificate generated"
    echo -e "${YELLOW}⚠️  Browsers will show security warnings${NC}"
else
    echo -e "${RED}❌ Invalid choice${NC}"
    exit 1
fi
echo ""

# Step 3: Deploy Docker Containers
echo -e "${BLUE}🐳 Step 3: Deploying Docker Containers${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Stop existing containers
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Start containers
docker-compose -f docker-compose.prod.yml up -d --build

echo -e "${YELLOW}⏳ Waiting for containers to start...${NC}"
sleep 15

# Check container status
docker-compose -f docker-compose.prod.yml ps
echo ""

# Step 4: Configure Nginx
echo -e "${BLUE}⚙️  Step 4: Configuring Nginx${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Copy Nginx configuration
cp nginx-standalone.conf /etc/nginx/sites-available/incident-handler

# Create symlink
ln -sf /etc/nginx/sites-available/incident-handler /etc/nginx/sites-enabled/incident-handler

# Remove default site if exists
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo -e "${YELLOW}Testing Nginx configuration...${NC}"
nginx -t

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Nginx configuration valid"
else
    echo -e "${RED}❌ Nginx configuration error${NC}"
    exit 1
fi

# Reload Nginx
systemctl reload nginx
echo -e "${GREEN}✓${NC} Nginx configured and reloaded"
echo ""

# Step 5: Configure Firewall
echo -e "${BLUE}🔥 Step 5: Configuring Firewall${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v ufw &> /dev/null; then
    ufw allow 80/tcp >/dev/null 2>&1
    ufw allow 443/tcp >/dev/null 2>&1
    echo -e "${GREEN}✓${NC} Firewall configured (ports 80, 443)"
else
    echo -e "${YELLOW}⚠️  UFW not found - manually open ports 80 and 443${NC}"
fi
echo ""

# Step 6: Health Check
echo -e "${BLUE}🏥 Step 6: Health Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sleep 5

# Test Docker app
if curl -s http://127.0.0.1:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker app is healthy"
else
    echo -e "${YELLOW}⚠️  Docker app health check pending${NC}"
fi

# Test Nginx proxy
if curl -k -s https://localhost/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Nginx proxy is working"
else
    echo -e "${YELLOW}⚠️  Nginx proxy check pending${NC}"
fi
echo ""

# Display summary
echo ""
echo "=============================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "=============================================="
echo ""
echo -e "${BLUE}Access your application:${NC}"
echo ""
echo -e "  ${GREEN}HTTPS:${NC} https://$SERVER_IP"
echo -e "  ${GREEN}HTTP:${NC}  http://$SERVER_IP  ${YELLOW}(redirects to HTTPS)${NC}"
echo ""
echo -e "${BLUE}Architecture:${NC}"
echo "  Browser → Nginx (host:443) → Docker App (localhost:8000) → PostgreSQL"
echo ""
echo -e "${BLUE}Service Status:${NC}"
echo "  Nginx:  systemctl status nginx"
echo "  Docker: docker-compose -f docker-compose.prod.yml ps"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo "  Nginx:  tail -f /var/log/nginx/incident-handler-error.log"
echo "  Docker: docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  Restart Nginx:  systemctl restart nginx"
echo "  Restart Docker: docker-compose -f docker-compose.prod.yml restart"
echo "  Stop all:       docker-compose -f docker-compose.prod.yml down"
echo ""
echo "=============================================="
