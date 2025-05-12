import redis
import os

redis_client = redis.Redis(
    host='redis',
    port=6379,
    db=0
)

redis_client = redis.from_url(os.getenv("REDIS_URL"))