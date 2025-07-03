import dramatiq
import logging
from typing import Union

logger = logging.getLogger(__name__)


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
    try:
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
        
        logger.info(f"Resume analysis completed for user: {user_id}, file: {filename}")
    except Exception as e:
        logger.error(f"Resume analysis failed for user: {user_id}, file: {filename}: {str(e)}")
        raise 