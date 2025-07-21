import dramatiq
import logging
import pandas as pd
from sqlmodel import Session
from app.core.db import engine
from app.providers.embedding_provider import EmbeddingsProvider
from app.crud.embedding import embedding_crud
from app.schemas.job_description import JobSummarySchema

logger = logging.getLogger(__name__)
JOB_DATA_CSV_PATH = "datas/job_data.csv"

@dramatiq.actor(queue_name="data_curation", max_retries=2)
def add_job_data_task(job_summary: JobSummarySchema):
	"""
    분석된 직무 데이터를 CSV와 벡터 DB에 추가하는 작업
    """
	try:
		job_data = JobSummarySchema(**job_summary)
		job_name = job_data.name
		skills = sorted(job_data.skill)
	except Exception as e:
		logger.error(f"Invalid job_summary format: {job_summary}. Error: {e}")
		return

	if not job_name or not skills:
		logger.warning(f"Job name or skills are missing: {job_summary}. Skipping.")
		return
	
	logger.info(f"Curating new job data for: {job_name}")

	# 벡터 DB 중복 검사 및 추가
	with Session(engine) as session:
		existing_job = embedding_crud.get_by_exact_skills(
            db=session, skills=skills, object_type="job"
        )

		if existing_job:
			logger.info(f"Job with identical skills for '{job_name}' already exists in Vector DB. Skipping.")
		else:
			logger.info(f"Saving new job data for '{job_name}' to Vector DB.")
			embeddings_provider = EmbeddingsProvider()

			embedding_text = f"{job_name}: {', '.join(skills)}"
			vector = embeddings_provider.get_model().embed_query(embedding_text)

			# extra_data 구성
			extra_data = {"name": job_name, "skill": skills}

			embedding_crud.create(
                db=session,
                object_id="0",
                object_type="job",
                embedding=vector,
                extra_data=extra_data
            )

		# CSV 파일에 데이터 추가
		try:
			df = pd.read_csv(JOB_DATA_CSV_PATH)
			skill_string = ", ".join(skills)
			is_csv_duplicate = ((df['name'] == job_name) & (df['skill'] == skill_string)).any()

			if not is_csv_duplicate:
				new_row = pd.DataFrame([{"name": job_name, "skill": skill_string}])
				new_row.to_csv(JOB_DATA_CSV_PATH, mode='a', header=False, index=False, encoding='utf-8-sig')
				logger.info(f"Appended '{job_name}' to {JOB_DATA_CSV_PATH}")
			else:
				logger.info(f"Job with identical name and skills already exists in {JOB_DATA_CSV_PATH}. Skipping.")
            
		except FileNotFoundError:
			new_row = pd.DataFrame([{"name": job_name, "skill": ", ".join(skills)}])
			new_row.to_csv(JOB_DATA_CSV_PATH, index=False, encoding='utf-8-sig')
			logger.info(f"Created {JOB_DATA_CSV_PATH} with '{job_name}'")