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

---

## How to Add the New Column

### Add "Generated Date" Column

1. Open your Notion database
2. Click the "+" button to add a new column
3. Select "Date" as the property type
4. Name it exactly: **"Generated Date"**
5. This will store both date and time automatically

---

## Example Database Structure

| Prompt                               | Status  | Response                         | Generated Date      |
| ------------------------------------ | ------- | -------------------------------- | ------------------- |
| "How do I create a Python function?" | Done    | "To create a Python function..." | 2024-01-15 14:30:25 |
| "What is the best way to..."         | Pending |                                  |                     |

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
