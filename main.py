import os, asyncio, random, logging
from datetime import datetime
from dotenv import load_dotenv
import httpx
import openai
from openai import AsyncOpenAI
from concurrent.futures import ThreadPoolExecutor
import aiosqlite
from memory_db import MemoryDB
import ast

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
CONTEXT_WINDOW = int(os.getenv("CONTEXT_WINDOW", 5))
INACTIVITY_RESET_HOURS = int(os.getenv("INACTIVITY_RESET_HOURS", 24))
LAST_ACTIVITY_FILE = "last_activity.txt"

def update_last_activity():
    with open(LAST_ACTIVITY_FILE, "w") as f:
        f.write(datetime.now().isoformat())

def get_last_activity():
    if not os.path.exists(LAST_ACTIVITY_FILE):
        return None
    with open(LAST_ACTIVITY_FILE, "r") as f:
        ts = f.read().strip()
        try:
            return datetime.fromisoformat(ts)
        except Exception:
            return None

if FAST_MODE:
    MIN_POLL_INTERVAL = 2
    MAX_POLL_INTERVAL = 5
    PROMPT_DELAY_MIN = PROMPT_DELAY_MAX = 0.1
    NOTION_QUERY_DELAY_MIN = NOTION_QUERY_DELAY_MAX = 0.1
    NOTION_UPDATE_DELAY_MIN = NOTION_UPDATE_DELAY_MAX = 0.1
    JITTER = 0
    logging.info("FAST_MODE enabled: All delays minimized for instant response.")

# Async OpenAI client
try:
    async_openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
except Exception:
    async_openai_client = None

# ThreadPool for sync OpenAI fallback
thread_pool = ThreadPoolExecutor()

# Initialize async memory system
memory_db = MemoryDB()

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

async def ask_chatgpt_with_context(prompt):
    # Fetch last CONTEXT_WINDOW prompt/response pairs for context
    recent_pairs = await memory_db.get_recent_prompts(limit=CONTEXT_WINDOW)
    recent_pairs = list(recent_pairs)  # Ensure it's a sequence for reversed()
    messages = []
    for prev_prompt, prev_response in reversed(recent_pairs):
        messages.append({"role": "user", "content": prev_prompt})
        messages.append({"role": "assistant", "content": prev_response})
    messages.append({"role": "user", "content": prompt})
    try:
        if async_openai_client:
            res = await async_openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            response = res.choices[0].message.content
            return response
        else:
            # Fallback: run sync OpenAI in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(thread_pool, sync_ask_chatgpt, prompt)
            return response
    except Exception as e:
        logging.error(f"Error calling ChatGPT: {e}")
        return f"Error processing request: {str(e)}"

def extract_code_blocks(response):
    """Extract code blocks from response and return both cleaned response and code"""
    import re
    
    code_block_pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(code_block_pattern, response, flags=re.DOTALL)
    
    extracted_codes = []
    cleaned_response = response
    
    for language, code in matches:
        lang = language or 'text'
        extracted_codes.append({
            'language': lang,
            'code': code.strip()
        })
    
    # Remove code blocks from the main response
    cleaned_response = re.sub(code_block_pattern, '', response, flags=re.DOTALL)
    cleaned_response = re.sub(r'\n\s*\n', '\n\n', cleaned_response)  # Clean up extra newlines
    cleaned_response = cleaned_response.strip()
    
    return cleaned_response, extracted_codes

def format_code_output(codes):
    """Format extracted codes for Notion storage"""
    if not codes:
        return ""
    
    output = ""
    for i, code_info in enumerate(codes, 1):
        output += f"// {code_info['language'].upper()} CODE BLOCK {i}\n"
        output += f"{code_info['code']}\n"
        if i < len(codes):
            output += "\n" + "="*40 + "\n\n"
    
    return output

def sync_ask_chatgpt(prompt):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000,  # Increased for better code responses
        presence_penalty=0.1,
        frequency_penalty=0.1
    )
    return res.choices[0].message.content

