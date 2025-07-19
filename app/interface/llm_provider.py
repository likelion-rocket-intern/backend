from abc import ABC, abstractmethod
from typing import Any


class LLMProviderInterface(ABC):
    """
    LLM 공급자를 위한 추상 기본 클래스(ABC).
    """

    @abstractmethod
    def invoke(self, prompt: str, **kwargs: Any) -> str:
        """
        주어진 프롬프트로 언어 모델을 호출합니다.

        Args:
            prompt: 모델에 대한 입력 텍스트.
            **kwargs: 모델 호출을 위한 추가 키워드 인수.

        Returns:
            언어 모델의 응답을 문자열로 반환합니다.
        """
        pass