# Notion AI Bot - Stealth Edition 🕵️

A stealthy automation system that connects Notion to ChatGPT, designed to work around corporate restrictions while appearing as a legitimate system monitor.

## 🎯 Features

- **Stealth Mode**: Appears as a system monitor to avoid detection
- **Continuous Polling**: Adaptive intervals (30s-5min) based on activity
- **Free Tier Optimized**: Uses GPT-3.5-turbo with token limits
- **Web Interface**: Monitor status via browser
- **Error Handling**: Robust error recovery and logging
- **Random Delays**: Avoids detection patterns

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to project
git clone <your-repo>
cd notion-ai-bot

# Run the deployment script
python deploy.py
```

### 2. Configure API Keys

The script will create a `.env` file. Fill in your API keys:

```env
NOTION_DB_ID=your_database_id_here
NOTION_API_KEY=your_notion_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Create Notion Database

Create a Notion database with these properties:

- **Prompt** (Title): Your questions/tasks
- **Status** (Select): Pending/Done
- **Response** (Rich Text): AI responses

### 4. Run the Bot

```bash
# Web interface (recommended)
python app.py

# Or console mode
python main.py
```

## 🔧 Setup Details

### Getting Notion API Keys

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create new integration
3. Copy the API key
4. Share your database with the integration

### Getting OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new API key
3. Add billing info (free tier available)

### Database ID

1. Open your Notion database
2. Copy the ID from the URL: `https://notion.so/workspace/[DATABASE_ID]`

## 🕵️ Stealth Features

### Detection Avoidance

- **Random Delays**: 0.5-3s random delays between requests
- **Adaptive Polling**: Slower when idle, faster when busy
- **Jitter**: ±5s variation in polling intervals
- **Stealth Logging**: Logs saved to file, not console
- **Generic Names**: Uses "System Monitor" branding

### Web Interface

- Looks like a legitimate system monitor
- No obvious AI/ChatGPT references
- Clean, professional interface
- Real-time status monitoring

### Cost Optimization

- GPT-3.5-turbo (cheaper than GPT-4)
- Token limits (500 max tokens)
- Efficient prompt processing
- Free tier compatible

## 📊 Usage

### Adding Tasks

1. Open your Notion database
2. Add new row with your prompt in the "Prompt" field
3. Set status to "Pending"
4. Bot will automatically process and respond

### Monitoring

- **Web**: Visit `http://localhost:8000`
- **Logs**: Check `notion_bot.log`
- **Status**: Real-time processing status

## 🔒 Security & Privacy

### Corporate Compliance

- No ChatGPT web access required
- All AI processing happens externally
- Notion remains the only visible interface
- No suspicious network traffic patterns

### Data Handling

- Responses truncated to 1900 characters
- Timestamps added to all responses
- Error handling prevents data loss
- No sensitive data stored locally

## 🛠️ Troubleshooting

### Common Issues

**"Missing environment variables"**

- Check your `.env` file exists
- Verify all API keys are set correctly

**"Failed to fetch prompts"**

- Check Notion API key
- Verify database ID
- Ensure integration has access to database

**"Error calling ChatGPT"**

- Check OpenAI API key
- Verify billing is set up
- Check internet connection

### Logs

Check `notion_bot.log` for detailed error information.

## 🚀 Deployment Options

### Local Development

```bash
python deploy.py
```

### Cloud Deployment

- **Railway**: Easy deployment with environment variables
- **Heroku**: Free tier available
- **VPS**: Full control, more stealth

### Docker (Advanced)

```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

## 📈 Advanced Configuration

### Custom Polling Intervals

Add to `.env`:

```env
MIN_POLL_INTERVAL=30
MAX_POLL_INTERVAL=300
```

### Custom Models

Edit `main.py` to use different models:

```python
# For GPT-4 (more expensive)
model="gpt-4"

# For Claude (alternative)
model="claude-3-sonnet-20240229"
```

## 🤝 Contributing

This is a stealth project - keep it low-key!

## ⚠️ Disclaimer

This tool is designed for legitimate productivity use. Ensure compliance with your organization's policies. The authors are not responsible for misuse.

---

**Happy coding! 🚀**
