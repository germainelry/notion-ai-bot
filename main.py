import os
import time
import requests
import openai

# ✅ Load env vars
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# ✅ Utility: Get correct property keys from Notion
def debug_show_property_keys():
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}"
    res = requests.get(url, headers=NOTION_HEADERS)
    data = res.json()
    print("🧩 Property keys from Notion:")
    for key in data["properties"]:
        print(f"- {key}")
    # Comment this out after verifying once
    # exit()

# ✅ Step 1: Get prompts from Notion
def get_pending_prompts():
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    body = {
        "filter": {
            "property": "Status",
            "select": {
                "equals": "🟡 Pending"
            }
        }
    }
    res = requests.post(url, headers=NOTION_HEADERS, json=body)
    if res.status_code != 200:
        print(f"❌ Failed to fetch prompts: {res.status_code}")
        print(res.text)
        return []
    return res.json().get("results", [])

# ✅ Step 2: Ask GPT-4
def ask_chatgpt(prompt):
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000
    )
    return res.choices[0].message.content.strip()

# ✅ Step 3: Update Notion with response
def update_response(page_id, response):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "Response": {
                "rich_text": [{
                    "text": {
                        "content": response[:2000]  # Notion text field limit
                    }
                }]
            },
            "Status": {
                "select": {"name": "✅ Done"}
            }
        }
    }
    res = requests.patch(url, headers=NOTION_HEADERS, json=payload)
    if res.status_code != 200:
        print(f"❌ Error updating page {page_id}: {res.status_code}")
        print("Response text:", res.text)
    else:
        print(f"✅ Updated Notion page {page_id}.")

# ✅ Main loop
def main():
    # debug_show_property_keys()  # Run once to confirm names
    while True:
        print("🔄 Checking for prompts...")
        prompts = get_pending_prompts()
        for p in prompts:
            try:
                prompt_text = p["properties"]["Prompt"]["title"][0]["text"]["content"]
                page_id = p["id"]
                print(f"🧠 Processing: {prompt_text}")
                reply = ask_chatgpt(prompt_text)
                update_response(page_id, reply)
            except Exception as e:
                print(f"⚠️ Error processing one item: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()
