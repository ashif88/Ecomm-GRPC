import redis

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_cached_data(key):
    return redis_client.get(key)

def set_cached_data(key, value, expiry=300):
    redis_client.set(key, value, ex=expiry)
