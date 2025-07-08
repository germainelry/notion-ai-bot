# Notion AI Bot

A modern, async Python bot that connects Notion to OpenAI's ChatGPT, automating Q&A, research, and documentation directly in your Notion workspace.

---

## Features

- **Seamless Notion ↔️ ChatGPT integration**
- **Async worker**: Fast, scalable, and configurable polling
- **Web dashboard**: Monitor status via FastAPI (`app.py`)
- **Automatic code extraction**: Stores code blocks separately
- **Contextual memory**: Remembers previous prompts for better answers
- **Persistent storage**: Uses SQLite for all prompt/response history
- **Easy search & reset**: CLI tools to view, search, or reset memory
- **Auto-reset on inactivity**: Memory can be reset automatically after a configurable period of inactivity

---

## Quick Start

1. **Clone the repo**
2. **Set up your Notion database** ([see setup guide](NOTION_SETUP.md))
3. **Create a `.env` file** with your API keys (see below)
4. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
5. **Run the worker**
   ```sh
   python main.py
   ```
6. _(Optional)_ **Run the web dashboard**
   ```sh
   python app.py
   ```

---

## Environment Variables

- `NOTION_DB_ID` — Your Notion database ID
- `NOTION_API_KEY` — Your Notion integration token
- `OPENAI_API_KEY` — Your OpenAI API key
- `FAST_MODE` — (optional) Set to `1` for instant response
- `CONTEXT_WINDOW` — (optional) Number of previous prompts to use as context (default: 5)
- `INACTIVITY_RESET_HOURS` — (optional) Number of hours of inactivity before memory is automatically reset (default: 24)

---

## Usage

- **Add prompts** to your Notion database (Status: Pending)
- The worker processes them and writes responses back to Notion
- **Monitor** via the web dashboard (optional)
- **View memory**:
  ```sh
  python main.py memory
  ```
- **Search memory**:
  ```sh
  python main.py search <query>
  ```
- **Reset memory**:
  ```sh
  python main.py reset
  ```

---

## Deployment

- **Railway/Render:** Deploy `main.py` as a worker and `app.py` as a web service
- **Add environment variables** to both services
- _(Optional)_ Use persistent volumes for long-term memory retention
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for details

---

## Memory System

- All prompts and responses are stored in a local SQLite database (`notion_bot_memory.db`)
- The bot uses the last N prompt/response pairs as context for ChatGPT (configurable via `CONTEXT_WINDOW`)
- **Automatic memory reset:** If no prompt is processed for a configurable period (`INACTIVITY_RESET_HOURS`), the memory is reset automatically.
- For a full technical explanation, see [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md)

---

## File Structure

```
notion-ai-bot/
├── main.py              # Worker: Notion processor
├── app.py               # Web dashboard
├── memory_db.py         # SQLite memory system
├── extract_code.py      # Code extraction utility
├── requirements.txt     # Python dependencies
├── NOTION_SETUP.md      # Notion setup guide
├── DEPLOYMENT_GUIDE.md  # Deployment instructions
├── MEMORY_SYSTEM.md     # Memory system details
└── ...
```

---

**© 2025 Germaine Luah**
