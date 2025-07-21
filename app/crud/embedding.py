from typing import Optional, List
from sqlmodel import Session, select
from app.models.embedding import Embedding

class CRUDEmbedding:
    def create(self, db: Session, *, embedding_obj: Embedding) -> Embedding:
        db.add(embedding_obj)
        db.commit()
        db.refresh(embedding_obj)
        return embedding_obj

    def get(self, db: Session, *, embedding_id: int) -> Optional[Embedding]:
        return db.get(Embedding, embedding_id)

    def get_by_object(self, db: Session, *, object_id: int, object_type: str) -> List[Embedding]:
        statement = select(Embedding).where(
            Embedding.object_id == object_id,
            Embedding.object_type == object_type
        )
        return list(db.exec(statement))
    
    def get_all_by_type(self, db: Session, *, object_type: str) -> List[Embedding]:
        """특정 타입의 모든 임베딩 객체를 조회"""
        statement = select(Embedding).where(Embedding.object_type == object_type)
        results = db.exec(statement).all()
        return list(results)

    def get_by_exact_skills(self, db: Session, *, skills: List[str], object_type: str) -> Embedding | None:
        """
        extra_data 안의 skill 리스트가 정확히 일치하는 데이터를 찾습니다.
        """
        sorted_skills = sorted(skills)
        statement = select(Embedding).where(
            Embedding.object_type == object_type,
            Embedding.extra_data['skill'].astext == str(sorted_skills)
        )
        return db.exec(statement).first()

    def update(self, db: Session, *, embedding_obj: Embedding, **kwargs) -> Embedding:
        for key, value in kwargs.items():
            setattr(embedding_obj, key, value)
        db.add(embedding_obj)
        db.commit()
        db.refresh(embedding_obj)
        return embedding_obj

    def delete(self, db: Session, *, embedding_id: int) -> None:
        obj = db.get(Embedding, embedding_id)
        if obj:
            db.delete(obj)
            db.commit()
            
embedding_crud = CRUDEmbedding()