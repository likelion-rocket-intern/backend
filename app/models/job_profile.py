from sqlmodel import SQLModel, Field
from typing import Optional

class JobProfile(SQLModel, table=True):
    __tablename__ = "job_profiles"
    
    id: int = Field(default=None, primary_key=True, index=True)
    job_type: str = Field(index=True, unique=True, max_length=50)
    job_name_ko: str = Field(max_length=50)  # 한글 직군명 (UI 표시용)
    
    # 8개 특성 점수 (1.0 ~ 6.0)
    stability: float = Field(ge=1.0, le=6.0)           # 안정성
    creativity: float = Field(ge=1.0, le=6.0)          # 창의성
    social_service: float = Field(ge=1.0, le=6.0)      # 사회봉사
    ability_development: float = Field(ge=1.0, le=6.0) # 능력발휘
    conservatism: float = Field(ge=1.0, le=6.0)        # 보수
    social_recognition: float = Field(ge=1.0, le=6.0)  # 사회적 인정
    autonomy: float = Field(ge=1.0, le=6.0)            # 자율성
    self_improvement: float = Field(ge=1.0, le=6.0)    # 자기계발
    
    # 메타데이터
    description: Optional[str] = Field(default=None)   # 직군 설명
    is_active: bool = Field(default=True)              # 활성화 여부

    def get_vector(self) -> list[float]:
        """특성 값들을 벡터로 반환 (유사도 계산용)"""
        return [
            self.stability,
            self.creativity,
            self.social_service,
            self.ability_development,
            self.conservatism,
            self.social_recognition,
            self.autonomy,
            self.self_improvement
        ]