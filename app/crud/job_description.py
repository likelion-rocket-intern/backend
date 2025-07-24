from sqlmodel import Session
from app.models.job_description import JobDescription
from app.schemas.job_description import JobDescriptionRequest

class CRUDJobDescription:
    def create_from_content(self, db: Session, *, content: str, resume_id: int, jinro_id: int, jd_url: str) -> JobDescription:
        """
        데이터베이스에 새로운 채용 공고 내용을 저장합니다.
        """

        db_obj = JobDescription(
            content=content,
            resume_id=resume_id,
            jinro_id=jinro_id,
            jd_url=jd_url
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
job_description_crud = CRUDJobDescription()