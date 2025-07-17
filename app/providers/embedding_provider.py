from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from app.core.config import settings
from typing import Optional
import torch

class EmbeddingsProvider:
    """ 임베딩 모델을 로드하는 Provider 클래스"""
    def __init__(
            self,
            model_name : str = f"{settings.EMBBEDING_MODEL}" ,
            device: Optional[str] = None,
            normalize_embeddings: bool = True
                 ):
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.normalize_embeddings = normalize_embeddings
        self.embeddings_model = self._load_model()

    def _load_model(self):
        try:
            return HuggingFaceEmbeddings(
                model_name = self.model_name,
                model_kwargs={"device": self.device},
                encode_kwargs={"normalize_embeddings": self.normalize_embeddings},
            )
        except Exception as e:
            raise RuntimeError(f"임베딩 모델 로딩 실패: {e}")
    
    def get_model(self):
        """ 임베딩 모델 객체 반환 """
        return self.embeddings_model
