import logging
import os
from redis import Redis
from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.config import settings
from app.core.db import engine

from app.service.embedding_service import DataEmbedder
from app.models.embedding import Embedding
from app.repository.sql_embedding_repository import SqlEmbeddingRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = "datas/" # 데이터셋 폴더 경로 상수 정의

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
    Embedding.metadata.create_all(db_engine)
    logger.info("`embeddings` 테이블 생성 또는 확인 완료.")

    if not os.path.exists(DATA_DIR):
        logger.warning(f"데이터 폴더 '{DATA_DIR}'를 찾을 수 없어 임베딩을 건너뜁니다.")
        return
    
    # DB 세션 생성
    with Session(db_engine) as session:
        # Repository 인스턴스 생성 (의존성 주입)
        embedding_repository = SqlEmbeddingRepository(session)

        # 데이터 폴더 내의 모든 파일을 순회
        for filename in os.listdir(DATA_DIR):
            # 지원하는 파일 형식(.csv, .json)만 처리
            if filename.endswith((".csv", ".json")):
                file_path = os.path.join(DATA_DIR, filename)

                try:
                    logger.info(f"'{file_path}' 데이터 임베딩 시작...")

                    embedder = DataEmbedder(
                        file_path=file_path,
                        repository=embedding_repository
                    )
                    embedder.run()

                    logger.info(f"'{file_path}' 데이터 임베딩 완료.")
                except Exception as e:
                    logger.error(f"'{file_path}' 처리 중 오류 발생: {e}")

def main() -> None:
    logger.info("Initializing service")
    init_db(engine)
    init_redis()
    init_embedding(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
