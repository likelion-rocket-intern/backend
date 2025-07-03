import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app.core.config import settings

# Redis broker 설정
redis_broker = RedisBroker(url=str(settings.REDIS_BROKER_URL))
dramatiq.set_broker(redis_broker) 