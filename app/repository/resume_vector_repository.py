import logging
from typing import List

from sqlmodel import Session, select

from app.core.config import settings
from app.interface.resume_vector_repository import ResumeVectorRepositoryInterface
from app.models.resume import ResumeEmbedding
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class SqlResumeVectorRepository(ResumeVectorRepositoryInterface):
    """
    SQLModel과 pgvector를 사용하여 이력서 벡터를 관리하는 저장소 구현체.
    """

    def __init__(self, db: Session, embeddings_model: Embeddings):
        self.db = db
        self.embeddings = embeddings_model

    def search_similar_chunks(
        self, resume_id: int, query: str, k: int = 5
    ) -> List[Document]:
        query_vector = self.embeddings.embed_query(f"query: {query}")

        # 벡터 정규화 (필요한 경우)
        # query_vector = query_vector / np.linalg.norm(query_vector)

        statement = (
            select(ResumeEmbedding)
            .where(ResumeEmbedding.resume_id == resume_id)
            .order_by(ResumeEmbedding.embedding.cosine_distance(query_vector))
            .limit(k)
        )
        results = self.db.exec(statement).all()
        
        return [Document(page_content=res.content,metadata={
            'id': res.id, 
            'resume_id': res.resume_id,
            'chunk_index': res.chunk_index
        }) for res in results]