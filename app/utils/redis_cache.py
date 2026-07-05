import logging
import os

import redis

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)


def get_cached_data(key):
    try:
        return redis_client.get(key)
    except Exception as e:
        logger.warning(f"Redis connection failed (get): {e}")
        return None


def set_cached_data(key, value, expiry=300):
    try:
        redis_client.set(key, value, ex=expiry)
        return True
    except Exception as e:
        logger.warning(f"Redis connection failed (set): {e}")
        return False


def delete_cached_data(key):
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Redis connection failed (delete): {e}")
        return False
