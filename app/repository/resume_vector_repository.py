import logging
from typing import List

from sqlmodel import Session, select

from app.core.config import settings
from app.interface.resume_vector_repository import ResumeVectorRepositoryInterface
from app.models.resume_embedding import ResumeEmbedding
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_core.documents import Document
from pgvector.sqlalchemy import cosine_distance

logger = logging.getLogger(__name__)


class SqlResumeVectorRepository(ResumeVectorRepositoryInterface):
    """
    SQLModel과 pgvector를 사용하여 이력서 벡터를 관리하는 저장소 구현체.
    """

    def __init__(self, db: Session):
        self.db = db
        self.embeddings = HuggingFaceInstructEmbeddings(
            model_name="intfloat/multilingual-e5-large",
            embed_instruction="query: ",
            query_instruction="",
        )

    def search_similar_chunks(
        self, resume_id: int, query: str, k: int = 5
    ) -> List[Document]:
        query_vector = self.embeddings.embed_query(f"query: {query}")

        # 벡터 정규화 (필요한 경우)
        # query_vector = query_vector / np.linalg.norm(query_vector)

        statement = (
            select(ResumeEmbedding)
            .where(ResumeEmbedding.resume_id == resume_id)
            .order_by(cosine_distance(ResumeEmbedding.embedding, query_vector))
            .limit(k)
        )
        results = self.db.exec(statement).all()
        
        return [Document(page_content=res.chunk, metadata=res.metadata) for res in results]