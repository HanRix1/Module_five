import redis.asyncio as redis

class RedisClient:
    def __init__(self, host: str = "localhost", port: int = 6379):
        self.host = host
        self.port = port
        self.redis = None

    async def connect(self):
        self.redis = await redis.from_url(f"redis://{self.host}:{self.port}", decode_responses=True)

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    def get_client(self):
        if not self.redis:
            raise RuntimeError("Redis не подключен")
        return self.redis

redis_client = RedisClient(host="redis", port=6379)
