from datetime import datetime
from typing import Annotated

from fastapi import Depends, Request

from core.config import settings
from core.exceptions import TooManyRequestsException
from core.logger import logger
from services.cache import RedisCacheService, get_cache_service


async def apply_rate_limit(
    request: Request,
    cache: Annotated[RedisCacheService, Depends(get_cache_service)],
) -> None:
    """
    Проверяет количество запросов с определенного хоста
     и возвращает ошибку при превышении лимита.
    """
    timestamp = datetime.now().timestamp()
    interval_sec = 60
    client_host = str(request.client.host)
    pipe = await cache.get_pipeline()
    # Удаление истекших значений
    await pipe.zremrangebyscore(client_host, 0, timestamp - interval_sec)
    # Получение количества неистекших запросов
    await pipe.zcard(client_host)
    # Добавление текущего запроса в Redis
    await pipe.zadd(client_host, {str(timestamp): timestamp})
    # Все элементы множества после добавления запроса (записи timestamp)
    await pipe.zrange(client_host, 0, -1)
    # Устанавливаем время существования ключа
    await pipe.expire(client_host, interval_sec)
    # Выполнение пайплайна Redis-команд
    result: list = await pipe.execute()
    number_requests = len(result[3])
    # Проверка на превышение лимита запросов
    if number_requests > settings.request_limit_per_minute:
        logger.exception(f"{number_requests} requests/min for {client_host}")
        raise TooManyRequestsException
