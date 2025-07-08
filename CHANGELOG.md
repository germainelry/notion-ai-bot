# Changelog

## [2.1.0] - 2025-07-07

- Migrated memory system from JSON to SQLite (`notion_bot_memory.db`)
- Context retention: previous prompt/response pairs now used as context for ChatGPT
- Added `python main.py reset` command to clear memory
- All memory management is now automatic; no manual intervention needed
- Old JSON memory file and references removed

## [2.0.0] - 2025-07-06

- Code extraction: automatic code block extraction and storage in Notion
- Long response handling: smart splitting and multi-part storage
- Memory system: persistent storage, similarity search, CLI for viewing/searching
- Developer tools: code extraction utility, memory search, enhanced logging
- Security: test, audit, secrets are safely stored in .env
- Documentation: merged and updated guides, changelog added
- Performance: increased token limit, optimized memory usage, improved async
- Deployment: ready for public repo, comprehensive docs, all features tested

## [1.0.0] - Initial Release

- Notion to ChatGPT integration
- Async polling system
- Configurable delays and intervals
- Web dashboard for monitoring
- Error handling and logging
- Secure environment variable setup
