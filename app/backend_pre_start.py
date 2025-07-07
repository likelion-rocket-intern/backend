import logging

from redis import Redis
from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.config import settings
from app.core.db import engine

from app.service.embedding_service import DataEmbedder
from app.repository.sql_embedding_repository import SqlEmbeddingRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init_db(db_engine: Engine) -> None:
    try:
        with Session(db_engine) as session:
            # Try to create session to check if DB is awake
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init_redis() -> None:
    try:
        redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            socket_timeout=1,
        )
        redis_client.ping()
        logger.info("Successfully connected to Redis")
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
        raise e
    finally:
        redis_client.close()

def init_embedding(db_engine):
    # DB 세션 생성
    with Session(db_engine) as session:
        # Repository 인스턴스 생성 (의존성 주입)
        embedding_repository = SqlEmbeddingRepository(session)

        # 임베딩 서비스 인스턴스에 repository 주입
        resume_embedder = DataEmbedder(
            "datas/resume_data.csv",
            column="attribute",
            repository=embedding_repository
        )
        resume_embedder.run()

        job_embedder = DataEmbedder(
            "datas/job_data.csv",
            column="name",
            repository=embedding_repository
        )
        job_embedder.run()

def main() -> None:
    logger.info("Initializing service")
    init_db(engine)
    init_redis()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
