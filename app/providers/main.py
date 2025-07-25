import logging

from .embedding_provider import EmbeddingsProvider
from .llm_provider import OpenAIProvider
from .prompt_generator import AnalysisPromptGenerator

""" 
Provider 레지스트리 방식
"""

# 여러 LLM 인스턴스를 관리하기 위한 main provider

logger = logging.getLogger(__name__)

main_llm_provider = OpenAIProvider(model_name="gpt-4o", temperature=0.1)
logger.info("main_llm_provider initialized successfully.")


# scheduler_llm_provider = OpenAIProvider(model_name="gpt-3.5-turbo", temperature=0.5)
# logger.info("scheduler_llm_provider initialized successfully.")


embeddings_provider = EmbeddingsProvider()
prompt_generator = AnalysisPromptGenerator()