import dramatiq
import logging
import json
from app.core.redis import get_redis_client
from app.schemas.status import TaskResumeStatus
from app.core.db import engine
from sqlmodel import Session
from app.models.resume import Resume
from app.service.resume_service import resume_service
from app.crud import resume_crud
from app.utils.storage import download_resume
import os

logger = logging.getLogger(__name__)

redis_client = get_redis_client()

def update_task_status(message_id: str, status: TaskResumeStatus, result: dict = None):
    """작업 상태를 Redis에 업데이트"""
    task_data = {
        "status": status,
        "result": result if result else {}
    }
    redis_client.set(f"task:{message_id}", json.dumps(task_data))
    redis_client.expire(f"task:{message_id}", 86400)  # 24시간 후 만료


def get_task_status(message_id: str) -> dict:
    """Redis에서 작업 상태 조회"""
    task_data = redis_client.get(f"task:{message_id}")
    if task_data:
        return json.loads(task_data)
    return {"status": TaskResumeStatus.PENDING, "result": {}}


@dramatiq.actor(queue_name="resume_analysis", max_retries=3)
def send_resume_analysis(
    file_url: str,
    original_filename: str,
    upload_filename: str,
    user_id: int,
    task_id: str,
) -> None:
    temp_file_path = None
    try:
        # user_id를 정수형으로 명시적 변환
        user_id = int(user_id)
        
        update_task_status(task_id, TaskResumeStatus.PROCESSING)
        logger.info(f"Starting resume analysis for user: {user_id}, file: {original_filename}")
        
        # Worker 내부에서 새로운 DB 세션 생성
        with Session(engine) as session:

            # 1. 새로운 이력서 생성
            resume_count = len(resume_crud.get_by_user_id(session, user_id))
            version = f"v_{resume_count + 1}.0"

            new_resume = Resume(
                user_id=user_id,
                file_url=file_url,
                original_filename=original_filename,
                upload_filename=upload_filename,
                version=version,
                analysis_result="Sample analysis result"
            )

            resume = resume_crud.create(session, resume=new_resume)

            # 1.5. 파일 다운로드
            temp_file_path = download_resume(upload_filename)
            if not temp_file_path:
                raise Exception("Failed to download file from storage")

            # 2. 파일 파싱 & 청킹
            chunks = resume_service.parse_and_chunk_resume(temp_file_path, upload_filename, original_filename)
            update_task_status(task_id, TaskResumeStatus.PARSING, {"message": "파일 파싱 중입니다."})
            
            # 3. 청크 임베딩
            vectors = resume_service.create_embeddings(chunks)
            update_task_status(task_id, TaskResumeStatus.EMBEDDING, {"message": "임베딩 중 입니다."})
            
            # 4. 청크 저장
            resume_service.save_embeddings_to_db(session, resume.id, chunks, vectors)
            update_task_status(task_id, TaskResumeStatus.SAVING, {"message": "결과를 저장 중입니다."})

            # 분석 완료 후 상태 업데이트
            result = {
                "filename": original_filename,
                "user_id": user_id,
                "analysis_result": "Sample analysis result"  # TODO: 실제 분석 결과로 대체
            }
            update_task_status(task_id, TaskResumeStatus.COMPLETED, result)
        
        logger.info(f"Resume analysis completed for user: {user_id}, file: {original_filename}")
    except Exception as e:
        logger.error(f"Resume analysis failed for user: {user_id}, file: {original_filename}: {str(e)}")
        update_task_status(task_id, TaskResumeStatus.FAILED, {"error": str(e)})
        raise 
    finally:
        # 임시 파일 정리
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.error(f"Failed to delete temporary file {temp_file_path}: {str(e)}") 