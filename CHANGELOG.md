# Changelog

## [2.1.0] - 2025-07-07

### 🆕 Improvements

#### Memory System Migration

- **Memory system migrated from JSON file (`notion_bot_memory.json`) to SQLite database (`notion_bot_memory.db`).**
- **Automatic context retention:** The bot now uses previous prompt/response pairs as context for new prompts, enabling more natural, continuous conversations.
- **Reset command:** You can now reset the memory database with `python main.py reset`.
- **No manual memory management required:** The database is created and updated automatically by the worker service.
- **Persistence note:** On Railway, the database persists as long as the service is running, but may be lost on redeploy/restart unless persistent volumes are used.
- **All references to the old JSON file have been removed from the codebase and documentation.**

---

## [2.0.0] - 2025-07-06

### 🆕 New Features

#### Code Extraction System

- **Automatic code block extraction** from ChatGPT responses
- **Separate "Code Output" column** in Notion database for code storage
- **Code extraction utility** (`extract_code.py`) for extracting code from text files
- **Enhanced code formatting** with clear separators and language indicators
- **Increased token limit** from 500 to 1000 for better code responses

#### Long Response Handling

- **Smart response splitting** for responses over 1900 characters
- **Multi-part storage** with first part in Response field, additional parts as comments
- **Sentence-based splitting** to avoid cutting in the middle of content
- **Clear continuation indicators** showing total number of parts

#### Memory System

- **Persistent memory storage** in `notion_bot_memory.json` (replaced in 2.1.0 by SQLite)
- **Similarity search** for finding similar previous prompts
- **Statistics tracking** for total processed prompts
- **Command-line interface** for viewing memory and searching
- **Automatic memory cleanup** and template creation

#### Developer Tools

- **Code extraction utility** for saving code blocks to files
- **Memory search functionality** for finding previous interactions
- **Enhanced logging** with memory tracking
- **Test scripts** for verifying functionality

### 🔧 Improvements

#### Security & Safety

- **Comprehensive security audit** completed
- **Memory file gitignored** to prevent sensitive data exposure
- **Clean memory template** created for new installations
- **Enhanced .gitignore** for better file protection
- **Security documentation** added

#### Code Quality

- **Unicode fix** for Windows PowerShell compatibility
- **Enhanced error handling** with better logging
- **Improved code organization** and documentation
- **Better exception handling** for missing permissions

#### Documentation

- **Merged README.md and IMPROVEMENTS.md** into comprehensive documentation
- **Updated setup guides** with new features
- **Security audit report** created
- **Changelog** added for version tracking

### 🐛 Bug Fixes

- **Fixed Unicode encoding errors** in Windows PowerShell
- **Resolved response truncation** issues for long responses
- **Fixed code block formatting** for better readability
- **Improved error messages** for missing permissions

### 📁 File Changes

#### Added

- `extract_code.py` - Code extraction utility
- `test_code_extraction.py` - Test script for code extraction
- `notion_bot_memory_template.json` - Clean memory template
- `SECURITY_AUDIT.md` - Security audit report
- `CHANGELOG.md` - This changelog

#### Modified

- `main.py` - Added code extraction, memory system, long response handling
- `README.md` - Merged with improvements documentation
- `.gitignore` - Added memory and data files
- `NOTION_SETUP.md` - Added Code Output column instructions

#### Removed

- `IMPROVEMENTS.md` - Merged into README.md

### 🔒 Security

- ✅ **No hardcoded API keys or secrets**
- ✅ **No database IDs or sensitive URLs**
- ✅ **Environment variables properly handled**
- ✅ **All sensitive files gitignored**
- ✅ **Safe for public repository**

### 📊 Performance

- **Increased token limit** for better responses
- **Optimized memory usage** with efficient storage
- **Improved error recovery** and logging
- **Enhanced async operations** for better performance

### 🚀 Deployment

- **Ready for public repository** sharing
- **Comprehensive documentation** for easy setup
- **Security audit completed** and documented
- **All features tested** and verified

---

## [1.0.0] - Initial Release

### Features

- Basic Notion to ChatGPT integration
- Async polling system
- Configurable delays and intervals
- Web interface for monitoring
- Error handling and logging

### Security

- Environment variable configuration
- No hardcoded secrets
- Basic .gitignore setup
