# Deployment Guide: Ubuntu Server with Nginx

This guide explains how to deploy the Career Guidance AI application on an Ubuntu server using Nginx as a reverse proxy.

## 📋 Prerequisites

1. **Ubuntu Server**: Ubuntu 20.04 LTS or higher (22.04 LTS recommended)
2. **Root/Sudo Access**: Administrative access to the server
3. **Domain Name** (Optional): For SSL/HTTPS setup
4. **SSH Access**: Ability to connect to your server

## 🚀 Step-by-Step Deployment

### Step 1: Initial Server Setup

#### 1.1 Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

#### 1.2 Install Required System Packages

```bash
sudo apt install -y python3 python3-pip python3-venv nginx git curl
```

#### 1.3 Create Application User (Recommended)

```bash
sudo adduser --disabled-password --gecos "" careerapp
sudo usermod -aG sudo careerapp
```

#### 1.4 Configure Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### Step 2: Clone and Setup Application

#### 2.1 Switch to Application User

```bash
sudo su - careerapp
```

#### 2.2 Clone Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/career-guidance-ai.git
cd career-guidance-ai
```

Replace `YOUR_USERNAME` with your GitHub username.

#### 2.3 Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2.4 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.5 Create Environment File

```bash
nano .env
```

Add the following content:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
PORT=8000
API_BASE_URL=http://your-domain.com
ALLOWED_ORIGINS=http://your-domain.com,https://your-domain.com
```

**Important**: Replace `your-domain.com` with your actual domain or server IP.

Save and exit (Ctrl+X, then Y, then Enter).

### Step 3: Configure FastAPI Backend

#### 3.1 Test Backend Locally

```bash
source venv/bin/activate
python main.py
```

Test in another terminal:
```bash
curl http://localhost:8000/health
```

Should return: `{"status": "healthy", "service": "career-guidance-agent"}`

Stop the server (Ctrl+C).

#### 3.2 Create Systemd Service for Backend

```bash
sudo nano /etc/systemd/system/career-backend.service
```

Add the following content:

```ini
[Unit]
Description=Career Guidance AI Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=careerapp
WorkingDirectory=/home/careerapp/career-guidance-ai
Environment="PATH=/home/careerapp/career-guidance-ai/venv/bin"
ExecStart=/home/careerapp/career-guidance-ai/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Important**: Update paths if your application is in a different location.

Save and exit.

#### 3.3 Enable and Start Backend Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable career-backend
sudo systemctl start career-backend
sudo systemctl status career-backend
```

Check logs:
```bash
sudo journalctl -u career-backend -f
```

### Step 4: Configure Streamlit Frontend

#### 4.1 Create Systemd Service for Frontend

```bash
sudo nano /etc/systemd/system/career-frontend.service
```

Add the following content:

```ini
[Unit]
Description=Career Guidance AI Frontend (Streamlit)
After=network.target career-backend.service

[Service]
Type=simple
User=careerapp
WorkingDirectory=/home/careerapp/career-guidance-ai
Environment="PATH=/home/careerapp/career-guidance-ai/venv/bin"
ExecStart=/home/careerapp/career-guidance-ai/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save and exit.

#### 4.2 Enable and Start Frontend Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable career-frontend
sudo systemctl start career-frontend
sudo systemctl status career-frontend
```

Check logs:
```bash
sudo journalctl -u career-frontend -f
```

### Step 5: Configure Nginx as Reverse Proxy

#### 5.1 Create Nginx Configuration for Backend

```bash
sudo nano /etc/nginx/sites-available/career-backend
```

Add the following content:

```nginx
server {
    listen 80;
    server_name api.your-domain.com;  # Replace with your domain or use IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Save and exit.

#### 5.2 Create Nginx Configuration for Frontend

```bash
sudo nano /etc/nginx/sites-available/career-frontend
```

Add the following content:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Replace with your domain or use IP

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

Save and exit.

#### 5.3 Enable Nginx Sites

```bash
sudo ln -s /etc/nginx/sites-available/career-backend /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/career-frontend /etc/nginx/sites-enabled/
```

#### 5.4 Test Nginx Configuration

```bash
sudo nginx -t
```

If test passes, reload Nginx:

```bash
sudo systemctl reload nginx
```

#### 5.5 Verify Services

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:8501

# Check Nginx
sudo systemctl status nginx
```

### Step 6: Setup SSL/HTTPS (Optional but Recommended)

#### 6.1 Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

#### 6.2 Obtain SSL Certificate

```bash
# For frontend
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# For backend API
sudo certbot --nginx -d api.your-domain.com
```

Follow the prompts to complete SSL setup.

#### 6.3 Auto-Renewal

Certbot automatically sets up renewal. Test it:

```bash
sudo certbot renew --dry-run
```

#### 6.4 Update Environment Variables

After SSL setup, update `.env`:

