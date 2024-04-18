from redis.asyncio import Redis

redis = Redis


async def get_redis_instance() -> type[Redis]:
    return redis
