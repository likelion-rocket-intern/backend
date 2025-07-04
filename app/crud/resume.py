from sqlmodel import Session, select
from app.models.resume import Resume
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

class CRUDResume:
    def create(
        self,
        db: Session,
        *,
        resume: Resume
    ) -> Resume:
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    def get_by_id(
        self,
        db: Session,
        resume_id: int
    ) -> Optional[Resume]:
        statement = select(Resume).where(Resume.id == resume_id)
        return db.exec(statement).first()

    def get_by_user_id(
        self,
        db: Session,
        user_id: int
    ) -> list[Resume]:
        statement = select(Resume).where(Resume.user_id == user_id)
        return db.exec(statement).all()

    def get_with_user(
        self,
        db: Session,
        resume_id: int
    ) -> Optional[Resume]:
        # join을 사용할 경우
        statement = select(Resume).where(Resume.id == resume_id).options(selectinload(Resume.user))
        return db.exec(statement).first()

resume_crud = CRUDResume()