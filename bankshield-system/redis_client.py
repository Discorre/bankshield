import redis
import os

redis_client = redis.Redis(
    host='redis',  # Имя сервиса в docker-compose
    port=6379,
    db=0
)

# Или через URL:
redis_client = redis.from_url(os.getenv("REDIS_URL"))