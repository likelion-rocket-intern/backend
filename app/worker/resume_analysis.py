import dramatiq
import logging
import json
from app.core.redis import get_redis_client
from app.schemas.status import TaskResumeStatus
from app.core.db import engine
from sqlmodel import Session
from app.models.resume import Resume, ResumeEmbedding, ResumeKeyword
from app.service.resume_service import resume_service
from app.crud import resume_crud
from app.utils.storage import download_resume, delete_resume
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
        user_id = int(user_id)
        update_task_status(task_id, TaskResumeStatus.PROCESSING)
        logger.info(f"Starting resume analysis for user: {user_id}, file: {original_filename}")
        
        with Session(engine) as session:
            with session.begin():  # 트랜잭션 시작
                # 1. 새로운 이력서 생성
                resume_count = len(resume_crud.get_by_user_id(session, user_id))
                version = f"v_{resume_count + 1}.0"

                new_resume = Resume(
                    user_id=user_id,
                    file_url=file_url,
                    original_filename=original_filename,
                    upload_filename=upload_filename,
                    version=version,
                    analysis_result="Processing"
                )

                # 1.5. 파일 다운로드
                temp_file_path = download_resume(upload_filename)
                if not temp_file_path:
                    raise Exception("Failed to download file from storage")

                # 2. 파일 파싱 & 청킹
                chunks, similar_words_list = resume_service.parse_and_chunk_resume(temp_file_path, upload_filename, original_filename)
                update_task_status(task_id, TaskResumeStatus.PARSING, {"message": "파일 파싱 중입니다."})
                
                # 3. 청크 임베딩
                vectors = resume_service.create_embeddings(chunks)
                update_task_status(task_id, TaskResumeStatus.EMBEDDING, {"message": "임베딩 중 입니다."})
                
                # 4. Resume와 Embeddings 한번에 저장
                new_resume.resume_embeddings = [
                    ResumeEmbedding(
                        chunk_index=idx,
                        content=chunk.page_content,
                        embedding=vector
                    )
                    for idx, (chunk, vector) in enumerate(zip(chunks, vectors))
                ]

                # similar_words_list를 ResumeKeyword로 변환하여 저장
                new_resume.resume_keywords = [
                    ResumeKeyword(
                        keyword=similar_word["word"],
                        similar_to=similar_word["similar_to"],
                        similarity=similar_word["similarity"],
                        frequency=similar_word["frequency"]
                    )
                    for similar_word in similar_words_list
                ]
                
                # 5. 한 트랜잭션으로 저장
                session.add(new_resume)
                
                # # 분석 결과 업데이트
                # new_resume.analysis_result = "Analysis completed"
                
                # 트랜잭션 자동 commit
                # --- 5. (확장) 이력서 종합 적합도 분석 ---
                update_task_status(task_id, TaskResumeStatus.SCORING, {"message": "종합 적합도를 분석 중입니다."})
                # 새로 생성된 이력서의 벡터를 사용하여 종합 분석 서비스 호출
                analysis_result = resume_service.analyze_resume_fitness(session, resume_vectors=vectors)


                # --- 5. (확장) 이력서 종합 적합도 분석 ---
                update_task_status(task_id, TaskResumeStatus.SCORING, {"message": "종합 적합도를 분석 중입니다."})
                # 새로 생성된 이력서의 벡터를 사용하여 종합 분석 서비스 호출
                analysis_result = resume_service.analyze_resume_fitness(session, resume_vectors=vectors)

                new_resume.analysis_result = analysis_result
                session.add(new_resume) # 변경된 객체 세션에 추가
                session.flush()
                session.refresh(new_resume) # DB에서 최신 상태로 새로고침
                session.commit() # DB에 변경사항 반영
            
            # 분석 완료 후 상태 업데이트
            result = {
                "filename": original_filename,
                "user_id": user_id,
                "resume_id": new_resume.id,
                "analysis_result": analysis_result  # 로 변환 완료
            }
            update_task_status(task_id, TaskResumeStatus.COMPLETED, result)
        
        logger.info(f"Resume analysis completed for user: {user_id}, file: {original_filename}")
    except Exception as e:
        logger.error(f"Resume analysis failed for user: {user_id}, file: {original_filename}: {str(e)}")
        delete_resume(upload_filename)
        update_task_status(task_id, TaskResumeStatus.FAILED, {"error": str(e)})
        raise 
    finally:
        # 임시 파일 정리
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.error(f"Failed to delete temporary file {temp_file_path}: {str(e)}") 
