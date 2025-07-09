# 💰 Cost Monitoring Guide

## Railway Costs (Hosting)

### Check Railway Usage:

1. Go to [railway.app](https://railway.app)
2. Click on your project
3. Go to **Billing** tab
4. You'll see:
   - Current usage (hours used)
   - Free tier limit (500 hours/month)
   - Remaining hours

### Railway Free Tier:

- ✅ **500 hours/month** (enough for 24/7)
- ✅ **Automatic restarts** included
- ✅ **SSL certificates** included
- ✅ **Custom domains** included

### If you exceed free tier:

- Railway will notify you
- You can upgrade to paid plan
- Or switch to Render (also has free tier)

---

## OpenAI Costs (AI Processing)

### Check OpenAI Usage:

1. Go to [platform.openai.com/usage](https://platform.openai.com/usage)
2. You'll see:
   - Daily usage
   - Monthly usage
   - Cost breakdown by model

### Set Spending Limits:

1. Go to [platform.openai.com/account/billing/overview](https://platform.openai.com/account/billing/overview)
2. Click **Set limits**
3. Set a monthly spending limit (e.g., $10/month)

### Typical Costs:

- **GPT-3.5-turbo**: ~$0.50 per 1M input tokens
- **Your bot**: ~$2-5/month for personal use
- **100 prompts/day**: ~$0.075/day = ~$2.25/month

---

## Cost Optimization Tips

### Reduce OpenAI Costs:

- ✅ **Already optimized**: Using GPT-3.5-turbo (cheapest)
- ✅ **Token limits**: Recommended limit of 2000 max tokens per response
- ✅ **Efficient polling**: Only calls API when needed
- ✅ **No idle calls**: No unnecessary API requests

### Monitor Usage:

- Check Railway dashboard weekly
- Check OpenAI usage monthly
- Set spending alerts if needed

### Cost Breakdown Example:

```
Railway (Hosting):     FREE (500 hours/month)
OpenAI (AI Processing): $2-5/month
Notion (Database):      FREE
Total:                  $2-5/month
```

---

## Alerts and Notifications

### Railway Alerts:

- Railway will email you if approaching free tier limit
- You can set up custom alerts in dashboard

### OpenAI Alerts:

- Set spending limits in OpenAI dashboard
- You'll get notified before exceeding limits
- Can pause service if needed

---

## Troubleshooting High Costs

### If OpenAI costs are high:

1. Check usage patterns in OpenAI dashboard
2. Reduce polling frequency (increase MIN_POLL_INTERVAL)
3. Reduce max_tokens in main.py
4. Set lower spending limits

### If Railway costs are high:

1. Check if you're exceeding free tier
2. Consider switching to Render (also free)
3. Optimize your bot's resource usage

---

## Quick Commands

### Check Railway Status:

- Go to railway.app → Your project → Deployments
- Check logs for any issues

### Check OpenAI Usage:

- Go to platform.openai.com/usage
- Monitor daily/monthly usage

### Set OpenAI Limits:

- Go to platform.openai.com/account/billing/overview
- Set monthly spending limit