```env
API_BASE_URL=https://api.your-domain.com
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

Restart services:

```bash
sudo systemctl restart career-backend
sudo systemctl restart career-frontend
```

### Step 7: Update Application Configuration

#### 7.1 Update Backend CORS

Edit `main.py` or set environment variable:

```bash
sudo nano /home/careerapp/career-guidance-ai/.env
```

Add:
```env
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com,http://localhost:8501
```

#### 7.2 Update Frontend API URL

The frontend will use the environment variable or Streamlit secrets. For production, ensure `.env` has:

```env
API_BASE_URL=https://api.your-domain.com
```

Or update the systemd service to pass environment variables.

### Step 8: Configure Logging

#### 8.1 View Backend Logs

```bash
sudo journalctl -u career-backend -n 50 --no-pager
sudo journalctl -u career-backend -f  # Follow logs
```

#### 8.2 View Frontend Logs

```bash
sudo journalctl -u career-frontend -n 50 --no-pager
sudo journalctl -u career-frontend -f  # Follow logs
```

#### 8.3 View Nginx Logs

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Step 9: Security Hardening

#### 9.1 Update Nginx Security Headers

Edit frontend config:

```bash
sudo nano /etc/nginx/sites-available/career-frontend
```

Add security headers:

```nginx
server {
    # ... existing configuration ...
    
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

#### 9.2 Restrict Backend Access (Optional)

If you want to restrict backend API access:

```nginx
# In career-backend config
location / {
    # Allow only from frontend domain
    allow 127.0.0.1;
    allow your-server-ip;
    deny all;
    
    proxy_pass http://127.0.0.1:8000;
    # ... rest of proxy settings ...
}
```

#### 9.3 Keep System Updated

```bash
# Set up automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Step 10: Monitoring and Maintenance

#### 10.1 Create Monitoring Script

```bash
sudo nano /home/careerapp/check-services.sh
```

Add:

```bash
#!/bin/bash

# Check backend
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend is down! Restarting..."
    sudo systemctl restart career-backend
fi

# Check frontend
if ! curl -f http://localhost:8501 > /dev/null 2>&1; then
    echo "Frontend is down! Restarting..."
    sudo systemctl restart career-frontend
fi
```

Make executable:

```bash
chmod +x /home/careerapp/check-services.sh
```

#### 10.2 Setup Cron Job for Monitoring

```bash
crontab -e
```

Add:

```cron
*/5 * * * * /home/careerapp/check-services.sh >> /home/careerapp/service-check.log 2>&1
```

#### 10.3 Useful Commands

```bash
# Restart services
sudo systemctl restart career-backend
sudo systemctl restart career-frontend
sudo systemctl restart nginx

# Check service status
sudo systemctl status career-backend
sudo systemctl status career-frontend
sudo systemctl status nginx

# View logs
sudo journalctl -u career-backend -n 100
sudo journalctl -u career-frontend -n 100

# Reload Nginx after config changes
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Advanced Configuration

### Multiple Domains Setup

If you want to serve both frontend and backend from the same domain:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:8501;
        # ... proxy settings ...
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        # ... proxy settings ...
    }
}
```

Then update `app.py` to use relative URLs:

```python
API_BASE_URL = "/api"  # Relative URL
```

### Load Balancing (Multiple Backend Instances)

If running multiple backend instances:

```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

### Rate Limiting

Add rate limiting to Nginx:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    location / {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## 🐛 Troubleshooting

### Backend Not Starting

1. **Check logs**:
   ```bash
   sudo journalctl -u career-backend -n 50
   ```

2. **Check if port is in use**:
   ```bash
   sudo netstat -tulpn | grep 8000
   ```

3. **Verify environment variables**:
   ```bash
   sudo cat /home/careerapp/career-guidance-ai/.env
   ```

4. **Test manually**:
   ```bash
   cd /home/careerapp/career-guidance-ai
   source venv/bin/activate
   python main.py
   ```

### Frontend Not Starting

1. **Check logs**:
   ```bash
   sudo journalctl -u career-frontend -n 50
   ```

2. **Check if port is in use**:
   ```bash
   sudo netstat -tulpn | grep 8501
   ```

3. **Verify Streamlit installation**:
   ```bash
   source /home/careerapp/career-guidance-ai/venv/bin/activate
   streamlit --version
   ```

### Nginx Errors

1. **Test configuration**:
   ```bash
   sudo nginx -t
   ```

2. **Check error logs**:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Verify upstream services**:
   ```bash
   curl http://127.0.0.1:8000/health
   curl http://127.0.0.1:8501
   ```

### Connection Issues

1. **Check firewall**:
   ```bash
   sudo ufw status
   ```

2. **Check if services are listening**:
   ```bash
   sudo ss -tulpn | grep -E '8000|8501|80|443'
   ```

3. **Test from server**:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8501
   ```

## 📊 Performance Optimization

### Enable Gzip Compression

Add to Nginx config:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

### Increase Worker Processes

Edit `/etc/nginx/nginx.conf`:

```nginx
worker_processes auto;
worker_connections 1024;
```

### Optimize FastAPI

For production, use multiple workers:

```ini
# In career-backend.service
ExecStart=/home/careerapp/career-guidance-ai/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
```

## 🔄 Updating the Application

### Update from GitHub

```bash
cd /home/careerapp/career-guidance-ai
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
sudo systemctl restart career-backend
sudo systemctl restart career-frontend
```

### Rollback

```bash
cd /home/careerapp/career-guidance-ai
git checkout <previous-commit-hash>
sudo systemctl restart career-backend
sudo systemctl restart career-frontend
```

## 📝 Deployment Checklist

- [ ] Server updated and packages installed
- [ ] Application cloned and dependencies installed
- [ ] Environment variables configured
- [ ] Backend systemd service created and running
- [ ] Frontend systemd service created and running
- [ ] Nginx configured and running
- [ ] SSL certificates installed (if using HTTPS)
- [ ] Firewall configured
- [ ] Services tested and working
- [ ] Monitoring setup
- [ ] Logs configured
- [ ] Backup strategy in place

## 🎉 Success!

Once deployed, you'll have:
- ✅ Backend: `http://api.your-domain.com` or `https://api.your-domain.com`
- ✅ Frontend: `http://your-domain.com` or `https://your-domain.com`
- ✅ API Docs: `http://api.your-domain.com/docs`

## 📚 Additional Resources

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Systemd Service Files](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Certbot Documentation](https://certbot.eff.org/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)

---

**Note**: This setup is for production use. Ensure you have proper backups and monitoring in place.

