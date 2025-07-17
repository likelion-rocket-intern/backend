from pydantic import BaseModel
from typing import List

# --- 입력(Create) 스키마 ---
# API를 통해 JD를 생성할 때 받을 데이터의 형식을 정의
class JobDescriptionCreate(BaseModel):
    name: str
    content: str
    skills: List[str] = []


# --- 출력(Read) 스키마 ---
# API가 클라이언트에게 JD 정보를 응답으로 보낼 때의 형식을 정의
class JobDescriptionRead(BaseModel):
    id: int
    user_id: int
    name: str
    content: str
    skills: List[str]

