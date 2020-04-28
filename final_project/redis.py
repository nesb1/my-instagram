from functools import lru_cache
from typing import Optional

import aioredis
from aioredis import Redis as AsyncRedis
from final_project.config import redis_settings
from redis import Redis
from rq import Queue


class RedisInstances:
    _async_redis: Optional[AsyncRedis] = None

    @staticmethod
    @lru_cache
    def sync_redis() -> Redis:
        return Redis(redis_settings.redis_address)

    @staticmethod
    async def async_redis() -> AsyncRedis:
        if RedisInstances._async_redis:
            return RedisInstances._async_redis
        return await aioredis.create_redis(f'redis://{redis_settings.redis_address}')

    @staticmethod
    @lru_cache
    def redis_queue() -> Queue:
        return Queue(connection=RedisInstances.sync_redis())
