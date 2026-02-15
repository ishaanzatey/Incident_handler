# Quick Reference - Production Deployment

## ✅ What Changed

### 1. Application NOT Directly Accessible
- ❌ **Before:** App exposed on port 8000
- ✅ **Now:** App ONLY accessible through Nginx reverse proxy

### 2. Flexible SSL Certificates
- ✅ Use your own SSL certificates (any CA)
- ✅ Or generate self-signed for testing

---

## 🚀 Deploy in 3 Steps

### Step 1: Transfer to Linux Server
```bash
scp -r Incident_Handler user@server-ip:/home/user/
```

### Step 2: SSH and Navigate
```bash
ssh user@server-ip
cd Incident_Handler
```

### Step 3: Run Deployment
```bash
./deploy-production.sh
```

**That's it!**

---

## 🔐 SSL Certificate Options

### Option 1: Use Your Own Certificates

```bash
# Place your certificates
mkdir -p certs
cp /path/to/fullchain.pem certs/
cp /path/to/privkey.pem certs/

# Deploy
./deploy-production.sh
# Choose option 1
```

### Option 2: Self-Signed (Testing)

```bash
# Deploy
./deploy-production.sh
# Choose option 2 (auto-generates certificate)
```

---

## 🌐 Access

**After deployment:**
```
https://YOUR_SERVER_IP
```

**Examples:**
- `https://192.168.1.100`
- `https://10.0.0.50`

---

## 🏗️ Architecture

```
Browser
   ↓
Nginx (Port 443)
   ↓
App Container (INTERNAL - Not exposed)
   ↓
PostgreSQL
```

**Key:** App is NOT accessible at `http://IP:8000` - ONLY through Nginx!

---

## ✅ Verification

```bash
# Services running
docker-compose -f docker-compose.prod.yml ps

# Test HTTPS
curl -k https://localhost/api/health

# Verify app NOT directly accessible (should fail)
curl http://localhost:8000  # Should get "Connection refused"
```

---

## 📋 Files Modified

1. **`docker-compose.prod.yml`** - App has NO ports exposed
2. **`nginx.conf`** - Reverse proxy to app container
3. **`deploy-production.sh`** - SSL certificate flexibility

---

## 🎯 No Changes Needed

All files work as-is! Just ensure `.env` has correct ServiceNow credentials.

---

**Ready to deploy!** 🚀
