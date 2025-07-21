import dramatiq
import logging
import json
from app.core.db import engine
from app.core.redis import get_redis_client
from app.schemas.status import TaskJobStatus
from sqlmodel import Session

from app.service.job_analysis_service import JobAnalysisService
from app.crud.user import user_crud
from app.repository.resume_vector_repository import SqlResumeVectorRepository

from app.models.job_description import JobDescription
from app.crud.job_description import job_description_crud
from app.crud.job_description_result import job_description_analysis_result_crud
from app.schemas.job_description import JobDescriptionResultCreate 
from app.providers.embedding_provider import EmbeddingsProvider
from app.providers.llm_provider import OpenAIProvider
from app.providers.prompt_generator import AnalysisPromptGenerator

logger = logging.getLogger(__name__)

redis_client = get_redis_client()

def update_task_status(message_id: str, status: TaskJobStatus, result: dict = None):
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
    return {"status": TaskJobStatus.PENDING, "result": {}}

@dramatiq.actor(queue_name="job_analysis", time_limit=300_000, max_retries=3) 
def send_job_analysis_task(
	task_id: str, 
	user_id: int, 
	resume_id: int, 
	job_description: str):
	"""
	채용 공고와 이력서를 실제로 분석하는 백그라운드 작업
	"""
	logger.info(f"Task {task_id}: Starting job analysis for user_id={user_id}, resume_id={resume_id}")
	update_task_status(task_id, TaskJobStatus.PROCESSING)

	with Session(engine) as session:
		try:
			# 채용공고 DB에 저장
			jd_obj = job_description_crud.create_from_content(
				db=session, content=job_description, resume_id=resume_id
			)

			embeddings_provider = EmbeddingsProvider()
			embeddings_model = embeddings_provider.get_model()

			vector_repo = SqlResumeVectorRepository(db=session, embeddings_model=embeddings_model)
			prompt_generator = AnalysisPromptGenerator()
			llm_provider = OpenAIProvider()
			

			service = JobAnalysisService(
				vector_repo=vector_repo,
				prompt_generator=prompt_generator,
				llm_provider=llm_provider,
			)

			user = user_crud.get(db=session, id=user_id)
			if not user:
				raise ValueError(f"User with id {user_id} not found.")

			analysis_result = service.analyze_job_fit(
				db=session,
				user=user, 
				resume_id=resume_id,
				job_description=job_description
			)

			validated_data = JobDescriptionResultCreate.model_validate(analysis_result)

			job_description_analysis_result_crud.create(
				db=session,
                result_in=validated_data,
                job_description_id=jd_obj.id
			)

			logger.info(f"Task {task_id}: Analysis successful and result saved.")
			update_task_status(task_id, TaskJobStatus.COMPLETED, result=analysis_result)
		except Exception as e:
			logger.error(f"Task {task_id}: Analysis failed. Error: {e}", exc_info=True)
			# 실패 시 에러 메시지를 결과에 담아 상태를 업데이트합니다.
			error_result = {"error": str(e)}
			update_task_status(task_id, TaskJobStatus.FAILED, result=error_result)
			# 에러를 다시 발생시켜 Dramatiq의 재시도 로직이 동작하도록 합니다.
			raise
