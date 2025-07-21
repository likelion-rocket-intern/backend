from sqlmodel import Session, select
from typing import Optional, List
from app.models.job_description_result import JobDescriptionResult
from app.schemas.job_description import JobDescriptionResultCreate

class CRUDJobDescriptionResult:
    def create(
        self,
        db: Session,
        *,
        result: JobDescriptionResultCreate,
        job_description_id: int
    ) -> JobDescriptionResult:
        result_dict = result.model_dump()

        db_obj = JobDescriptionResult(
            result=result_dict,
            job_description_id=job_description_id
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return result

    def get_by_id(self, db: Session, id: int) -> Optional[JobDescriptionResult]:
        return db.get(JobDescriptionResult, id)

    def get_by_resume_id(self, db: Session, resume_id: int) -> List[JobDescriptionResult]:
        query = select(JobDescriptionResult).where(JobDescriptionResult.resume_id == resume_id)
        return list(db.exec(query).all())


job_description_analysis_result_crud = CRUDJobDescriptionResult()
