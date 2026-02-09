from redis import asyncio as aioredis
from redis import client, utils

from core.config import config


class RedisService:
    __redis: client.Redis = None
    __aioredis: aioredis.Redis = None
    url = config.redis.url

    @classmethod
    def redis(cls) -> client.Redis:
        cls.__redis = utils.from_url(cls.url)
        return cls.__redis

    @classmethod
    def aioredis(cls) -> aioredis.Redis:
        cls.__aioredis = aioredis.from_url(cls.url)
        return cls.__aioredis

    @classmethod
    def close_redis(cls) -> None:
        if not cls.__redis:
            return None

        cls.__redis.close()

    @classmethod
    async def close_aioredis(cls) -> None:
        if not cls.__aioredis:
            return None

        await cls.__aioredis.close()


redis_service = RedisService.aioredis()
