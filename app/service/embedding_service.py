import os
import logging
import pandas as pd
from app.repository.embedding_repository import EmbeddingRepository
from app.providers.embedding_provider import EmbeddingsProvider
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
    def __init__(self, 
                file_path: str,
                repository: EmbeddingRepository, 
                columns: list[str] | None = None
                ):
        self.file_path = file_path
        self.columns = columns
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
        
        if self.columns is None:
            self.columns = self.df.columns.tolist()
            logger.info(f"컬럼이 지정되지 않아 파일의 모든 컬럼을 사용합니다: {self.columns}")


        self.df[self.columns] = self.df[self.columns].fillna('')
        self.texts = self.df[self.columns].astype(str).agg(' '.join, axis=1).tolist()
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
            if self.repository.exists(str(object_id), self.object_type):
                continue

            row_dict = row._asdict()
            row_dict.pop('Index', None)

            embedding_obj = Embedding(
                object_id=str(object_id),
                object_type=self.object_type,
                embedding=vector,
                extra_data=row_dict
            )
            self.repository.save(embedding_obj)
        logger.info("DB 저장 완료")

    def run(self):
        self.load_data()
        self.embed()
        self.save_to_db()
