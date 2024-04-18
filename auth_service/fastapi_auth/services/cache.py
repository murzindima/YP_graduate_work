from abc import ABC, abstractmethod
from datetime import timedelta
from functools import lru_cache

from fastapi import Depends
from redis.asyncio import Redis

from db.redis import get_redis_instance


class CacheService(ABC):
    """Абстрактный класс-интерфейс для сервисов кэширования"""

    @abstractmethod
    async def add_to_set(self, *args, **kwargs):
        """Записывает значение в множество."""
        raise NotImplementedError

    @abstractmethod
    async def is_value_in_set(self, *args, **kwargs):
        """Проверяет, есть ли значение в множестве."""
        raise NotImplementedError

    @abstractmethod
    async def get_pipeline(self, *args, **kwargs):
        """Возвращает pipline."""
        raise NotImplementedError


class RedisCacheService(CacheService):
    def __init__(self, redis_instance: Redis) -> None:
        self.redis = redis_instance

    async def add_to_set(
        self, key: str, value: str, expire_sec: int | timedelta
    ) -> None:
        """Записывает значение в множество."""

        await self.redis.sadd(key, value)
        await self.redis.expire(key, expire_sec)

    async def is_value_in_set(self, key: str, value: str) -> bool:
        """Проверяет, есть ли значение в множестве."""

        is_value = await self.redis.sismember(key, value)
        return is_value

    async def get_pipeline(self):
        """Возвращает redis pipeline."""

        return self.redis.pipeline()


@lru_cache()
def get_cache_service(
    redis_instance: Redis = Depends(get_redis_instance),
) -> CacheService:
    return RedisCacheService(redis_instance)
