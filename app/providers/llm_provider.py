import logging
from typing import Any, Optional

from app.core.config import settings
from app.interface.llm_provider import LLMProviderInterface
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProviderInterface):
    """
    LangChain을 통해 OpenAI의 언어 모델과 상호 작용하기 위한 공급자입니다.
    """

    def __init__(
        self,
        model_name: str = settings.OPENAI_MODEL,
        temperature: float = 0.3,
        api_key: Optional[str] = settings.OPENAI_API_KEY,
    ):
        """
        OpenAI 공급자를 초기화합니다.

        Args:
            model_name: 사용할 OpenAI 모델의 이름.
            temperature: 모델의 샘플링 온도.
            api_key: OpenAI API 키.
        """
        if not api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

        self.llm = ChatOpenAI(
            model_name=model_name, temperature=temperature, api_key=api_key
        )
        logger.info(f"OpenAI LLM Provider가 다음 모델로 초기화되었습니다: {model_name}")

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        response = self.llm.invoke(prompt, **kwargs)
        return response.content