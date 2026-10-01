import json
import redis

from src.core.settings import settings

# =========== REDIS CLIENT ==================
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


# ============= SET CACHE =====================
def set_cache(key: str, value: str, expire: int | None = None):
    value = json.dumps(value)

    if expire:
        redis_client.set(key, value, ex=expire)
    else:
        redis_client.set(key, value)


# ============= GET CACHE =====================
def get_cache(key: str):
    value = redis_client.get(key)

    if value is None:
        return None

    return json.loads(value)


# ============= DELETE CACHE =====================
def delete_cache(key: str):
    redis_client.delete(key)


# ============= DELETE USER TASK CACHE =====================
def delete_user_task_cache(user_id: int):
    pattern = f"tasks:user:{user_id}:*"

    keys = redis_client.keys(pattern)

    if keys:
        redis_client.delete(*keys)


# ============= INCREMENT COUNTER =====================
def increment_counter(key: str, expire: int):
    count = redis_client.incr(key)

    if count == 1:
        redis_client.expire(key, expire)

    return count
