import aiosqlite
from datetime import datetime
import ast

class MemoryDB:
    def __init__(self, db_path="notion_bot_memory.db"):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    page_id TEXT,
                    prompt TEXT,
                    response TEXT,
                    code_blocks TEXT
                )
            """)
            await db.commit()

    async def add_entry(self, prompt, response, page_id, code_blocks=None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO memory (timestamp, page_id, prompt, response, code_blocks) VALUES (?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), page_id, prompt, response, str(code_blocks or []))
            )
            await db.commit()

    async def get_recent_prompts(self, limit=10):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT prompt, response FROM memory ORDER BY id DESC LIMIT ?", (limit,)) as cursor:
                return await cursor.fetchall()

    async def get_recent_entries(self, limit=10):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT timestamp, prompt, response, code_blocks FROM memory ORDER BY id DESC LIMIT ?", (limit,)) as cursor:
                return await cursor.fetchall()

    async def search_memory(self, query, limit=10):
        import difflib
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT prompt, response, timestamp, code_blocks FROM memory") as cursor:
                all_entries = await cursor.fetchall()
                results = []
                for prompt, response, timestamp, code_blocks in all_entries:
                    similarity = difflib.SequenceMatcher(None, query.lower(), prompt.lower()).ratio()
                    if similarity > 0.3:
                        results.append((similarity, prompt, response, timestamp, code_blocks))
                results.sort(key=lambda x: x[0], reverse=True)
                return results[:limit]

    async def count(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM memory") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def clear(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM memory")
            await db.commit()