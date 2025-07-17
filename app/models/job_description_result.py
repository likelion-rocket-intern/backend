from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy.sql import func
from typing import Optional, List, TYPE_CHECKING, Dict, Any
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from .user import User
    from .resume import Resume
    from .job_description import JobDescription

class JobDescriptionAnalysisResult(SQLModel, table=True):
    __tablename__ = "job_description_result"

    id: int = Field(default=None, primary_key=True, index=True)
    
    # Foreign Keys
    user_id: int = Field(foreign_key="users.id", index=True)
    resume_id: int = Field(foreign_key="resumes.id", index=True)
    job_description_id: int = Field(foreign_key="job_descriptions.id", index=True)

    # LLM이 생성한 JSON 형식의 분석 결과
    analysis_result: Dict[str, Any] = Field(sa_column=Column(JSON))
    
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column_kwargs={"server_default": func.now()}
    )
    
    # [스타일 반영] Relationship 설정
    user: Optional["User"] = Relationship(back_populates="analysis_results")
    resume: Optional["Resume"] = Relationship(back_populates="analysis_results")
    job_description: Optional["JobDescription"] = Relationship(back_populates="analysis_results")

