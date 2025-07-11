from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class JinroTestReportRequest(BaseModel):
    qestrnSeq: str = Field(..., examples=["6"])
    trgetSe: str = Field(..., examples=["100208"])
    startDtm: int = Field(..., examples=[1550466291034])
    answers: str = Field(..., examples=["1=2 2=3 3=6 4=7 5=10 6=12 7=13 8=15 9=17 10=20 11=21 12=24 13=25 14=28 15=29 16=31 17=33 18=35 19=38 20=40 21=41 22=44 23=45 24=48 25=50 26=52 27=53 28=56"])
    apikey: Optional[str] = None


class ValueItem(BaseModel):
    name: str = Field(..., description="가치관 이름")
    weight: int = Field(..., description="가치관 가중치")


class JinroTestScore(BaseModel):
    values: List[ValueItem] = Field(..., description="가치관 목록")


class JobProfileResponse(BaseModel):
    id: int
    job_type: str
    job_name_ko: str
    description: Optional[str] = None
    stability: float
    creativity: float
    social_service: float
    ability_development: float
    conservatism: float
    social_recognition: float
    autonomy: float
    self_improvement: float
    
    class Config:
        from_attributes = True


class JinroResultResponse(BaseModel):
    id: int
    jinro_id: int
    version: int
    stability_score: float
    creativity_score: float
    social_service_score: float
    ability_development_score: float
    conservatism_score: float
    social_recognition_score: float
    autonomy_score: float
    self_improvement_score: float
    first_job_id: int = Field(..., description="첫 번째 유사 직업군 id")
    first_job: JobProfileResponse = Field(..., description="첫 번째 유사 직업군 정보")
    first_job_score: float
    second_job_id: int = Field(..., description="두 번째 유사 직업군 id")
    second_job: JobProfileResponse = Field(..., description="두 번째 유사 직업군 정보")
    second_job_score: float
    third_job_id: int = Field(..., description="세 번째 유사 직업군 id")
    third_job: JobProfileResponse = Field(..., description="세 번째 유사 직업군 정보")
    third_job_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class JinroResponse(BaseModel):
    id: int
    user_id: int
    version: str
    test: Optional[Dict[str, Any]] = None
    test_result: Optional[Dict[str, Any]] = None
    created_at: datetime
    jinro_results: List[JinroResultResponse]

    class Config:
        from_attributes = True

