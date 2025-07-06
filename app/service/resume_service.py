from sqlmodel import Session
from app.crud.resume import resume_crud
from app.models.resume import Resume
from typing import Optional, List
from fastapi import HTTPException
from app.core.config import settings
from app.models.resume_embedding import ResumeEmbedding
import json
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from docx import Document as DocxDocument
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class ResumeService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY
        )

    def create(
        self,
        db: Session,
        *,
        resume: Resume
    ) -> Resume:
        return resume_crud.create(db=db, resume=resume)

    def get_by_id(
        self,
        db: Session,
        resume_id: int
    ) -> Optional[Resume]:
        resume = resume_crud.get_by_id(db=db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume

    def get_by_user_id(
        self,
        db: Session,
        user_id: int
    ) -> List[Resume]:
        resumes = resume_crud.get_by_user_id(db=db, user_id=user_id)
        return resumes

    def get_with_user(
        self,
        db: Session,
        resume_id: int
    ) -> Optional[Resume]:
        resume = resume_crud.get_with_user(db=db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume

    def delete(
        self,
        db: Session,
        resume_id: int
    ) -> None:
        resume = self.get_by_id(db=db, resume_id=resume_id)
        if resume:
            db.delete(resume)
            db.commit()

    # def parse_resume(self, file_path: str, filename: str) -> List[Document]:
    #     file_extenstion = filename.split(".")[-1].lower()

    #     if file_extenstion == "pdf":
    #         loader = PyPDFLoader(file_path)
    #         return loader.load()
    #     elif file_extenstion in ["doc", "docx"]:
    #         doc = DocxDocument(file_path)
    #         full_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    #         return [Document(page_content=full_text)]
    #     else:
    #         raise HTTPException(status_code=400, detail="Unsupported file type")

    # def process_resume_file(self, file_path: str, filename: str) -> None:
    #     document = self.parse_resume(file_path, filename)

    #     full_text = ""
    #     for doc in document:
    #         full_text += doc.page_content + "\n"

    #     return full_text
    
    def parse_and_chunk_resume(self, file_path: str, filename: str) -> List[Document]:
        file_extenstion = filename.split(".")[-1].lower()
        
        # 텍스트 분할기 설정
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,  # 크기를 늘려서 의미단위 보존
            chunk_overlap=100,  # 겹침을 줄임
            separators=[
                "\n**",          # 섹션 제목 (볼드)
                "\n✓",           # 프로젝트 내 항목들
                "\n\n",          # 단락 구분
                "\n",            # 줄바꿈
                ".",             # 마침표
                " "              # 공백
            ]
        )
            
        if file_extenstion == 'pdf':
            loader = PyMuPDFLoader(file_path)
        elif file_extenstion in ['doc', 'docx']:
            loader = Docx2txtLoader(file_path)
        
        # 로드와 동시에 청킹
        documents = loader.load_and_split(text_splitter=text_splitter)
        # print(f"총 청크 수: {len(documents)}")
        # print("\n" + "="*50)

        # for i, doc in enumerate(documents):
        #     print(f"청크 {i+1}:")
        #     print(f"길이: {len(doc.page_content)}자")
        #     print(f"내용: {doc.page_content[:200]}...")
        #     print("-" * 30)
        
        return documents
        
    def create_embeddings(self, chunks: List[Document]) -> List[List[float]]:
        try:
            texts = [chunk.page_content for chunk in chunks]

            vectors = self.embeddings.embed_documents(texts)
            return vectors
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating embeddings: {str(e)}")
        
    def save_embeddings_to_db(
        self, 
        db: Session, 
        resume_id: int, 
        chunks: List[Document], 
        vectors: List[List[float]]
    ) -> List[ResumeEmbedding]:
        """
        청크와 임베딩을 DB에 저장
        """
        return resume_crud.bulk_create_embeddings(
            db=db,
            resume_id=resume_id,
            chunks=chunks,
            vectors=vectors
        )
        
    # def process_resume_with_embeddings(self, file_path: str, filename: str) -> tuple[List[Document], List[List[float]]]:
    #     # 1. 파싱 & 청킹
    #     chunks = self.parse_and_chunk_resume(file_path, filename)
        
    #     # 2. 임베딩 생성
    #     vectors = self.create_embeddings(chunks)

    #     print(f"청크 수: {len(chunks)}")
    #     print(f"벡터 수: {len(vectors)}")
    #     print(f"벡터 차원: {len(vectors[0])}")
        
    #     return chunks, vectors
    
    # def process_and_save_resume(
    #     self, 
    #     db: Session, 
    #     file_path: str, 
    #     filename: str, 
    #     resume_id: int = 1  # 테스트용 고정
    # ):
    #     """
    #     이력서 처리하고 DB에 저장하는 전체 플로우
    #     """
    #     # 1. 파싱 & 청킹 & 임베딩
    #     chunks, vectors = self.process_resume_with_embeddings(file_path, filename)
        
    #     # 2. DB에 저장
    #     embedding_records = self.save_embeddings_to_db(db, resume_id, chunks, vectors)
        
    #     print(f"✅ {len(embedding_records)}개의 임베딩이 DB에 저장되었습니다!")
        
    #     return {
    #         "resume_id": resume_id,
    #         "chunks_count": len(chunks),
    #         "embeddings_saved": len(embedding_records)
    #     }
    
resume_service = ResumeService()
