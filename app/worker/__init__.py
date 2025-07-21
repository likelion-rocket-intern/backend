import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import Middleware

from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ModelLoaderMiddleware(Middleware):
    def __init__(self):
        self.loaded = False

    def after_process_boot(self, broker):
        """워커 프로세스가 부팅된 후 호출되는 메서드"""
        if not self.loaded:
            from app.service.resume_service import resume_service
            try:
                logger.info("Loading models in worker master process...")
                resume_service.load_models()
                logger.info("Successfully loaded models in worker master process")
                self.loaded = True
            except Exception as e:
                logger.error(f"Failed to load models in worker master process: {e}")
                raise

# Redis broker 설정
redis_broker = RedisBroker(url=str(settings.REDIS_BROKER_URL))
redis_broker.add_middleware(ModelLoaderMiddleware())
dramatiq.set_broker(redis_broker) 