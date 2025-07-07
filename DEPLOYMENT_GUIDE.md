# 🚀 Cloud Deployment Guide (Railway & Render)

## Railway Deployment (Recommended)

### 1. Prepare Your Code

```bash
git add .
git commit -m "Deploy Notion AI Bot"
git push origin main
```

### 2. Deploy to Railway

- Go to [railway.app](https://railway.app)
- Sign up with GitHub
- Click **New Project** → **Deploy from GitHub repo** → Select your repository

### 3. Set Up the Web Service

- **Start Command:** `python app.py`
- **Port:** `8000`
- **Add Environment Variables:**
  ```
  NOTION_DB_ID=your_database_id_here
  NOTION_API_KEY=your_notion_api_key_here
  OPENAI_API_KEY=your_openai_api_key_here
  ```
  _(Add any optional variables for FAST_MODE or custom delays as needed)_
- **Deploy the web service.**

### 4. Add the Worker Service (for Notion Processing)

- In your Railway project, click **New Service** (or the “+” button)
- **Deploy from GitHub repo** → Select your repository
- **Start Command:** `python main.py`
- **Add the same environment variables** as your web service
- **Deploy the worker service**

**You should now have two services:**

- `web` (runs `python app.py`) — the dashboard/status page
- `worker` (runs `python main.py`) — the background Notion processor

**Both must be running for full functionality!**

---

## Render Deployment (Alternative)

1. Go to [render.com](https://render.com)
2. Create account with GitHub
3. New Web Service → Connect your repo
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `python app.py`
6. Add environment variables (same as above)
7. Deploy!

---

## Environment Variables

- **No secrets or API keys are in this repo.**
- **.env is gitignored and must be created by you.**
- **Safe for public GitHub.**

---

## Testing & Monitoring

- Add a test prompt to your Notion database (Status: Pending)
- Wait for the worker to process it
- Check the response and "Generated Date" in Notion
- Monitor logs in Railway/Render dashboard

---

## Troubleshooting

- **Bot not responding?**
  - Check logs in cloud platform
  - Verify environment variables
  - Test API keys locally
- **High costs?**
  - Monitor OpenAI usage
  - Set spending limits in OpenAI dashboard
  - Reduce polling frequency if needed

---

## Cost

- **Railway/Render:** FREE (500 hours/month)
- **OpenAI:** ~$2-5/month for personal use
- **Notion:** FREE

---

## Next Steps

1. Choose Railway or Render
2. Follow the deployment steps above
3. Add your environment variables
4. Deploy and test
5. Monitor the logs
6. Enjoy 24x7 automation!
