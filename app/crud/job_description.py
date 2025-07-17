from sqlmodel import Session, select
from typing import Optional, List
from app.models.job_description import JobDescription

class CRUDJobDescription:
    def create(
        self,
        db: Session,
        *,
        job_description: JobDescription
    ) -> JobDescription:
        db.add(job_description)
        db.commit()
        db.refresh(job_description)
        return job_description

    def get_by_id(self, db: Session, id: int) -> Optional[JobDescription]:
        return db.get(JobDescription, id)
    
    # 특정 사용자가 업로드한 모든 JD를 가져오는 메서드 (예시)
    def get_by_user_id(self, db: Session, user_id: int) -> List[JobDescription]:
        query = select(JobDescription).where(JobDescription.user_id == user_id)
        return list(db.exec(query).all())
    
crud_job_description = CRUDJobDescription()
