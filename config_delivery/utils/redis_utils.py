from redis import Redis
import redis.asyncio as aioredis
from redis.exceptions import ConnectionError
from config import Config

class Cache:
    def __init__(self, host='127.0.0.1', port=6379, db=0):
        # self.redis = Redis(host=host, port=port, db=db, decode_responses=True)
        self.redis =  aioredis.Redis(host=host, port=port, db=db, decode_responses=True)
        # self.redis = Redis.from_url(f"rediss://default:{Config.REDIS_PASSWORD}@organic-guppy-35039.upstash.io:6379", decode_responses=True)
        self.key = {}
        try:
            self.redis.ping()
        except ConnectionError:
            raise ConnectionError("Could not connect to Redis server")

    async def set(self, key, value, ex=None):
        """Set a value in the cache with an optional expiration time."""
        await self.redis.set(key, value, ex=ex)

    async def get(self, key):
        """Get a value from the cache."""
        return await self.redis.get(key)

    async def delete(self, key):
        """Delete a key from the cache."""
        await self.redis.delete(key)
        print(f"Cache key '{key}' deleted.")

    async def exists(self, key):
        """Check if a key exists in the cache."""
        return await self.redis.exists(key)

    async def clear(self):
        """Clear the entire cache."""
        await self.redis.flushdb()


cache = Cache()  # Create a global cache instance