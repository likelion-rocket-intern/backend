import dramatiq
import logging
import json
import pandas as pd
import threading
from concurrent.futures import ThreadPoolExecutor

from app.core.db import engine
from app.core.redis import get_redis_client
from sqlmodel import Session

from app.schemas.status import TaskJobStatus
from app.schemas.job_description import JobDescriptionResultCreate, JobDescription as JobDescriptionSchema
from app.service.job_analysis_service import JobAnalysisService
from app.crud.user import user_crud
from app.crud.job_description import job_description_crud
from app.crud.embedding import embedding_crud
from app.repository.resume_vector_repository import SqlResumeVectorRepository
from app.providers.main import main_llm_provider, embeddings_provider, prompt_generator
from app.models.job_description import JobDescription as JobDescriptionModel
from app.schemas.job_description import JobDescriptionRequest
from app.utils.crawler.main_crawler import crawl_url

logger = logging.getLogger(__name__)

redis_client = get_redis_client()
JOB_DATA_CSV_PATH = "datas/job_data.csv"
csv_lock = threading.Lock()
background_executor = ThreadPoolExecutor(max_workers=2)


def _save_job_data(job_summary_dict: dict):
	try:
		logger.info(f"Background curation started for: {job_summary_dict.get('name')}")
		job_data = JobDescriptionSchema.model_validate(job_summary_dict)
		job_name = job_data.name
		description = sorted(job_data.description)

		if not job_name or not description:
				logger.warning(f"Job name or descriptions are missing in curation task. Skipping.")
				return

		with Session(engine) as session:
			existing_job = embedding_crud.get_by_exact_description(db=session, description=description, object_type="job")

			if existing_job:
				logger.info(f"Job with identical description for '{job_name}' already exists in Vector DB. Skipping vector save.")
			else:
				logger.info(f"Saving new job data for '{job_name}' to Vector DB.")

				embedding_text = f"{job_name}: {', '.join(description)}"
				vector = embeddings_provider.get_model().embed_query(embedding_text)

				extra_data = {"name": job_name, "description": description}
				embedding_crud.create(
					db=session,
					object_id="0", 
					object_type="job",
					embedding=vector,
					extra_data=extra_data
				)

		# 구분자 사용
		description_string = " | ".join(sorted(job_data.description))

		with csv_lock:
			try:
				# job_data.csv 읽음
				df = pd.read_csv(JOB_DATA_CSV_PATH)
				# 중복 확인
				is_csv_duplicate = ((df['name'] == job_name) & (df['description'] == description_string)).any()
				if not is_csv_duplicate:
					new_row = pd.DataFrame([{"name": job_name, "description": description_string}])
					new_row.to_csv(JOB_DATA_CSV_PATH, mode='a', header=False, index=False, encoding='utf-8-sig')
					logger.info(f"Appended '{job_name}' to {JOB_DATA_CSV_PATH}")
			except FileNotFoundError:
				new_row = pd.DataFrame([{"name": job_name, "description": description_string}])
				new_row.to_csv(JOB_DATA_CSV_PATH, index=False, encoding='utf-8-sig')
				logger.info(f"Created {JOB_DATA_CSV_PATH} with '{job_name}'")
		logger.info(f"Background curation finished for: {job_name}")
	except Exception as e:
		logger.error(f"Error during background job data curation: {e}", exc_info=True)

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

@dramatiq.actor(queue_name="job_analysis", time_limit=300_000, max_retries=1) 
def send_job_analysis_task(
	task_id: str, 
	user_id: int, 
	resume_id: int, 
	job_description: str,
	job_request: dict
	):
	"""
	채용 공고와 이력서를 실제로 분석하는 백그라운드 작업
	"""
	logger.info(f"Task {task_id}: Starting job analysis for user_id={user_id}, resume_id={job_request['resume_id']}, jinro_id={job_request['jinro_id']}")
	update_task_status(task_id, TaskJobStatus.PROCESSING)

	with Session(engine) as session:
		try:
			content = crawl_url(job_request['jd_url'])
			# 채용공고 DB에 저장
			jd_obj = job_description_crud.create_from_content(
                db=session, 
                content=content['raw_data'], 
                jinro_id=job_request['jinro_id'],
                jd_url=job_request['jd_url'],
                resume_id=job_request['resume_id']
            )



			vector_repo = SqlResumeVectorRepository(db=session, embeddings_model=embeddings_provider.get_model())

			service = JobAnalysisService(
				vector_repo=vector_repo,
				prompt_generator=prompt_generator,
				llm_provider=main_llm_provider,
			)

            user = user_crud.get(db=session, id=user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found.")

			analysis_result = service.analyze_job_fit(
				db=session,
				user=user, 
				resume_id=job_request['resume_id'],
				job_description=content['raw_data']
			)
			
			job_details_data = analysis_result.get("job_summary")
			if not job_details_data:
				raise ValueError("LLM analysis result is missing 'job_summary' key.")

			job_details_schema = JobDescriptionSchema.model_validate(job_details_data)
				
			analysis_result_schema = JobDescriptionResultCreate.model_validate(analysis_result)
				

			validated_data = JobDescriptionResultCreate.model_validate(analysis_result)

			job_description_crud.create_jd_and_result(
                db=session, jd_url=jd_url,
                content=job_description,
                job_details=job_details_schema,
                analysis_result=analysis_result_schema
            )

			logger.info(f"Task {task_id}: Analysis successful and result saved.")
			update_task_status(task_id, TaskJobStatus.COMPLETED, result=analysis_result)

			future = background_executor.submit(_save_job_data, job_details_data)

		except Exception as e:
			logger.error(f"Task {task_id}: Analysis failed. Error: {e}", exc_info=True)
			# 실패 시 에러 메시지를 결과에 담아 상태를 업데이트합니다.
			error_result = {"error": str(e)}
			update_task_status(task_id, TaskJobStatus.FAILED, result=error_result)
			# 에러를 다시 발생시켜 Dramatiq의 재시도 로직이 동작하도록 합니다.
			raise
