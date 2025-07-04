from sqlmodel import Session
from app.crud.resume import resume_crud
from app.models.resume import Resume
from typing import Optional, List
from fastapi import HTTPException

class ResumeService:
    def create(
        self,
        db: Session,
        *,
        resume: Resume
    ) -> Resume:
        return resume_crud.create(db=db, resume=resume)

    def get_by_id(
        self,
        db: Session,
        resume_id: int
    ) -> Optional[Resume]:
        resume = resume_crud.get_by_id(db=db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume

    def get_by_user_id(
        self,
        db: Session,
        user_id: int
    ) -> List[Resume]:
        resumes = resume_crud.get_by_user_id(db=db, user_id=user_id)
        return resumes

    def get_with_user(
        self,
        db: Session,
        resume_id: int
    ) -> Optional[Resume]:
        resume = resume_crud.get_with_user(db=db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume

    def delete(
        self,
        db: Session,
        resume_id: int
    ) -> None:
        resume = self.get_by_id(db=db, resume_id=resume_id)
        if resume:
            db.delete(resume)
            db.commit()

resume_service = ResumeService()
