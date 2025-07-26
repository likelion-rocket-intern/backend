from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from app.models.embedding import Embedding

class CRUDEmbedding:
    def create(
            self, 
            db: Session, 
            *, 
            object_id: str, 
            object_type: str, 
            embedding: List[float], 
            extra_data: Dict[str, Any]) -> Embedding:
        """
        개별 데이터를 받아 Embedding 객체를 생성하고 DB에 저장합니다.
        """
        embedding_obj = Embedding(
            object_id=object_id,
            object_type=object_type,
            embedding=embedding,
            extra_data=extra_data
        )
        
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

    def get_by_exact_description(self, db: Session, *, description: List[str], object_type: str) -> Embedding | None:
        """
        extra_data 안의 skill 리스트가 정확히 일치하는 데이터를 찾습니다.
        """
        sorted_description = sorted(description)
        statement = select(Embedding).where(
            Embedding.object_type == object_type,
            Embedding.extra_data['description'].astext == str(sorted_description)
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