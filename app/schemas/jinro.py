from pydantic import BaseModel, Field
from typing import Optional, List

class JinroTestReportRequest(BaseModel):
    #TODO 여기 환경변수로 넣으셈
    apikey: str = Field(..., examples=["878211ba94ee6b8314869638fe245b6a"])
    qestrnSeq: str = Field(..., examples=["6"])
    trgetSe: str = Field(..., examples=["100208"])
    startDtm: int = Field(..., examples=[1550466291034])
    answers: str = Field(..., examples=["1=2 2=3 3=6 4=7 5=10 6=12 7=13 8=15 9=17 10=20 11=21 12=24 13=25 14=28 15=29 16=31 17=33 18=35 19=38 20=40 21=41 22=44 23=45 24=48 25=50 26=52 27=53 28=56"])


class ValueItem(BaseModel):
    name: str = Field(..., description="가치관 이름")
    weight: int = Field(..., description="가치관 가중치")


class JinroTestScore(BaseModel):
    values: List[ValueItem] = Field(..., description="가치관 목록")

