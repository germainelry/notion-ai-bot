# Notion AI Bot - Productivity Edition 🕵️

A modern, async automation system that connects Notion to ChatGPT, designed to boost productivity by automating knowledge work, answering questions, and streamlining your workflow—all from your Notion workspace.

## 🎯 Features

- **Productivity Boost**: Automate Q&A, research, and documentation in Notion
- **Async & Fast Mode**: Instant response with FAST_MODE, or tune delays for batching
- **Continuous Polling**: Adaptive intervals (configurable)
- **Free Tier Optimized**: Uses GPT-3.5-turbo with token limits
- **Web Interface**: Monitor status via browser
- **Error Handling**: Robust error recovery and logging
- **Random Delays**: Avoids detection patterns (unless FAST_MODE)

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to project
git clone <your-repo>
cd notion-ai-bot
```

### 2. Configure API Keys

Create a `.env` file (not included in repo):

```env
NOTION_DB_ID=your_database_id_here
NOTION_API_KEY=your_notion_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. (Optional) Enable Fast Mode or Custom Delays

For instant response:

```env
FAST_MODE=1
```

Or, for custom delays:

```env
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

### 4. Create Notion Database

Create a Notion database with these properties:

- **Prompt** (Title): Your questions/tasks
- **Status** (Select): Pending/Done
- **Response** (Rich Text): AI responses
- **Generated Date** (Date): When response was generated (date+time)

### 5. Run the Bot

```bash
# Web interface (recommended)
python app.py

# Or console mode
python main.py
```

## 🔧 Setup Details

- **No secrets or API keys are in this repo.**
- **.env is gitignored and must be created by you.**
- **Safe for public GitHub.**

## 🕵️ Productivity & Async Features

- **Async**: All Notion/OpenAI calls are async for speed and scalability
- **FAST_MODE**: All delays minimized for instant response
- **Configurable**: All delays and intervals can be set via env vars
- **No local traces**: All processing is in the cloud

## 📊 Usage

- Add prompts to Notion, set status to Pending
- Bot will process and update with response and timestamp
- Monitor via web interface or logs

## 🔒 Security & Privacy

- No API keys or secrets in code or repo
- .env is gitignored
- All cloud-to-cloud (no local traces)

## 🛠️ Troubleshooting

- Check logs for errors
- Ensure all environment variables are set
- See COST_MONITORING.md for cost tips

## 🚀 Deployment Options

- **Railway**: Free 24/7 hosting (see DEPLOYMENT_GUIDE.md)
- **Render**: Free alternative
- **VPS/Docker**: Supported

## 📈 Advanced Configuration

- All delays and intervals are configurable via env vars
- FAST_MODE=1 for instant response
- See NOTION_SETUP.md for Notion database setup

## 🤝 Contributing

Safe for public GitHub. No secrets in repo.

## ⚠️ Disclaimer

This tool is designed for legitimate productivity use. Ensure compliance with your organization's policies. The authors are not responsible for misuse.

---

**Happy automating! 🚀**
