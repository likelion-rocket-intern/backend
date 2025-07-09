from app.crud.embedding import embedding_crud
from app.models.embedding import Embedding

class SqlEmbeddingRepository:
    def __init__(self, db):
        self.db = db

    def exists(self, object_id: int, object_type: str) -> bool:
        return bool(embedding_crud.get_by_object(self.db, object_id=object_id, object_type=object_type))

    def save(self, embedding: Embedding) -> None:
        embedding_crud.create(self.db, embedding_obj=embedding)
