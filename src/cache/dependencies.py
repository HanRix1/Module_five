from typing import AsyncGenerator
from fastapi import Depends
from redis import Redis
import redis.asyncio as redis

from cache.cache_client import RedisCache

async def get_redis_client() -> AsyncGenerator[Redis, None]:
    # client = await redis.from_url(f"redis://{self.host}:{self.port}", decode_responses=True)
    client = await redis.from_url(f"redis://localhost:6379", decode_responses=True)
    yield client
    await client.aclose()


async def get_redis_cache(redis_client: Redis = Depends(get_redis_client)) -> RedisCache:
    return RedisCache(redis_client)