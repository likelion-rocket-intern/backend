from abc import ABC, abstractmethod
from typing import List
import numpy as np

class EmbeddingProviderInterface(ABC):
    @abstractmethod
    def create_embedding(self, text: str) -> List[float]:
        """하나의 텍스트에 대한 임베딩 벡터를 생성합니다."""
        pass