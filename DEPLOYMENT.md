# Deployment Guide: Streamlit Cloud with GitHub

This guide explains how to deploy the Career Guidance AI application to Streamlit Cloud using a GitHub repository.

## 📋 Prerequisites

1. **GitHub Account**: Create a free account at [github.com](https://github.com)
2. **Streamlit Cloud Account**: Sign up at [streamlit.io/cloud](https://streamlit.io/cloud) (free tier available)
3. **Git Installed**: On your local machine
4. **GitHub Repository**: Your code pushed to GitHub

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository

#### 1.1 Initialize Git Repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit: Career Guidance AI Agent"
```

#### 1.2 Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name it (e.g., `career-guidance-ai`)
4. **DO NOT** initialize with README, .gitignore, or license (if you already have these)
5. Click "Create repository"

#### 1.3 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/career-guidance-ai.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 2: Prepare for Streamlit Cloud

#### 2.1 Create `streamlit_app.py` (Optional but Recommended)

Streamlit Cloud looks for `streamlit_app.py` or `app.py` by default. Since we have `app.py`, we're good, but you can create an alias:

**Option A**: Keep using `app.py` (recommended)
- Streamlit Cloud will automatically detect it

**Option B**: Create `streamlit_app.py` that imports from `app.py`:
```python
# streamlit_app.py
from app import main

if __name__ == '__main__':
    main()
```

#### 2.2 Create `.streamlit/config.toml` (Optional)

Create a `.streamlit` directory and `config.toml` file for configuration:

```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

#### 2.3 Update `.gitignore`

Ensure `.gitignore` includes:
```
.env
__pycache__/
*.pyc
venv/
.env.local
```

**IMPORTANT**: Never commit `.env` file with API keys!

### Step 3: Deploy Backend Separately

Since Streamlit Cloud only hosts the frontend, you need to deploy the FastAPI backend separately.

#### Option A: Deploy Backend to Railway (Recommended - Free Tier)

1. **Sign up at [railway.app](https://railway.app)**
2. **Create New Project**
3. **Deploy from GitHub**:
   - Connect your GitHub account
   - Select your repository
   - Railway will auto-detect Python
4. **Configure**:
   - Root Directory: `/` (root)
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Python Version: 3.10 or 3.11
5. **Set Environment Variables**:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `GEMINI_MODEL`: `gemini-2.5-flash`
   - `PORT`: Railway sets this automatically
6. **Get Backend URL**: Railway will provide a URL like `https://your-app.railway.app`

#### Option B: Deploy Backend to Render (Free Tier)

1. **Sign up at [render.com](https://render.com)**
2. **Create New Web Service**
3. **Connect GitHub Repository**
4. **Configure**:
   - Name: `career-guidance-backend`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Set Environment Variables**:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `GEMINI_MODEL`: `gemini-2.5-flash`
6. **Get Backend URL**: Render will provide a URL

#### Option C: Deploy Backend to Heroku

1. **Install Heroku CLI**: [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)
2. **Create `Procfile`**:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. **Deploy**:
   ```bash
   heroku create your-app-name
   heroku config:set GEMINI_API_KEY=your_key_here
   heroku config:set GEMINI_MODEL=gemini-2.5-flash
   git push heroku main
   ```

### Step 4: Deploy Frontend to Streamlit Cloud

#### 4.1 Sign in to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Authorize Streamlit Cloud to access your repositories

#### 4.2 Deploy Your App

1. Click **"New app"**
2. **Select Repository**: Choose your GitHub repository
3. **Branch**: Select `main` (or your default branch)
4. **Main file path**: Enter `app.py`
5. **App URL**: Choose a custom subdomain (optional)
6. Click **"Deploy"**

#### 4.3 Configure Secrets (Environment Variables)

1. In Streamlit Cloud, go to your app settings
2. Click **"Secrets"** or **"Settings" → "Secrets"**
3. Add the following secrets:

```toml
# .streamlit/secrets.toml (in Streamlit Cloud UI)
GEMINI_API_KEY = "your_gemini_api_key_here"
GEMINI_MODEL = "gemini-2.5-flash"
API_BASE_URL = "https://your-backend-url.railway.app"  # Your backend URL from Step 3
```

**Important**: 
- Replace `your-backend-url.railway.app` with your actual backend URL
- Never commit secrets to GitHub!

### Step 5: Update Frontend Code for Production

#### 5.1 Update `app.py` to Use Streamlit Secrets

Modify the beginning of `app.py`:

```python
# Configuration
import streamlit as st

# Try to get from secrets (Streamlit Cloud) or env (local)
if hasattr(st, 'secrets') and 'API_BASE_URL' in st.secrets:
    API_BASE_URL = st.secrets['API_BASE_URL']
    GEMINI_API_KEY = st.secrets.get('GEMINI_API_KEY')
else:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

#### 5.2 Commit and Push Changes

```bash
git add app.py
git commit -m "Update for Streamlit Cloud deployment"
git push origin main
```

Streamlit Cloud will automatically redeploy when you push changes.

### Step 6: Verify Deployment

1. **Check Backend**: Visit your backend URL (e.g., `https://your-app.railway.app/health`)
   - Should return: `{"status": "healthy", "service": "career-guidance-agent"}`

2. **Check Frontend**: Visit your Streamlit Cloud URL
   - Should show the chat interface
   - Sidebar should show "✅ Backend Connected"

3. **Test Conversation**: Try a full conversation flow

## 🔧 Configuration Files for Deployment

### For Railway/Render Backend

Create `Procfile` (for Heroku) or use platform-specific config:

**Railway**: Uses `railway.json` or environment variables
**Render**: Uses `render.yaml`:

```yaml
services:
  - type: web
    name: career-guidance-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: GEMINI_MODEL
        value: gemini-2.5-flash
```

### For Streamlit Cloud

Create `.streamlit/config.toml`:

```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

## 🔐 Security Best Practices

### 1. Never Commit Secrets

- ✅ Add `.env` to `.gitignore`
- ✅ Use Streamlit Cloud Secrets for frontend
- ✅ Use platform environment variables for backend
- ❌ Never commit API keys to GitHub

### 2. Update CORS Settings

In `main.py`, update CORS for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.streamlit.app",  # Your Streamlit Cloud URL
        "http://localhost:8501"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting (Optional)

Consider adding rate limiting to your backend for production:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/chat")
@limiter.limit("10/minute")  # 10 requests per minute
async def chat(request: Request, chat_request: ChatRequest):
    # ... existing code
```

## 📝 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Backend deployed (Railway/Render/Heroku)
- [ ] Backend URL obtained and tested
- [ ] Frontend deployed to Streamlit Cloud
- [ ] Secrets configured in Streamlit Cloud
- [ ] API_BASE_URL updated in frontend code
- [ ] CORS configured for production
- [ ] Both services tested and working
- [ ] Custom domain configured (optional)

## 🐛 Troubleshooting

### Frontend Can't Connect to Backend

1. **Check Backend URL**: Verify it's correct in Streamlit secrets
2. **Check CORS**: Ensure backend allows your Streamlit Cloud URL
3. **Check Backend Status**: Visit backend `/health` endpoint
4. **Check Logs**: View Streamlit Cloud logs for errors

### Backend Not Starting

1. **Check Logs**: View platform logs (Railway/Render/Heroku)
2. **Verify Dependencies**: Ensure `requirements.txt` is correct
3. **Check Port**: Backend should use `$PORT` environment variable
4. **Verify Environment Variables**: All required vars are set

### API Key Errors

1. **Verify Key**: Check if API key is correct
2. **Check Quota**: Verify Gemini API quota not exceeded
3. **Check Secrets**: Ensure secrets are set correctly in Streamlit Cloud

## 🔄 Continuous Deployment

Streamlit Cloud automatically redeploys when you:
- Push to the main branch
- Merge a pull request
- Manually trigger redeploy

Backend platforms (Railway/Render) also auto-deploy on git push.

## 📊 Monitoring

### Streamlit Cloud
- View logs in Streamlit Cloud dashboard
- Monitor usage and performance
- Check error logs

### Backend Platform
- Railway: View logs in dashboard
- Render: View logs in service dashboard
- Heroku: Use `heroku logs --tail`

## 🎉 Success!

Once deployed, you'll have:
- ✅ Frontend: `https://your-app.streamlit.app`
- ✅ Backend: `https://your-backend.railway.app`
- ✅ API Docs: `https://your-backend.railway.app/docs`

Share the Streamlit Cloud URL with users!

## 📚 Additional Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Railway Documentation](https://docs.railway.app)
- [Render Documentation](https://render.com/docs)
- [Heroku Documentation](https://devcenter.heroku.com)

---

**Note**: Free tiers have limitations. For production use, consider paid plans or self-hosting.

