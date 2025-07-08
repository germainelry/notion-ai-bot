# Notion AI Bot - Async Automation with ChatGPT & Notion 🚀

A modern, async automation system that seamlessly connects Notion to OpenAI's ChatGPT, designed to boost productivity by automating knowledge work, answering questions, and streamlining your workflow — all within your Notion workspace.

This lightweight Python bot continuously monitors a Notion database for new prompts (Status = Pending), sends them to ChatGPT (GPT-3.5 or GPT-4), and writes the generated responses directly back into the Notion table — making it your personal AI assistant for study notes, coding help, or content drafting.

---

## What Are the Two Services?

### 1. **Web Service (`app.py`)**

- **Purpose:** Runs the web dashboard/status page so you can monitor the bot's health and status in your browser.
- **How to run:** `python app.py`
- **Deploy as:** The `web` service on Railway/Render.

### 2. **Worker Service (`main.py`)**

- **Purpose:** Continuously polls your Notion database for new prompts, sends them to ChatGPT, and writes responses back to Notion.
- **How to run:** `python main.py`
- **Deploy as:** The `worker` service on Railway/Render.

**Both must be running for the bot to work!**

---

## 🎯 Features

- **Automate Q&A, research, and documentation in Notion**
- **Async & Fast Mode**: Instant response with FAST_MODE, or tune delays for batching
- **Continuous Polling**: Adaptive intervals (configurable)
- **Web Interface**: Monitor status via browser (`app.py`)
- **Code Extraction**: Automatically extracts and stores code blocks separately
- **Memory System (SQLite)**: Tracks all prompts and responses for search, context, and analysis
- **Long Response Handling**: Smart splitting for responses over 1900 characters
- **Contextual Chat**: Remembers previous prompts and responses for more natural conversations

---

## 🚀 Quick Start

1. **Clone the repo & set up your environment**
2. **Create a Notion database** with the required columns
3. **Configure your `.env` file** with Notion and OpenAI API keys
4. **Deploy both services** (web and worker) as described below

---

## Deployment (Railway Example)

1. **Deploy the Web Service**
   - Start command: `python app.py`
   - Add environment variables: `NOTION_DB_ID`, `NOTION_API_KEY`, `OPENAI_API_KEY`, etc.
2. **Deploy the Worker Service**
   - Start command: `python main.py`
   - Add the same environment variables as the web service

**Both services must be running for full functionality!**

---

## Environment Variables

- `NOTION_DB_ID`
- `NOTION_API_KEY`
- `OPENAI_API_KEY`
- _(Optional: FAST_MODE, polling intervals, etc.)_

---

## Usage

- Add prompts to Notion (Status: Pending)
- The worker service processes them and updates the database
- Monitor the system via the web dashboard

---

## 🧠 Memory Retention & Context (New: SQLite-based)

### 1. **How Memory Retention Works**

- Every prompt and response is stored in a local SQLite database (`notion_bot_memory.db`).
- When a new prompt is processed, the bot automatically retrieves the last few prompt/response pairs and sends them as context to ChatGPT. This allows the bot to "remember" the conversation and provide more relevant, contextual answers.
- **You do not need to do anything special in Notion**—just keep adding prompts as usual. The bot will remember previous prompts and responses automatically.

### 2. **How the Database Updates (Railway/Cloud)**

- The SQLite database is updated automatically by the worker service running on Railway.
- **No manual intervention is needed.**
- Note: The database file is stored in the Railway service's filesystem. If the service is redeployed or restarted, the file may be lost unless you use Railway's persistent volumes (if available). For most use cases, the memory will persist as long as the service is running.

### 3. **How to Reset the Memory (Start a New Chat)**

- You can reset the memory (clear all previous prompts and responses) by running:
  ```sh
  python main.py reset
  ```
  - On Railway, you can trigger this by running a one-off job or using the Railway shell.
- This will clear the SQLite database and the bot will "forget" all previous conversations, starting fresh.
- **Note:** There is no way to reset memory from within Notion itself; the reset must be triggered via the command line.

### 4. **Searching and Viewing Memory**

- To view recent prompts:
  ```sh
  python main.py memory
  ```
- To search for previous prompts:
  ```sh
  python main.py search <query>
  ```

---

## File Structure

```
notion-ai-bot/
├── main.py                 # Worker: Notion processor
├── app.py                  # Web: Dashboard/status page
├── extract_code.py         # Code extraction utility
├── memory_db.py            # SQLite-based memory system
├── notion_bot_memory.db    # SQLite database (auto-created)
├── requirements.txt        # Python dependencies
├── NOTION_SETUP.md         # Database setup guide
├── DEPLOYMENT_GUIDE.md     # Deployment instructions
├── COST_MONITORING.md      # Cost optimization tips
└── README.md               # This documentation
```

---

**© 2025 Germaine Luah**
