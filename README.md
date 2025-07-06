# Notion AI Bot - Productivity Edition 🚀

A modern, async automation system that connects Notion to ChatGPT, designed to boost productivity by automating knowledge work, answering questions, and streamlining your workflow—all from your Notion workspace.

## 🎯 Features

- **Productivity Boost**: Automate Q&A, research, and documentation in Notion
- **Async & Fast Mode**: Instant response with FAST_MODE, or tune delays for batching
- **Continuous Polling**: Adaptive intervals (configurable)
- **Free Tier Optimized**: Uses GPT-3.5-turbo with token limits
- **Web Interface**: Monitor status via browser
- **Error Handling**: Robust error recovery and logging
- **Random Delays**: Avoids detection patterns (unless FAST_MODE)
- **Code Extraction**: Automatically extracts and stores code blocks separately
- **Memory System**: Tracks all prompts and responses for search and analysis
- **Long Response Handling**: Smart splitting for responses over 1900 characters

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
- **Code Output** (Rich Text): Extracted code blocks (NEW)
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

# 🆕 Recent Improvements

## 1. Long Response Handling

### Problem

- Responses longer than 1900 characters were truncated with "..."
- Important information was lost

### Solution

- **Smart Response Splitting**: Long responses are now split by sentences to avoid cutting in the middle
- **Multi-Part Storage**: First part goes to the main Response field, additional parts are added as comments
- **Clear Indicators**: Users see how many parts the response has been split into

### How it works:

1. If response ≤ 1900 chars: stored normally
2. If response > 1900 chars: split by sentences into multiple blocks
3. First block goes to Response field with continuation notice
4. Additional blocks added as page comments (requires "Insert content" permission)

**Note**: If your Notion integration doesn't have "Insert content" permission, additional blocks will be logged but not saved to Notion.

## 2. Developer-Friendly Code Extraction

### Problem

- Code blocks in responses were hard to copy and use
- No easy way to extract and save code files

### Solution

- **Enhanced Code Block Formatting**: Code blocks are now clearly marked with separators
- **Code Extraction Utility**: `extract_code.py` script to extract and save code blocks
- **Increased Token Limit**: Increased from 500 to 1000 tokens for better code responses
- **Separate Code Storage**: Code blocks are automatically extracted and stored in a dedicated "Code Output" column

### Usage:

```bash
# Extract code from a response file
python extract_code.py response.txt

# The script will:
# 1. Find all code blocks
# 2. Show preview of each block
# 3. Ask if you want to save them
# 4. Save with appropriate file extensions
```

### Code Block Format:

```
==================================================
CODE BLOCK (PYTHON)
==================================================
def hello_world():
    print("Hello, World!")
==================================================
```

## 3. Memory Retention System

### Problem

- No history of prompts and responses
- No way to learn from previous interactions
- No search capability

### Solution

- **Persistent Memory**: All prompts and responses stored in `notion_bot_memory.json`
- **Similarity Search**: Find similar previous prompts
- **Statistics Tracking**: Track total processed prompts
- **Command Line Interface**: View memory and search

### Usage:

```bash
# View memory statistics and recent prompts
python main.py memory

# Search memory for similar prompts
python main.py search "python async"

# Run the bot normally
python main.py
```

### Memory Features:

- **Automatic Storage**: Every prompt/response pair is automatically saved
- **Similarity Detection**: Uses difflib to find similar previous prompts
- **Timestamp Tracking**: All entries include timestamps
- **Response Length Tracking**: Track response sizes for optimization

## 4. Additional Improvements

### Unicode Fix

- Removed emoji characters from logging messages
- Fixed Windows PowerShell encoding issues
- Clean, readable log output

### Enhanced Logging

- Better error handling
- More informative status messages
- Memory tracking in logs

### Configuration

- All delays and intervals remain configurable via environment variables
- FAST_MODE still available for testing
- Memory system is transparent and doesn't affect performance

## File Structure

```
notion-ai-bot/
├── main.py                 # Main bot with all improvements
├── app.py                  # Web interface
├── extract_code.py         # Code extraction utility
├── notion_bot_memory.json  # Memory storage (auto-created)
├── extracted_code/         # Directory for extracted code files
├── NOTION_SETUP.md        # Database setup guide
├── DEPLOYMENT_GUIDE.md    # Deployment instructions
├── COST_MONITORING.md     # Cost optimization tips
└── README.md              # This documentation
```

## Environment Variables

All existing environment variables still work:

- `FAST_MODE=1` - Enable fast mode for testing
- `MIN_POLL_INTERVAL=30` - Minimum polling interval
- `MAX_POLL_INTERVAL=300` - Maximum polling interval
- `PROMPT_DELAY_MIN=2.0` - Minimum delay between prompts
- `PROMPT_DELAY_MAX=5.0` - Maximum delay between prompts
- `NOTION_QUERY_DELAY_MIN=0.5` - Minimum Notion query delay
- `NOTION_QUERY_DELAY_MAX=2.0` - Maximum Notion query delay
- `NOTION_UPDATE_DELAY_MIN=1.0` - Minimum Notion update delay
- `NOTION_UPDATE_DELAY_MAX=3.0` - Maximum Notion update delay
- `JITTER=5.0` - Random jitter for intervals

## Benefits for Developers

1. **Easy Code Extraction**: Use `extract_code.py` to quickly extract and save code blocks
2. **Memory Search**: Find similar previous prompts to avoid duplication
3. **Complete Responses**: No more truncated responses, all content is preserved
4. **Better Logging**: Clean, readable logs without encoding issues
5. **Historical Tracking**: Keep track of all your AI interactions
6. **Separate Code Storage**: Code blocks are automatically extracted and stored separately

## Future Enhancements

- **Context Awareness**: Use memory to provide context to ChatGPT
- **Response Templates**: Pre-defined response templates for common tasks
- **Code Validation**: Automatic syntax checking for extracted code
- **Integration**: Connect with version control systems
- **Analytics**: Response time and quality metrics

---

**Happy automating! 🚀 © 2025 Germaine Luah**
