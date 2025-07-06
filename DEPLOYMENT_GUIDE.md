# Cloud Deployment Guide (Async & Fast Mode Ready)

## Quick Deployment Options

### Option 1: Railway (Recommended - Free)

1. **Prepare your code:**

   ```bash
   git add .
   git commit -m "Deploy Notion AI Bot"
   git push origin main
   ```

2. **Deploy to Railway:**

   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure the service:**

   - Set start command: `python app.py`
   - Set port: `8000`

4. **Add environment variables:**

   - **Required:**
     ```
     NOTION_DB_ID=your_database_id_here
     NOTION_API_KEY=your_notion_api_key_here
     OPENAI_API_KEY=your_openai_api_key_here
     ```
   - **Optional (for fast mode):**
     ```
     FAST_MODE=1
     ```
   - **Optional (for custom delays):**
     ```
     FAST_MODE=0
     MIN_POLL_INTERVAL=5
     MAX_POLL_INTERVAL=30
     PROMPT_DELAY_MIN=0.5
     PROMPT_DELAY_MAX=1.0
     NOTION_QUERY_DELAY_MIN=0.1
     NOTION_QUERY_DELAY_MAX=0.5
     NOTION_UPDATE_DELAY_MIN=0.1
     NOTION_UPDATE_DELAY_MAX=0.5
     JITTER=1
     ```

5. **Deploy and monitor:**
   - Click "Deploy"
   - Check logs in Railway dashboard
   - Test with a Notion prompt

### Option 2: Render (Also Free)

1. Go to [render.com](https://render.com)
2. Create account with GitHub
3. New Web Service -> Connect your repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`
6. Add environment variables (same as above)
7. Deploy!

## Environment Variables

- **No secrets or API keys are in this repo.**
- **.env is gitignored and must be created by you.**
- **Safe for public GitHub.**

## Testing Your Deployment

1. Add a test prompt to your Notion database
2. Set status to "Pending"
3. Wait a few seconds (FAST_MODE) or up to your polling interval
4. Check if the response appears
5. Verify the "Generated Date" is filled

## Monitoring

- Check logs regularly in your cloud platform
- Monitor OpenAI API usage
- Test with prompts occasionally
- Set up alerts if needed

## Cost

- **Railway/Render**: FREE (500 hours/month)
- **OpenAI**: ~$2-5/month for personal use
- **Notion**: FREE

## Troubleshooting

**Bot not responding:**

- Check logs in cloud platform
- Verify environment variables
- Test API keys locally first

**High costs:**

- Monitor OpenAI usage
- Set spending limits in OpenAI dashboard
- Consider reducing polling frequency

## Security Notes

- Never commit your .env file
- Keep API keys secure in cloud platform
- Use environment variables, not hardcoded values
- Monitor for unusual activity
- **This project is safe for public GitHub.**

## Next Steps

1. Choose Railway or Render
2. Follow the deployment steps
3. Add your environment variables
4. Deploy and test
5. Monitor the logs
6. Enjoy 24x7 automation!
