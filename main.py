import os, time, requests
import openai
from openai import OpenAI


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
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    body = {
        "filter": {
            "property": "Status",
            "select": {
                "equals": "Pending"
            }
        }
    }
    res = requests.post(url, headers=NOTION_HEADERS, json=body)
    if res.status_code != 200:
        print(f"❌ Failed to fetch prompts: {res.status_code}")
        print(res.text)
        return []
    return res.json().get("results", [])

def ask_chatgpt(prompt):
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return res.choices[0].message.content


def update_response(page_id, response):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "Response": {
                "rich_text": [{"text": {"content": response[:2000]}}]
            },
            "Status": {"select": {"name": "Done"}}
        }
    }
    requests.patch(url, headers=NOTION_HEADERS, json=payload)

def main():
    while True:
        print("🔄 Checking for prompts...")
        prompts = get_pending_prompts()
        print(f"Found {len(prompts)} pending prompts.")
        for p in prompts:
            prompt_text = p["properties"]["Prompt"]["title"][0]["text"]["content"]
            page_id = p["id"]
            print(f"🧠 Processing: {prompt_text}")
            reply = ask_chatgpt(prompt_text)
            update_response(page_id, reply)
            print(f"✅ Updated page: {page_id}")
        time.sleep(60)

if __name__ == "__main__":
    main()
