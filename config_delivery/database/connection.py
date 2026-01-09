from typing import AsyncGenerator
import asyncpg
from fastapi import HTTPException
from config import Config

DATABASE_URL = f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:5432/{Config.DB_NAME}"

class Database:
    def __init__(self) -> None:
        self.pool : asyncpg.Pool | None = None

    async def connect(self):
        """Creates the connection pool on app startup."""
        self.pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,
            min_size=2,
            max_size=20
        )
        print("DB connected succesfully")

    async def disconnect(self):
        """Closes the pool on app shutdown."""
        if self.pool:
            await self.pool.close()
            print("DB Disconnected")
    

db = Database()


async def get_db_conn() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Yields a connection inside a transaction.
    - If the controller raises an error -> Rollback happens automatically.
    - If the controller finishes successfully -> Commit happens automatically.
    """
    if not db.pool:
        raise HTTPException(status_code=500, detail="Database not initialized")

    # 1. Acquire connection from pool
    async with db.pool.acquire() as conn:
        # 2. Start a transaction block
        async with conn.transaction():
            # 3. Give connection to the controller
            yield conn
            # 4. (Implicit) If we get here without error, asyncpg commits.


