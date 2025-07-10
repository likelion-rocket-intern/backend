import logging
import os
from sqlmodel import Session

from app.core.db import engine
from app.service.embedding_service import DataEmbedder
from app.repository.sql_embedding_repository import SqlEmbeddingRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = "datas/" # 데이터셋 폴더 경로 상수 정의

def init_embedding():
    if not os.path.exists(DATA_DIR):
        logger.warning(f"데이터 폴더 '{DATA_DIR}'를 찾을 수 없어 임베딩을 건너뜁니다.")
        return
    
    # DB 세션 생성
    with Session(engine) as session:
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
    logger.info("Starting embedding initialization")
    init_embedding()
    logger.info("Finished embedding initialization")

if __name__ == "__main__":
    main() 