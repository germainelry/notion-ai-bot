# 📅 Notion Database Setup Guide (Async & Fast Mode Ready)

## Required Database Columns

Your Notion database needs these columns for the bot to work properly:

### 1. **Prompt** (Title)

- **Type**: Title
- **Purpose**: Your questions or tasks for the AI
- **Required**: ✅ Yes

### 2. **Status** (Select)

- **Type**: Select
- **Options**:
  - `Pending` (for new prompts)
  - `Done` (for completed prompts)
- **Required**: ✅ Yes

### 3. **Response** (Rich Text)

- **Type**: Rich Text
- **Purpose**: AI-generated responses
- **Required**: ✅ Yes

### 4. **Generated Date** (Date)

- **Type**: Date
- **Purpose**: When the response was generated (includes both date and time)
- **Required**: ✅ Yes

### 5. **Code Output** (Rich Text) - **NEW**

- **Type**: Rich Text
- **Purpose**: Extracted code blocks from AI responses
- **Required**: ✅ Yes (for code-related questions)
- **Note**: This column will contain only the code, making it easy to copy and use

---

## How to Add the New Column

### Add "Generated Date" Column

1. Open your Notion database
2. Click the "+" button to add a new column
3. Select "Date" as the property type
4. Name it exactly: **"Generated Date"**
5. This will store both date and time automatically

### Add "Code Output" Column

1. Open your Notion database
2. Click the "+" button to add a new column
3. Select "Rich Text" as the property type
4. Name it exactly: **"Code Output"**
5. This will store extracted code blocks separately

---

## Example Database Structure

| Prompt                               | Status  | Response                         | Code Output    | Generated Date      |
| ------------------------------------ | ------- | -------------------------------- | -------------- | ------------------- |
| "How do I create a Python function?" | Done    | "To create a Python function..." | `def hello():` | 2024-01-15 14:30:25 |
| "What is the best way to..."         | Pending |                                  |                |                     |

---

## Benefits of This Setup

✅ **Async & Fast Mode**: Bot is fully async and can be set to instant response
✅ **Configurable Delays**: All delays and intervals are configurable via env vars
✅ **Clean Responses**: No timestamp clutter in the response text
✅ **Sortable**: You can sort by generation date
✅ **Filterable**: Filter by date ranges
✅ **Professional**: Clean, organized appearance
✅ **Searchable**: Easy to find responses by date

---

## Testing the Setup

1. Add a new row with a prompt
2. Set status to "Pending"
3. Run your bot: `python main.py` or deploy to Railway
4. Check that "Generated Date" is filled with date and time
5. Verify the response is clean (no timestamp prefix)

---

## Required Notion Integration Permissions

For the bot to work properly, your Notion integration needs these permissions:

### 1. **Database Access**

- **Read content**: To read prompts from the database
- **Update content**: To update responses and status

### 2. **Page Access** (for comment blocks feature)

- **Read content**: To read page content
- **Update content**: To add comment blocks for long responses
- **Insert content**: To add new blocks as comments

### How to Set Permissions:

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Select your integration
3. Under "Capabilities", ensure these are enabled:
   - ✅ **Read content**
   - ✅ **Update content**
   - ✅ **Insert content**

### Note on Comments Feature:

The "additional blocks as comments" feature requires **Insert content** permission. If you don't have this permission:

- Long responses will still be split into multiple parts
- But only the first part will be saved to the Response field
- Additional parts will be logged but not saved to Notion

## Security & Public Repo Notes

- **No secrets or API keys are in this repo.**
- **.env is gitignored and must be created by you.**
- **Safe for public GitHub.**

---

## Troubleshooting

**"Property not found" error:**

- Make sure column names match exactly (case-sensitive)
- Check that the column types are correct

**Date not showing:**

- Ensure the "Generated Date" column is set to Date type
- Check that your Notion integration has edit permissions
