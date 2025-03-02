from datetime import datetime
import json
from typing import Any
from typing import AsyncGenerator

from redis import Redis
from fastapi import Depends



class RedisCache:
    def __init__(self, redis_client: Redis):
        self._redis_client = redis_client

    async def get_cached_data(self, cache_key: str) -> Any | None:
        cached_data = await self._redis_client.get(cache_key)
        return cached_data

    async def set_cached_data(self, cache_key: str, time_left: datetime, data: str) -> None:
        await self._redis_client.setex(cache_key, time_left.seconds, json.dumps(data))
