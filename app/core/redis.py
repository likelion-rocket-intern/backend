from redis import Redis
from app.core.config import settings

def get_redis_client() -> Redis:
    """Redis 클라이언트 인스턴스 생성"""
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        socket_timeout=1,
    )