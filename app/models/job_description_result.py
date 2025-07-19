from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from .job_description import JobDescription

class JobDescriptionResult(SQLModel, table=True):
    __tablename__ = "job_description_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # LLM이 생성한 JSON 결과를 저장하기 위해 PostgreSQL의 JSONB 타입을 사용
    result: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)

    # 어떤 채용 공고 분석에 대한 결과인지 연결하기 위한 외래 키
    job_description_id: int = Field(foreign_key="job_descriptions.id", unique=True)
    
    # 관계 설정: JobDescriptionResult와 JobDescription은 1:1 관계
    job_description: "JobDescription" = Relationship(back_populates="result")