from sqlmodel import Session, select
from app.models.resume import Resume, ResumeEmbedding
from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from langchain_core.documents import Document

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

    def bulk_create_embeddings(
        self,
        db: Session,
        resume_id: int,
        chunks: List[Document],
        vectors: List[List[float]]
    ) -> List[ResumeEmbedding]:
        """
        청크와 임베딩을 DB에 일괄 저장
        """
        try:
            embedding_records = []
            
            for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
                embedding_record = ResumeEmbedding(
                    resume_id=resume_id,
                    chunk_index=i,
                    content=chunk.page_content,
                    embedding=vector
                )
                
                db.add(embedding_record)
                embedding_records.append(embedding_record)
            
            db.commit()
            return embedding_records
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save embeddings: {str(e)}"
            )

resume_crud = CRUDResume()