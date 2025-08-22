from redis.asyncio import Redis
from config import settings

redis: Redis | None = None


async def redis_startup():
    global redis
    try:
        redis = Redis.from_url(str(settings.redis.url), decode_responses=True)
        await redis.ping()
        print("Redis connection opened.")
    except Exception:
        print("Redis connection failed.")


async def redis_shutdown():
    global redis
    if redis:
        await redis.close()
        print("Redis connection closed.")


async def get_redis() -> Redis:
    return redis