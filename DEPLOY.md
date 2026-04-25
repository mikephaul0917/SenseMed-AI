# Deployment Guide: Render.com

## Prerequisites
- GitHub account with your repository pushed (✅ Already done)
- Render.com account (free tier available)
- API keys for:
  - Google Gemini API
  - Arcade MCP

## Step-by-Step Deployment

### 1. Sign Up on Render
- Go to [render.com](https://render.com)
- Click "Sign up" and authenticate with GitHub
- Grant Render access to your repositories

### 2. Create a New Web Service
- Click "New +" → "Web Service"
- Select your `SenseMed-AI` repository
- Choose the branch (main)

### 3. Configure Service
Fill in the following settings:

| Field | Value |
|-------|-------|
| **Name** | sensemed-ai |
| **Environment** | Python 3 |
| **Region** | Choose closest to your users |
| **Branch** | main |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn agent_app.main:app --bind 0.0.0.0:$PORT` |

### 4. Add Environment Variables
Click "Advanced" → "Add Environment Variable" for each:

```
GOOGLE_API_KEY = <your_api_key>
ARCADE_API_KEY = <your_api_key>
FLASK_ENV = production
PYTHONUNBUFFERED = 1
```

### 5. Set Up Database (Optional)
For persistent SQLite storage, you can:
- Use Render's PostgreSQL addon (paid)
- Or keep SQLite in `/tmp` (data resets on redeploy)

To use PostgreSQL, add:
```
DATABASE_URL = postgresql://user:password@host/dbname
```

### 6. Deploy
- Click "Create Web Service"
- Render will automatically:
  - Clone your repo
  - Install dependencies
  - Start the Flask app
  - Assign a public URL

### 7. Monitor Deployment
- Watch the "Deploy Log" tab
- Once complete, you'll get a URL like: `https://sensemed-ai.onrender.com`

## Troubleshooting

### Port Binding Error
Ensure `main.py` doesn't hardcode a port:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000))
```

### Database Issues
- SQLite in `/tmp` will reset on redeploy
- Consider PostgreSQL for production data persistence

### Build Failures
Check the Build Log for missing dependencies or syntax errors

## Post-Deployment
Once deployed:
1. Visit your Render URL
2. Test the dashboard
3. Monitor logs via Render dashboard
4. Set up auto-deploy on GitHub pushes (automatic with Render)

## Next Steps
- Set up a custom domain (optional)
- Enable auto-deploys from GitHub
- Add monitoring/alerts
- Consider upgrading to paid plan for persistent storage
