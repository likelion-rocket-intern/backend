from datetime import datetime
from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, TEXT, JSONB

if TYPE_CHECKING:
    from .resume import Resume  

class JobDescriptionTechStack(SQLModel, table=True):
    __tablename__ = "job_description_tech_stacks"
    
    job_description_id: int = Field(foreign_key="job_descriptions.id", primary_key=True)
    tech_stack_id: int = Field(foreign_key="tech_stacks.id", primary_key=True)


class TechStack(SQLModel, table=True):
    __tablename__ = "tech_stacks"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(TEXT, nullable=False), unique=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)

    # N:N 관계 추가
    job_descriptions: List["JobDescription"] = Relationship(
        back_populates="tech_stacks",
        link_model=JobDescriptionTechStack
    )

class Description(SQLModel, table=True):
    __tablename__ = "descriptions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    job_description_id: int = Field(foreign_key="job_descriptions.id")
    description: str = Field(sa_column=Column(TEXT, nullable=False), unique=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # 추가 필요: 역방향 관계 설정
    job_description: "JobDescription" = Relationship(back_populates="job_descriptions")

class JobDescription(SQLModel, table=True):
    __tablename__ = "job_descriptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    jd_url: str = Field(sa_column=Column(TEXT, nullable=False))
    content: str = Field(sa_column=Column(TEXT, nullable=False))
    name: str = Field(sa_column=Column(TEXT, nullable=False))
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # 관계들
    tech_stacks: List["TechStack"] = Relationship(
        back_populates="job_descriptions",
        link_model=JobDescriptionTechStack
    ) 
    descriptions: List["Description"] = Relationship(
        back_populates="job_description"
    )
    # result 관계만 설정 (ID는 없음)
    result: Optional["JobDescriptionResult"] = Relationship(back_populates="job_description")


class JobDescriptionResult(SQLModel, table=True):
    __tablename__ = "job_description_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    resume_keywords: List[str] = Field(sa_column=Column(JSONB, nullable=False))
    resume_strengths: List[str] = Field(sa_column=Column(JSONB, nullable=False))
    resume_weaknesses: List[str] = Field(sa_column=Column(JSONB, nullable=False))
    overall_assessment: str = Field(sa_column=Column(JSONB, nullable=False))
    
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)

    # JobDescription의 ID를 외래키로 가짐 (필수)
    job_description_id: int = Field(foreign_key="job_descriptions.id", unique=True)
    
    # 관계 설정
    job_description: "JobDescription" = Relationship(back_populates="result")

