import logging
import os
from sqlmodel import Session
from sqlalchemy import Engine
from app.core.db import engine
from app.service.embedding_service import DataEmbedder
from app.repository.sql_embedding_repository import SqlEmbeddingRepository
from app.models.job_profile import JobProfile
from app.models.embedding import Embedding
from sqlmodel import select
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = "datas/" # 데이터셋 폴더 경로 상수 정의

def init_embedding(db_engine: Engine):
    if not os.path.exists(DATA_DIR):
        logger.warning(f"데이터 폴더 '{DATA_DIR}'를 찾을 수 없어 임베딩을 건너뜁니다.")
        return
    
    Embedding.metadata.create_all(db_engine)
    logger.info("`embeddings` 테이블 생성 또는 확인 완료.")

    # DB 세션 생성
    with Session(engine) as session:
        # Repository 인스턴스 생성 (의존성 주입)
        embedding_repository = SqlEmbeddingRepository(session)

        # 데이터 폴더 내의 모든 파일을 순회
        for filename in os.listdir(DATA_DIR):
            # 지원하는 파일 형식(.csv, .json)만 처리
            if filename.endswith((".csv")):
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

def init_job_profiles():
    """직군 프로필 데이터를 JSON 파일에서 읽어 DB에 초기화"""
    
    profile_file_path = os.path.join(DATA_DIR, "jinro_data.json")
    
    if not os.path.exists(profile_file_path):
        logger.warning(f"프로필 파일 '{profile_file_path}'를 찾을 수 없어 프로필 초기화를 건너뜁니다.")
        return
    
    # 한글 직군명 매핑
    job_name_mapping = {
        "backend_developer": "백엔드 개발자",
        "frontend_developer": "프론트엔드 개발자",
        "ai_developer": "AI 개발자",
        "marketer": "마케터",
        "business_development_manager": "사업개발매니저",
        "game_developer": "게임 개발자",
        "ui_ux_designer": "UI/UX 디자이너",
        "embedded_developer": "임베디드 개발자",
        "cloud_engineer": "클라우드 엔지니어",
        "devops_infrastructure": "데브옵스 & 인프라",
        "data_engineer": "데이터 엔지니어",
        "app_developer": "앱 개발자"
    }
    
    with Session(engine) as session:
        try:
            logger.info("직군 프로필 초기화 시작...")
            
            # JSON 파일 읽기
            with open(profile_file_path, 'r', encoding='utf-8') as f:
                profiles_data = json.load(f)
            
            # 기존 직군 타입들을 가져옴
            existing_job_types = {
                profile.job_type 
                for profile in session.exec(select(JobProfile))
            }
            
            # 각 직군 프로필을 DB에 저장 (없는 것만)
            created_count = 0
            skipped_count = 0
            for job_type, profile_data in profiles_data.items():
                # 이미 존재하는 job_type이면 건너뜀
                if job_type in existing_job_types:
                    skipped_count += 1
                    continue
                
                job_profile = JobProfile(
                    job_type=job_type,
                    job_name_ko=job_name_mapping.get(job_type, job_type),
                    stability=profile_data["stability"],
                    creativity=profile_data["creativity"],
                    social_service=profile_data["social_service"],
                    ability_development=profile_data["ability_development"],
                    conservatism=profile_data["conservatism"],
                    social_recognition=profile_data["social_recognition"],
                    autonomy=profile_data["autonomy"],
                    self_improvement=profile_data["self_improvement"],
                    is_active=True
                )
                
                session.add(job_profile)
                created_count += 1
                logger.info(f"직군 프로필 추가: {job_type} ({job_name_mapping.get(job_type, job_type)})")
            
            if created_count > 0:
                session.commit()
                logger.info(f"직군 프로필 초기화 완료. {created_count}개 추가, {skipped_count}개 건너뜀")
            else:
                logger.info(f"추가할 새 직군 프로필이 없습니다. (기존 프로필: {skipped_count}개)")
            
        except FileNotFoundError:
            logger.error(f"프로필 파일 '{profile_file_path}'를 찾을 수 없습니다.")
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파일 파싱 오류: {e}")
        except Exception as e:
            logger.error(f"직군 프로필 초기화 중 오류 발생: {e}")
            session.rollback()
    

def main() -> None:
    logger.info("Starting embedding initialization")
    init_embedding(engine)
    init_job_profiles()
    logger.info("Finished embedding initialization")

if __name__ == "__main__":
    main() 