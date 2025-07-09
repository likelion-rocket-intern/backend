from app.crud.embedding import embedding_crud
from app.models.embedding import Embedding
from typing import List

class SqlEmbeddingRepository:
    def __init__(self, db):
        self.db = db

    def exists(self, object_id: int, object_type: str) -> bool:
        return bool(embedding_crud.get_by_object(self.db, object_id=object_id, object_type=object_type))

    def save(self, embedding: Embedding) -> None:
        embedding_crud.create(self.db, embedding_obj=embedding)

    def get_all_by_type(self, object_type: str) -> List[Embedding]:
        """
        특정 타입의 모든 임베딩 객체를 조회합니다.
        실제 로직은 CRUD 계층에 위임합니다.
        """
        return embedding_crud.get_all_by_type(self.db, object_type=object_type)