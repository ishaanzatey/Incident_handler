#!/bin/bash

# Production Deployment Script - Nginx Reverse Proxy Setup
# The application is ONLY accessible through Nginx (not directly)

set -e

echo "=============================================="
echo "  Incident Handler - Production Deployment"
echo "  Nginx Reverse Proxy Setup"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Please do not run this script as root${NC}"
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

# Check .env file
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

echo -e "${BLUE}� Deployment Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
echo -e "${GREEN}✓${NC} Server IP detected: ${YELLOW}$SERVER_IP${NC}"
echo ""

# SSL Certificate Setup
echo -e "${BLUE}🔐 SSL Certificate Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Choose SSL certificate option:"
echo "  1) Use existing certificates (in ./certs/ directory)"
echo "  2) Generate self-signed certificate (for testing)"
echo ""
read -p "Enter choice (1 or 2): " SSL_CHOICE

mkdir -p certs

if [ "$SSL_CHOICE" = "1" ]; then
    # Check if certificates exist
    if [ -f "certs/fullchain.pem" ] && [ -f "certs/privkey.pem" ]; then
        echo -e "${GREEN}✓${NC} Using existing certificates"
    else
        echo -e "${YELLOW}⚠️  Certificate files not found in ./certs/${NC}"
        echo ""
        echo "Please place your SSL certificates in ./certs/ directory:"
        echo "  - certs/fullchain.pem  (certificate)"
        echo "  - certs/privkey.pem    (private key)"
        echo ""
        read -p "Press Enter after placing certificates, or Ctrl+C to cancel..."
        
        if [ ! -f "certs/fullchain.pem" ] || [ ! -f "certs/privkey.pem" ]; then
            echo -e "${RED}❌ Certificates still not found${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓${NC} Certificates found"
    fi
    
elif [ "$SSL_CHOICE" = "2" ]; then
    echo -e "${YELLOW}📜 Generating self-signed certificate...${NC}"
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout certs/privkey.pem \
        -out certs/fullchain.pem \
        -subj "/CN=$SERVER_IP" \
        -addext "subjectAltName=IP:$SERVER_IP" 2>/dev/null
    
    echo -e "${GREEN}✓${NC} Self-signed certificate generated"
    echo -e "${YELLOW}⚠️  Browsers will show security warnings (normal for self-signed)${NC}"
else
    echo -e "${RED}❌ Invalid choice${NC}"
    exit 1
fi

echo ""

# Firewall Configuration
echo -e "${BLUE}🔥 Firewall Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v ufw &> /dev/null; then
    sudo ufw allow 80/tcp >/dev/null 2>&1
    sudo ufw allow 443/tcp >/dev/null 2>&1
    echo -e "${GREEN}✓${NC} Ports 80 and 443 opened"
else
    echo -e "${YELLOW}⚠️  UFW not found - please manually open ports 80 and 443${NC}"
fi
echo ""

# Stop existing containers
echo -e "${BLUE}🛑 Stopping existing containers${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
echo -e "${GREEN}✓${NC} Stopped"
echo ""

# Build and start services
echo -e "${BLUE}🚀 Building and starting services${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker-compose -f docker-compose.prod.yml up -d --build

echo ""
echo -e "${YELLOW}⏳ Waiting for services to initialize...${NC}"
sleep 15

# Check service status
echo ""
echo -e "${BLUE}📊 Service Status${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker-compose -f docker-compose.prod.yml ps
echo ""

# Test health
echo -e "${BLUE}🏥 Health Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sleep 5
if curl -k -s "https://localhost/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Application is healthy"
else
    echo -e "${YELLOW}⚠️  Health check pending (services may still be starting)${NC}"
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

if [ "$SSL_CHOICE" = "2" ]; then
    echo -e "${YELLOW}⚠️  Browser Security Warning:${NC}"
    echo "   Self-signed certificate will show a warning"
    echo "   Click 'Advanced' → 'Proceed' to continue"
    echo ""
fi

echo -e "${BLUE}Architecture:${NC}"
echo "  Browser → Nginx (port 443) → App Container → PostgreSQL"
echo "  ${YELLOW}Note: App is NOT directly accessible (only through Nginx)${NC}"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  View logs:    docker-compose -f docker-compose.prod.yml logs -f"
echo "  Stop:         docker-compose -f docker-compose.prod.yml down"
echo "  Restart:      docker-compose -f docker-compose.prod.yml restart"
echo "  Rebuild:      docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "=============================================="
