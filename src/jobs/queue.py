import redis
from rq import Queue, Retry

from src.core.settings import settings

redis_connection = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)

email_queue = Queue("emails", connection=redis_connection)

email_retry = Retry(max=3, interval=[10, 30, 60])
