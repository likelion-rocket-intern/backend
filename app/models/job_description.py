from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import Column, JSON, Text
from sqlalchemy.sql import func
from typing import Optional, List, TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from .user import User
    from .job_description_result import JobDescriptionAnalysisResult

class JobDescription(SQLModel, table=True):

    __tablename__ = "job_descriptions"

    id: int = Field(default=None, primary_key=True, index=True)
    

    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column_kwargs={"server_default": func.now()}
    )
    
    # 직무명 ("백엔드 개발자" 등)
    name: str = Field(index=True)
    # 주요 기술 스택 또는 자격 요건
    skills: List[str] = Field(default=[], sa_column=Column(JSON))
    # 채용 공고 원본 전체 텍스트
    content: str = Field(sa_column=Column(Text))
    
    user: Optional["User"] = Relationship(back_populates="job_descriptions")
    analysis_results: List["JobDescriptionAnalysisResult"] = Relationship(back_populates="job_description")

