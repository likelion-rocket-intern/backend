
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .jinro import Jinro

class JinroResult(SQLModel, table=True):
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
    # first_job_name: str = Field(..., description="첫 번째 유사 직업군명")
    # first_job_score: float = Field(..., description="첫 번째 직업군 유사도 점수")
    
    # second_job_name: str = Field(..., description="두 번째 유사 직업군명")
    # second_job_score: float = Field(..., description="두 번째 직업군 유사도 점수")
    
    # third_job_name: str = Field(..., description="세 번째 유사 직업군명")
    # third_job_score: float = Field(..., description="세 번째 직업군 유사도 점수")
    
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column_kwargs={"server_default": func.now()}
    )
    
    # Relationship
    jinro: Optional["Jinro"] = Relationship(back_populates="jinro_results")

