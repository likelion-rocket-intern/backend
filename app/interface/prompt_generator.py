from abc import ABC, abstractmethod
from typing import List

from langchain_core.documents import Document


class PromptGeneratorInterface(ABC):
    """
    LLM에 전달할 프롬프트를 생성하기 위한 인터페이스.
    """

    @abstractmethod
    def create_job_fit_prompt(
        self, job_description: str, resume_chunks: List[Document]
    ) -> str:
        """
        채용 공고와 이력서 청크를 기반으로 직무 적합도 분석 프롬프트를 생성합니다.
        """
        pass