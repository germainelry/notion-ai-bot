import os, time, requests
import openai
from openai import OpenAI
import random
import logging
from datetime import datetime
from dotenv import load_dotenv

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

client = OpenAI(api_key=OPENAI_API_KEY)

def get_pending_prompts():
    """Fetch pending prompts with stealth features"""
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    body = {
        "filter": {
            "and": [
                {
                    "property": "Status",
                    "select": {
                        "equals": "Pending"
                    }
                },
                {
                    "property": "Response",
                    "rich_text": {
                        "is_empty": True
                    }
                }
            ]
        }
    }
    
    try:
        # Add random delay to avoid detection patterns
        time.sleep(random.uniform(0.5, 2.0))
        
        res = requests.post(url, headers=NOTION_HEADERS, json=body, timeout=10)
        if res.status_code != 200:
            logging.error(f"Failed to fetch prompts: {res.status_code} - {res.text}")
            return []
        return res.json().get("results", [])
    except Exception as e:
        logging.error(f"Error fetching prompts: {e}")
        return []

def ask_chatgpt(prompt):
    """Get ChatGPT response with free tier optimizations"""
    try:
        # Use gpt-3.5-turbo for cost efficiency (free tier friendly)
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,  # Limit tokens for cost control
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        return res.choices[0].message.content
    except Exception as e:
        logging.error(f"Error calling ChatGPT: {e}")
        return f"Error processing request: {str(e)}"

def update_response(page_id, response):
    """Update Notion with response and stealth features"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    # Get current timestamp for the date column
    current_time = datetime.now()
    formatted_date = current_time.strftime("%Y-%m-%d")
    formatted_time = current_time.strftime("%H:%M:%S")
    
    # Truncate response to fit Notion limits (no timestamp in text)
    truncated_response = response[:1900] + "..." if len(response) > 1900 else response
    
    payload = {
        "properties": {
            "Response": {
                "rich_text": [{"text": {"content": truncated_response}}]
            },
            "Status": {"select": {"name": "Done"}},
            "Generated Date": {
                "date": {
                    "start": current_time.isoformat(),
                    "end": None
                }
            }
        }
    }
    
    try:
        # Add random delay to avoid detection
        time.sleep(random.uniform(1.0, 3.0))
        
        res = requests.patch(url, headers=NOTION_HEADERS, json=payload, timeout=10)
        if res.status_code != 200:
            logging.error(f"Failed to update page {page_id}: {res.status_code}")
            return False
        return True
    except Exception as e:
        logging.error(f"Error updating page {page_id}: {e}")
        return False

def continuous_polling():
    """Continuous polling with adaptive intervals"""
    consecutive_empty = 0
    base_interval = 30  # Start with 30 seconds
    
    while True:
        try:
            logging.info("🔄 Checking for prompts...")
            prompts = get_pending_prompts()
            
            if prompts:
                consecutive_empty = 0
                logging.info(f"Found {len(prompts)} pending prompts.")
                
                for p in prompts:
                    prompt_text = p["properties"]["Prompt"]["title"][0]["text"]["content"]
                    page_id = p["id"]
                    logging.info(f"🧠 Processing: {prompt_text[:50]}...")
                    
                    reply = ask_chatgpt(prompt_text)
                    if update_response(page_id, reply):
                        logging.info(f"✅ Updated page: {page_id}")
                    else:
                        logging.error(f"❌ Failed to update page: {page_id}")
                    
                    # Small delay between processing multiple prompts
                    time.sleep(random.uniform(2.0, 5.0))
                
                # If we found work, poll more frequently
                sleep_time = max(10, base_interval - 10)
            else:
                consecutive_empty += 1
                logging.info(f"No pending prompts found. (Empty count: {consecutive_empty})")
                
                # Adaptive polling: slower when no work, faster when work found
                if consecutive_empty > 5:
                    sleep_time = min(300, base_interval + consecutive_empty * 10)  # Max 5 minutes
                else:
                    sleep_time = base_interval
            
            # Add jitter to avoid detection patterns
            jitter = random.uniform(-5, 5)
            actual_sleep = max(5, sleep_time + jitter)
            
            logging.info(f"Sleeping for {actual_sleep:.1f} seconds...")
            time.sleep(actual_sleep)
            
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(60)  # Wait longer on errors

def main():
    """Main function with stealth features"""
    logging.info("🚀 Starting Notion AI Bot with stealth mode...")
    
    # Validate environment variables
    if not all([NOTION_DB_ID, NOTION_API_KEY, OPENAI_API_KEY]):
        logging.error("❌ Missing required environment variables!")
        return
    
    # Start continuous polling
    continuous_polling()

if __name__ == "__main__":
    main()