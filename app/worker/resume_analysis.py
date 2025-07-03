import dramatiq
import logging
from typing import Union
import json
from redis import Redis
from enum import Enum

logger = logging.getLogger(__name__)

# Redis 클라이언트 설정
redis_client = Redis(host='localhost', port=6379, db=0)

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


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
    file_content: Union[str, bytes],
    filename: str,
    user_id: str,
) -> None:
    """
    이력서 분석을 수행하는 워커
    
    Args:
        file_content: 이력서 파일 내용 (텍스트 또는 바이너리)
        filename: 파일 이름
        user_id: 사용자 ID
    """
    message_id = dramatiq.get_message_id()
    try:
        update_task_status(message_id, TaskStatus.PROCESSING)
        logger.info(f"Starting resume analysis for user: {user_id}, file: {filename}")
        
        # 파일 내용이 바이너리인 경우 처리
        if isinstance(file_content, bytes):
            try:
                file_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                logger.warning(f"Binary file detected for {filename}")
                # TODO: 바이너리 파일 처리 로직 구현
        
        # TODO: 실제 분석 로직 구현
        # 1. 파일 저장
        # 2. 분석 수행
        # 3. 결과 저장
        
        # 분석 완료 후 상태 업데이트
        result = {
            "filename": filename,
            "user_id": user_id,
            "analysis_result": "Sample analysis result"  # TODO: 실제 분석 결과로 대체
        }
        update_task_status(message_id, TaskStatus.COMPLETED, result)
        
        logger.info(f"Resume analysis completed for user: {user_id}, file: {filename}")
    except Exception as e:
        logger.error(f"Resume analysis failed for user: {user_id}, file: {filename}: {str(e)}")
        update_task_status(message_id, TaskStatus.FAILED, {"error": str(e)})
        raise 