async def update_response(page_id, response):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    current_time = datetime.now()
    
    # Extract code blocks and clean response
    cleaned_response, extracted_codes = extract_code_blocks(response)
    code_output = format_code_output(extracted_codes)
    
    # Handle long responses
    max_chars_per_block = 1900
    response_blocks = []
    
    if len(cleaned_response) <= max_chars_per_block:
        response_blocks = [cleaned_response]
    else:
        # Split by sentences to avoid cutting in the middle
        sentences = cleaned_response.split('. ')
        current_block = ""
        
        for sentence in sentences:
            if len(current_block + sentence + '. ') <= max_chars_per_block:
                current_block += sentence + '. '
            else:
                if current_block:
                    response_blocks.append(current_block.strip())
                current_block = sentence + '. '
        
        if current_block:
            response_blocks.append(current_block.strip())
    
    # Update with first block
    first_block = response_blocks[0]
    if len(response_blocks) > 1:
        first_block += f"\n\n[Response continues in {len(response_blocks)} parts - see comments below]"
    
    # Prepare payload with both response and code output
    payload = {
        "properties": {
            "Response": {"rich_text": [{"text": {"content": first_block}}]},
            "Status": {"select": {"name": "Done"}},
            "Generated Date": {"date": {"start": current_time.isoformat(), "end": None}}
        }
    }
    
    # Add code output if there are extracted codes
    if code_output:
        payload["properties"]["Code Output"] = {"rich_text": [{"text": {"content": code_output}}]}
        logging.info(f"Extracted {len(extracted_codes)} code block(s) for page {page_id}")
    await asyncio.sleep(random.uniform(NOTION_UPDATE_DELAY_MIN, NOTION_UPDATE_DELAY_MAX))
    async with httpx.AsyncClient() as client:
        try:
            res = await client.patch(url, headers=NOTION_HEADERS, json=payload, timeout=10)
            if res.status_code != 200:
                logging.error(f"Failed to update page {page_id}: {res.status_code}")
                return False
            
            # Add additional blocks as comments if response was split
            if len(response_blocks) > 1:
                try:
                    await add_response_blocks_as_comments(page_id, response_blocks[1:])
                except Exception as e:
                    logging.warning(f"Could not add comment blocks to page {page_id}: {e}")
                    logging.warning("This might be due to missing 'Insert content' permission in your Notion integration")
                    logging.warning("Only the first part of the response was saved. Additional parts:")
                    for i, block in enumerate(response_blocks[1:], 2):
                        logging.warning(f"Part {i}: {block[:100]}...")
            
            return True
        except Exception as e:
            logging.error(f"Error updating page {page_id}: {e}")
            return False

async def add_response_blocks_as_comments(page_id, blocks):
    """Add additional response blocks as comments to the Notion page"""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    
    for i, block in enumerate(blocks, 2):
        comment_text = f"Response Part {i}/{len(blocks) + 1}:\n\n{block}"
        
        payload = {
            "children": [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": comment_text}
                            }
                        ]
                    }
                }
            ]
        }
        
        await asyncio.sleep(random.uniform(NOTION_UPDATE_DELAY_MIN, NOTION_UPDATE_DELAY_MAX))
        async with httpx.AsyncClient() as client:
            try:
                res = await client.patch(url, headers=NOTION_HEADERS, json=payload, timeout=10)
                if res.status_code != 200:
                    logging.error(f"Failed to add comment block {i} to page {page_id}: {res.status_code}")
                else:
                    logging.info(f"Added response block {i} as comment to page {page_id}")
            except Exception as e:
                logging.error(f"Error adding comment block {i} to page {page_id}: {e}")

async def continuous_polling():
    consecutive_empty = 0
    base_interval = MIN_POLL_INTERVAL
    while True:
        try:
            # Inactivity auto-reset logic
            last_activity = get_last_activity()
            if last_activity and (datetime.now() - last_activity).total_seconds() > INACTIVITY_RESET_HOURS * 3600:
                logging.info(f"No activity for {INACTIVITY_RESET_HOURS} hours. Resetting memory.")
                await memory_db.clear()
                update_last_activity()  # Reset the timer after clearing

            logging.info("Checking for prompts...")
            prompts = await get_pending_prompts()
            if prompts:
                consecutive_empty = 0
                logging.info(f"Found {len(prompts)} pending prompts.")
                for p in prompts:
                    prompt_text = p["properties"]["Prompt"]["title"][0]["text"]["content"]
                    page_id = p["id"]
                    logging.info(f"Processing: {prompt_text[:50]}...")

                    # Use previous context for ChatGPT
                    reply = await ask_chatgpt_with_context(prompt_text)

                    # Extract code blocks for memory storage
                    _, extracted_codes = extract_code_blocks(reply)

                    # Store in memory DB
                    await memory_db.add_entry(prompt_text, reply, page_id, extracted_codes)

                    if await update_response(page_id, reply):
                        logging.info(f"Updated page: {page_id}")
                    else:
                        logging.error(f"Failed to update page: {page_id}")
                    update_last_activity()  # Update on every processed prompt
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
    logging.info("Starting Notion AI Bot with async mode...")
    if not all([NOTION_DB_ID, NOTION_API_KEY, OPENAI_API_KEY]):
        logging.error("Missing required environment variables!")
        return
    await memory_db.init()
    await continuous_polling()

if __name__ == "__main__":
    import sys
    import asyncio
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "memory":
            # Show memory statistics
            count = asyncio.run(memory_db.count())
            print(f"Total prompts processed: {count}")
            print("\nRecent prompts:")
            recent = asyncio.run(memory_db.get_recent_entries(5))
            for entry in recent:
                timestamp, prompt, response, code_blocks = entry
                code_info = f" ({len(ast.literal_eval(code_blocks))} code blocks)" if code_blocks else ""
                print(f"- {timestamp}: {prompt[:100]}...{code_info}")
        elif sys.argv[1] == "search" and len(sys.argv) > 2:
            # Search memory
            query = " ".join(sys.argv[2:])
            results = asyncio.run(memory_db.search_memory(query))
            print(f"Search results for '{query}':")
            for similarity, prompt, response, timestamp, code_blocks in results:
                print(f"- {similarity:.2f}: {prompt[:100]}...")
        elif sys.argv[1] == "reset":
            asyncio.run(memory_db.clear())
            print("Memory reset. All previous prompts forgotten.")
        else:
            print("Usage: python main.py [memory|search <query>|reset]")
    else:
        asyncio.run(main())