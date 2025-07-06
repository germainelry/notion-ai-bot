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
    logging.info("FAST_MODE enabled: All delays minimized for instant response.")

# Async OpenAI client
try:
    async_openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
except Exception:
    async_openai_client = None

# ThreadPool for sync OpenAI fallback
thread_pool = ThreadPoolExecutor()

# Memory system for tracking prompts and responses
class MemorySystem:
    def __init__(self):
        self.memory_file = "notion_bot_memory.json"
        self.memory = self.load_memory()
    
    def load_memory(self):
        try:
            import json
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"prompts": [], "responses": [], "statistics": {"total_processed": 0}}
    
    def save_memory(self):
        import json
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def add_entry(self, prompt, response, page_id, extracted_codes=None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "page_id": page_id,
            "prompt": prompt,
            "response": response,
            "response_length": len(response),
            "code_blocks": extracted_codes or []
        }
        self.memory["prompts"].append(entry)
        self.memory["statistics"]["total_processed"] += 1
        self.save_memory()
        logging.info(f"Memory: Added entry for page {page_id} (Total: {self.memory['statistics']['total_processed']})")
    
    def get_recent_prompts(self, limit=10):
        return self.memory["prompts"][-limit:]
    
    def search_memory(self, query):
        """Search through memory for similar prompts"""
        import difflib
        results = []
        for entry in self.memory["prompts"]:
            similarity = difflib.SequenceMatcher(None, query.lower(), entry["prompt"].lower()).ratio()
            if similarity > 0.3:  # 30% similarity threshold
                results.append((similarity, entry))
        return sorted(results, key=lambda x: x[0], reverse=True)

# Initialize memory system
memory_system = MemorySystem()

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
                max_tokens=1000,  # Increased for better code responses
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
            logging.info("Checking for prompts...")
            prompts = await get_pending_prompts()
            if prompts:
                consecutive_empty = 0
                logging.info(f"Found {len(prompts)} pending prompts.")
                for p in prompts:
                    prompt_text = p["properties"]["Prompt"]["title"][0]["text"]["content"]
                    page_id = p["id"]
                    logging.info(f"Processing: {prompt_text[:50]}...")
                    
                    # Check memory for similar prompts
                    similar_prompts = memory_system.search_memory(prompt_text)
                    if similar_prompts:
                        logging.info(f"Memory: Found {len(similar_prompts)} similar previous prompts")
                        # You could use this to provide context to ChatGPT
                    
                    reply = await ask_chatgpt(prompt_text)
                    
                    # Extract code blocks for memory storage
                    _, extracted_codes = extract_code_blocks(reply)
                    
                    # Store in memory
                    memory_system.add_entry(prompt_text, reply, page_id, extracted_codes)
                    
                    if await update_response(page_id, reply):
                        logging.info(f"Updated page: {page_id}")
                    else:
                        logging.error(f"Failed to update page: {page_id}")
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
    await continuous_polling()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "memory":
            # Show memory statistics
            print(f"Total prompts processed: {memory_system.memory['statistics']['total_processed']}")
            print("\nRecent prompts:")
            for entry in memory_system.get_recent_prompts(5):
                code_info = f" ({len(entry.get('code_blocks', []))} code blocks)" if entry.get('code_blocks') else ""
                print(f"- {entry['timestamp']}: {entry['prompt'][:100]}...{code_info}")
        elif sys.argv[1] == "search" and len(sys.argv) > 2:
            # Search memory
            query = " ".join(sys.argv[2:])
            results = memory_system.search_memory(query)
            print(f"Search results for '{query}':")
            for similarity, entry in results[:5]:
                print(f"- {similarity:.2f}: {entry['prompt'][:100]}...")
        else:
            print("Usage: python main.py [memory|search <query>]")
    else:
        asyncio.run(main())