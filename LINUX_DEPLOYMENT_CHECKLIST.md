# Linux Server Deployment Checklist

This guide provides a complete checklist for deploying the Incident Handler application on a Linux server using Docker.

## Prerequisites

### On Your Local Machine
- [ ] All files are ready in `/Users/ishan/Desktop/Incident_Handler`
- [ ] `.env` file is configured with correct values
- [ ] You have SSH access to the Linux server

### On Linux Server
- [ ] Docker is installed (`docker --version`)
- [ ] Docker Compose is installed (`docker-compose --version`)
- [ ] User has permissions to run Docker commands
- [ ] Ports 8000 and 5432 are available

## Step 1: Prepare Files for Transfer

On your local machine, verify all required files exist:

```bash
cd /Users/ishan/Desktop/Incident_Handler

# Check essential files
ls -la .env docker-compose.yml Dockerfile requirements.txt
```

## Step 2: Transfer Files to Linux Server

### Option A: Using SCP (Recommended)

```bash
# Replace with your server details
SERVER_USER="your_username"
SERVER_IP="your_server_ip"
DEPLOY_PATH="/home/$SERVER_USER/incident_handler"

# Create deployment directory on server
ssh $SERVER_USER@$SERVER_IP "mkdir -p $DEPLOY_PATH"

# Transfer all files
scp -r /Users/ishan/Desktop/Incident_Handler/* $SERVER_USER@$SERVER_IP:$DEPLOY_PATH/
```

### Option B: Using rsync (Better for updates)

```bash
rsync -avz --exclude='.git' --exclude='__pycache__' \
  /Users/ishan/Desktop/Incident_Handler/ \
  $SERVER_USER@$SERVER_IP:$DEPLOY_PATH/
```

## Step 3: Configure Environment Variables

SSH into your server and verify/update the `.env` file:

```bash
ssh $SERVER_USER@$SERVER_IP
cd $DEPLOY_PATH

# Edit .env if needed
nano .env
```

**Important Configuration Notes:**

### For Docker Deployment (Default)
The `.env` file is already configured with these defaults:
```env
PG_HOST=postgres
PG_PORT=5432
PG_DB=incident_automation
PG_USER=incident_bot
PG_PASSWORD=Kashmir2025$
```

✅ **No changes needed** - These work with Docker Compose

### For Non-Docker Deployment
If running without Docker, change:
```env
PG_HOST=localhost  # or your PostgreSQL server IP
```

## Step 4: Deploy with Docker Compose

```bash
# Start the application
docker-compose up -d

# Verify containers are running
docker-compose ps

# Check logs
docker-compose logs -f
```

Expected output:
```
NAME                    STATUS          PORTS
incident-handler-app    Up 30 seconds   0.0.0.0:8000->8000/tcp
incident-handler-db     Up 30 seconds   5432/tcp
```

## Step 5: Verify Deployment

### Check Application Health

```bash
# Test API endpoint
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","database_mode":"postgres"}
```

### Access Dashboard

Open your browser and navigate to:
```
http://YOUR_SERVER_IP:8000
```

You should see:
- ✅ Connection status showing "Connected"
- ✅ Statistics cards displaying
- ✅ No error banners (unless database is unavailable)

## Step 6: Monitor and Maintain

### View Logs

```bash
# All logs
docker-compose logs -f

# Application logs only
docker-compose logs -f app

# Database logs only
docker-compose logs -f postgres
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart app
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose down -v
```

### Update Application

```bash
# Pull latest changes
cd $DEPLOY_PATH

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## Troubleshooting

### Issue: Database Connection Failed

**Symptoms:** Frontend shows "Running in In-Memory Mode" banner

**Solutions:**
1. Check if PostgreSQL container is running:
   ```bash
   docker-compose ps postgres
   ```

2. Check PostgreSQL logs:
   ```bash
   docker-compose logs postgres
   ```

3. Verify `.env` has correct database settings:
   ```bash
   cat .env | grep PG_
   ```

4. Restart services:
   ```bash
   docker-compose restart
   ```

### Issue: Port Already in Use

**Symptoms:** Error: "port is already allocated"

**Solutions:**
1. Check what's using port 8000:
   ```bash
   sudo lsof -i :8000
   ```

2. Either stop the conflicting service or change the port in `docker-compose.yml`:
   ```yaml
   ports:
     - "8080:8000"  # Use port 8080 instead
   ```

### Issue: Permission Denied

**Symptoms:** Docker commands fail with permission errors

**Solutions:**
1. Add user to docker group:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. Or use sudo:
   ```bash
   sudo docker-compose up -d
   ```

### Issue: Application Not Accessible

**Symptoms:** Cannot access dashboard from browser

**Solutions:**
1. Check if firewall is blocking port 8000:
   ```bash
   sudo ufw status
   sudo ufw allow 8000
   ```

2. Verify application is listening:
   ```bash
   netstat -tlnp | grep 8000
   ```

3. Check application logs:
   ```bash
   docker-compose logs app
   ```

## Security Recommendations

### 1. Change Default Passwords

Update `PG_PASSWORD` in `.env`:
```env
PG_PASSWORD=YourSecurePasswordHere
```

Also update in `docker-compose.yml`:
```yaml
environment:
  POSTGRES_PASSWORD: YourSecurePasswordHere
```

### 2. Use Environment Variables for Secrets

Never commit `.env` to version control. Use `.env.example` as a template.

### 3. Enable HTTPS

Use a reverse proxy like Nginx with SSL certificates:
```bash
sudo apt install nginx certbot python3-certbot-nginx
```

### 4. Restrict Access

Configure firewall to allow only specific IPs:
```bash
sudo ufw allow from YOUR_IP to any port 8000
```

## Quick Reference Commands

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Check status
docker-compose ps

# Update and restart
docker-compose down && docker-compose up -d --build

# Access PostgreSQL
docker-compose exec postgres psql -U incident_bot -d incident_automation
```

## Support

If you encounter issues not covered here:

1. Check application logs: `docker-compose logs -f app`
2. Check database logs: `docker-compose logs -f postgres`
3. Verify all environment variables are set correctly
4. Ensure Docker and Docker Compose are up to date

## Success Criteria

✅ Dashboard is accessible at `http://YOUR_SERVER_IP:8000`  
✅ Connection status shows "Connected"  
✅ Database mode shows "postgres" (not "memory")  
✅ Statistics are displaying correctly  
✅ No error notifications on page load  
✅ Processing history loads without errors  

---

**You're all set!** Your Incident Handler application is now running on your Linux server.
