
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .jinro import Jinro
    from .job_profile import JobProfile

class JinroResult(SQLModel, table=True):

    __tablename__ = "jinro_result"
    
    id: int = Field(default=None, primary_key=True, index=True)
    jinro_id: int = Field(foreign_key="jinro.id", index=True)

    version: int
    
    # 8개 가치관 점수
    stability_score: int = Field(..., description="안정성 점수")
    creativity_score: int = Field(..., description="창의성 점수")
    social_service_score: int = Field(..., description="사회봉사 점수")
    ability_development_score: int = Field(..., description="능력발휘 점수")
    conservatism_score: int = Field(..., description="보수 점수")
    social_recognition_score: int = Field(..., description="사회적 인정 점수")
    autonomy_score: int = Field(..., description="자율성 점수")
    self_improvement_score: int = Field(..., description="자기계발 점수")
    
    # 상위 3개 직업군 정보
    first_job_id: int = Field(..., foreign_key="job_profiles.id", description="첫 번째 유사 직업군 id")
    first_job_score: float = Field(..., description="첫 번째 유사 직업군 점수")
    second_job_id: int = Field(..., foreign_key="job_profiles.id", description="두 번째 유사 직업군 id")
    second_job_score: float = Field(..., description="두 번째 유사 직업군 점수")
    third_job_id: int = Field(..., foreign_key="job_profiles.id", description="세 번째 유사 직업군 id")
    third_job_score: float = Field(..., description="세 번째 유사 직업군 점수")
    
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column_kwargs={"server_default": func.now()}
    )
    
    # Relationships
    jinro: Optional["Jinro"] = Relationship(back_populates="jinro_results")
    first_job: Optional["JobProfile"] = Relationship(back_populates="first_job_results", sa_relationship_kwargs={"foreign_keys": "[JinroResult.first_job_id]"})
    second_job: Optional["JobProfile"] = Relationship(back_populates="second_job_results", sa_relationship_kwargs={"foreign_keys": "[JinroResult.second_job_id]"})
    third_job: Optional["JobProfile"] = Relationship(back_populates="third_job_results", sa_relationship_kwargs={"foreign_keys": "[JinroResult.third_job_id]"})

