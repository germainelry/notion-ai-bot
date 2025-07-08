# 🧠 Notion AI Bot Memory System (SQLite)

This document explains in detail how the memory retention system works in `main.py` and `memory_db.py` for the Notion AI Bot.

---

## 1. Overview

- The bot uses a local SQLite database (`notion_bot_memory.db`) to store every prompt and response it processes.
- This enables the bot to "remember" previous conversations, provide context to ChatGPT, and allow searching/viewing of past interactions.

---

## 2. How Prompts and Responses Are Stored

### Where in the Code?

- In `main.py`, inside the `continuous_polling` function:

```python
await memory_db.add_entry(prompt_text, reply, page_id, extracted_codes)
```

- This line is called after every prompt is processed and a response is generated.
- It calls the `add_entry` method in `memory_db.py`, which inserts a new row into the SQLite database.

### What Is Stored?

- Timestamp
- Notion page ID
- Prompt text
- Response text
- Extracted code blocks (if any)

---

## 3. Feeding Context to ChatGPT (Conversation Memory)

### Where in the Code?

- In `main.py`, the function `ask_chatgpt_with_context`:

```python
recent_pairs = await memory_db.get_recent_prompts(limit=5)
messages = []
for prev_prompt, prev_response in reversed(recent_pairs):
    messages.append({"role": "user", "content": prev_prompt})
    messages.append({"role": "assistant", "content": prev_response})
messages.append({"role": "user", "content": prompt})
```

- This builds a list of the last 5 prompt/response pairs and sends them as context to ChatGPT, followed by the new prompt.
- The OpenAI API receives this as the `messages` parameter, allowing it to generate context-aware responses.

### Why Does This Work?

- By including previous turns, ChatGPT can "see" the conversation history and respond more naturally, as if in a chat.

---

## 4. Searching for Previous Prompts

### Where in the Code?

- In `memory_db.py`, the method `search_memory`:

```python
async def search_memory(self, query, limit=10):
    import difflib
    ...
    similarity = difflib.SequenceMatcher(None, query.lower(), prompt.lower()).ratio()
    if similarity > 0.3:
        results.append((similarity, prompt, response, timestamp, code_blocks))
```

- This method compares the search query to all stored prompts using fuzzy matching (difflib).
- Returns the most similar previous prompts and their responses.

### How to Use

- From the command line:
  ```sh
  python main.py search <query>
  ```
- This will print the most similar previous prompts and their similarity scores.

---

## 5. Viewing Recent Prompts

### Where in the Code?

- In `memory_db.py`, the method `get_recent_entries`:

```python
async def get_recent_entries(self, limit=10):
    ...
    return await cursor.fetchall()
```

- This retrieves the most recent prompts and responses from the database.

### How to Use

- From the command line:
  ```sh
  python main.py memory
  ```
- This will print the last 5 prompts and responses, including code block counts.

---

## 6. Resetting Memory

### Where in the Code?

- In `memory_db.py`, the method `clear`:

```python
async def clear(self):
    async with aiosqlite.connect(self.db_path) as db:
        await db.execute("DELETE FROM memory")
        await db.commit()
```

- This deletes all rows from the memory table, erasing all stored prompts and responses.

### How to Use

- From the command line:
  ```sh
  python main.py reset
  ```
- This will clear the memory database and start fresh.

---

## 7. Summary Table

| Functionality         | How It Works / How to Use                 |
| --------------------- | ----------------------------------------- |
| Store prompt/response | `await memory_db.add_entry(...)`          |
| Feed context to GPT   | `ask_chatgpt_with_context` builds context |
| Search memory         | `python main.py search <query>`           |
| View recent memory    | `python main.py memory`                   |
| Reset memory          | `python main.py reset`                    |

---

## Running CLI Commands in Railway (Locally)

You can use the [Railway CLI](https://docs.railway.app/develop/cli) to link your local project to your Railway service and run memory/search/reset commands in the Railway environment.

### 1. **Install the Railway CLI**

```sh
npm install -g railway
```

### 2. **Login to Railway**

```sh
railway login
```

### 3. **Link Your Local Project to Railway**

In your project directory:

```sh
railway link
```

Follow the prompts to select your Railway project.

### 4. **Run Commands in the Railway Environment**

You can now run commands in your Railway service environment using:

```sh
railway run python main.py memory
railway run python main.py search <query>
railway run python main.py reset
```

This will use your Railway environment variables and database, just like in production.

---

**For more details, see the code in `main.py` and `memory_db.py`.**
