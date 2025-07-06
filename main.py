import os, asyncio, random, logging
from datetime import datetime
from dotenv import load_dotenv
import httpx
import openai
from openai import AsyncOpenAI
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

# Configure logging to be less visible
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notion_bot.log'),
        logging.StreamHandler()
    ]
)

# ✅ Load env vars
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# === Configurable Delays and Intervals ===
FAST_MODE = os.getenv("FAST_MODE", "0") == "1"
MIN_POLL_INTERVAL = int(os.getenv("MIN_POLL_INTERVAL", 30))
MAX_POLL_INTERVAL = int(os.getenv("MAX_POLL_INTERVAL", 300))
PROMPT_DELAY_MIN = float(os.getenv("PROMPT_DELAY_MIN", 2.0))
PROMPT_DELAY_MAX = float(os.getenv("PROMPT_DELAY_MAX", 5.0))
NOTION_QUERY_DELAY_MIN = float(os.getenv("NOTION_QUERY_DELAY_MIN", 0.5))
NOTION_QUERY_DELAY_MAX = float(os.getenv("NOTION_QUERY_DELAY_MAX", 2.0))
NOTION_UPDATE_DELAY_MIN = float(os.getenv("NOTION_UPDATE_DELAY_MIN", 1.0))
NOTION_UPDATE_DELAY_MAX = float(os.getenv("NOTION_UPDATE_DELAY_MAX", 3.0))
JITTER = float(os.getenv("JITTER", 5.0))

if FAST_MODE:
    MIN_POLL_INTERVAL = 2
    MAX_POLL_INTERVAL = 5
    PROMPT_DELAY_MIN = PROMPT_DELAY_MAX = 0.1
    NOTION_QUERY_DELAY_MIN = NOTION_QUERY_DELAY_MAX = 0.1
    NOTION_UPDATE_DELAY_MIN = NOTION_UPDATE_DELAY_MAX = 0.1
    JITTER = 0
    logging.info("🚀 FAST_MODE enabled: All delays minimized for instant response.")

# Async OpenAI client
try:
    async_openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
except Exception:
    async_openai_client = None

# ThreadPool for sync OpenAI fallback
thread_pool = ThreadPoolExecutor()

async def get_pending_prompts():
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    body = {
        "filter": {
            "and": [
                {"property": "Status", "select": {"equals": "Pending"}},
                {"property": "Response", "rich_text": {"is_empty": True}}
            ]
        }
    }
    await asyncio.sleep(random.uniform(NOTION_QUERY_DELAY_MIN, NOTION_QUERY_DELAY_MAX))
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, headers=NOTION_HEADERS, json=body, timeout=10)
            if res.status_code != 200:
                logging.error(f"Failed to fetch prompts: {res.status_code} - {res.text}")
                return []
            return res.json().get("results", [])
        except Exception as e:
            logging.error(f"Error fetching prompts: {e}")
            return []

async def ask_chatgpt(prompt):
    try:
        if async_openai_client:
            res = await async_openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            return res.choices[0].message.content
        else:
            # Fallback: run sync OpenAI in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(thread_pool, sync_ask_chatgpt, prompt)
    except Exception as e:
        logging.error(f"Error calling ChatGPT: {e}")
        return f"Error processing request: {str(e)}"

def sync_ask_chatgpt(prompt):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500,
        presence_penalty=0.1,
        frequency_penalty=0.1
    )
    return res.choices[0].message.content

async def update_response(page_id, response):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    current_time = datetime.now()
    truncated_response = response[:1900] + "..." if len(response) > 1900 else response
    payload = {
        "properties": {
            "Response": {"rich_text": [{"text": {"content": truncated_response}}]},
            "Status": {"select": {"name": "Done"}},
            "Generated Date": {"date": {"start": current_time.isoformat(), "end": None}}
        }
    }
    await asyncio.sleep(random.uniform(NOTION_UPDATE_DELAY_MIN, NOTION_UPDATE_DELAY_MAX))
    async with httpx.AsyncClient() as client:
        try:
            res = await client.patch(url, headers=NOTION_HEADERS, json=payload, timeout=10)
            if res.status_code != 200:
                logging.error(f"Failed to update page {page_id}: {res.status_code}")
                return False
            return True
        except Exception as e:
            logging.error(f"Error updating page {page_id}: {e}")
            return False

async def continuous_polling():
    consecutive_empty = 0
    base_interval = MIN_POLL_INTERVAL
    while True:
        try:
            logging.info("🔄 Checking for prompts...")
            prompts = await get_pending_prompts()
            if prompts:
                consecutive_empty = 0
                logging.info(f"Found {len(prompts)} pending prompts.")
                for p in prompts:
                    prompt_text = p["properties"]["Prompt"]["title"][0]["text"]["content"]
                    page_id = p["id"]
                    logging.info(f"🧠 Processing: {prompt_text[:50]}...")
                    reply = await ask_chatgpt(prompt_text)
                    if await update_response(page_id, reply):
                        logging.info(f"✅ Updated page: {page_id}")
                    else:
                        logging.error(f"❌ Failed to update page: {page_id}")
                    await asyncio.sleep(random.uniform(PROMPT_DELAY_MIN, PROMPT_DELAY_MAX))
                sleep_time = max(1, base_interval - 10)
            else:
                consecutive_empty += 1
                logging.info(f"No pending prompts found. (Empty count: {consecutive_empty})")
                if consecutive_empty > 5:
                    sleep_time = min(MAX_POLL_INTERVAL, base_interval + consecutive_empty * 10)
                else:
                    sleep_time = base_interval
            jitter = random.uniform(-JITTER, JITTER)
            actual_sleep = max(1, sleep_time + jitter)
            logging.info(f"Sleeping for {actual_sleep:.1f} seconds...")
            await asyncio.sleep(actual_sleep)
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            await asyncio.sleep(60)

async def main():
    logging.info("🚀 Starting Notion AI Bot with async mode...")
    if not all([NOTION_DB_ID, NOTION_API_KEY, OPENAI_API_KEY]):
        logging.error("❌ Missing required environment variables!")
        return
    await continuous_polling()

if __name__ == "__main__":
    asyncio.run(main())