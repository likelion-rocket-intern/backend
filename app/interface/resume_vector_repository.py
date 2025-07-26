from abc import ABC, abstractmethod
from typing import List

from langchain_core.documents import Document


class ResumeVectorRepositoryInterface(ABC):
    """
    이력서 벡터 데이터 저장소와 상호작용하기 위한 인터페이스.
    """

    @abstractmethod
    def search_similar_chunks(
        self, resume_id: int, query: str, k: int = 5
    ) -> List[Document]:
        """
        주어진 쿼리(예: 채용공고)와 가장 유사한 이력서 청크를 검색합니다.

        Args:
            resume_id: 검색 대상 이력서 ID.
            query: 유사도 검색을 위한 쿼리 텍스트.
            k: 반환할 청크의 수.

        Returns:
            유사도가 높은 순으로 정렬된 Document 객체의 리스트.
        """
        pass