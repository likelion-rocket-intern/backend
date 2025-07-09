import os
import logging
import pandas as pd
from app.repository.embedding_repository import EmbeddingRepository
from app.service.embedding_provider import EmbeddingsProvider
from app.crud.embedding import embedding_crud
from app.models.embedding import Embedding
from sqlmodel import Session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def extract_object_type(file_path: str) -> str:
    """ 파일명에 따라 object_type 지정 """
    filename = os.path.basename(file_path)
    object_type = filename.split("_")[0]
    return object_type

class DataEmbedder:
    def __init__(self, file_path: str, column: str, repository: EmbeddingRepository):
        self.file_path = file_path
        self.column = column
        self.repository = repository
        self.df = None
        self.texts = None
        self.vectors = None
        self.object_type = extract_object_type(file_path)

    def load_data(self):
        ext = os.path.splitext(self.file_path)[-1].lower()
        if ext == ".csv":
            self.df = pd.read_csv(self.file_path)
        elif ext == ".json":
            self.df = pd.read_json(self.file_path)
        else:
            raise ValueError("지원하지 않는 파일 형식입니다.")
        self.texts = self.df[self.column].astype(str).tolist()
        logger.info(f"{len(self.texts)}개의 텍스트를 로드했습니다.")

    def embed(self):
        provider = EmbeddingsProvider()
        model = provider.get_model()
        self.vectors = model.embed_documents(self.texts)
        logger.info(f"{len(self.vectors)}개의 임베딩 벡터를 생성했습니다.")
        return self.vectors

    def save_to_db(self):
        crud = embedding_crud
        for idx, (row, vector) in enumerate(zip(self.df.itertuples(), self.vectors)):
            object_id = getattr(row, "id", idx)
            # --- 중복 체크 ---
            if self.repository.exists(object_id, self.object_type):
                continue
            embedding_obj = Embedding(
                object_id=object_id,
                object_type=self.object_type,
                embedding=vector,
                name=getattr(row, "name", None),
                skill=getattr(row, "skill", None),
                attribute=getattr(row, "attribute", None),
                description=getattr(row, "description", None),
            )
            self.repository.save(embedding_obj)
        logger.info("DB 저장 완료")

    def run(self):
        self.load_data()
        self.embed()
        self.save_to_db()
