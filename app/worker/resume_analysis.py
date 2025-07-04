import dramatiq
import logging
import json
from app.core.redis import get_redis_client
from app.schemas.status import TaskStatus
from app.core.db import engine
from sqlmodel import Session
from app.models.resume import Resume
from app.crud import resume_crud
import os

logger = logging.getLogger(__name__)

redis_client = get_redis_client()

def update_task_status(message_id: str, status: TaskStatus, result: dict = None):
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
    return {"status": TaskStatus.PENDING, "result": {}}


@dramatiq.actor(queue_name="resume_analysis", max_retries=3)
def send_resume_analysis(
    file_path: str,
    filename: str,
    user_id: int,
    task_id: str,
) -> None:
    try:
        update_task_status(task_id, TaskStatus.PROCESSING)
        logger.info(f"Starting resume analysis for user: {user_id}, file: {filename}")
        
        # Worker 내부에서 새로운 DB 세션 생성
        with Session(engine) as session:
            # 파일 처리
            with open(file_path, 'rb') as f:
                # 여기서 파일 분석 작업 수행
                # 필요시 session을 사용하여 DB 작업 수행
                pass
            
            # TODO: 실제 분석 로직 구현
            # 1. 파일 저장
            # 2. 분석 수행
            # 3. 결과 저장 (session 사용)

            resume_count = len(resume_crud.get_by_user_id(session, user_id))
            version = f"v_{resume_count + 1}.0"

            new_resume = Resume(
                user_id=user_id,
                file_path=file_path,
                version=version,
                analysis_result="Sample analysis result"
            )

            resume_crud.create(session, resume=new_resume)
            
            # 분석 완료 후 상태 업데이트
            result = {
                "filename": filename,
                "user_id": user_id,
                "analysis_result": "Sample analysis result"  # TODO: 실제 분석 결과로 대체
            }
            update_task_status(task_id, TaskStatus.COMPLETED, result)

            # os.remove(file_path)
        
        logger.info(f"Resume analysis completed for user: {user_id}, file: {filename}")
    except Exception as e:
        logger.error(f"Resume analysis failed for user: {user_id}, file: {filename}: {str(e)}")
        update_task_status(task_id, TaskStatus.FAILED, {"error": str(e)})
        raise 