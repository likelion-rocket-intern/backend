from typing import Optional
from pydantic import BaseModel
from sqlmodel import SQLModel
from app.schemas.resume import ResumeDetailResponse as ResumeResponse
from app.schemas.jinro import JinroResponse

class UserInfo(BaseModel):
    """소셜 로그인 사용자 정보의 추상 기본 클래스"""
    id: int
    social_id: str
    nickname: str
    email: Optional[str] = None
    profile_image: Optional[str] = None

class TokenPayload(BaseModel):
    sub: UserInfo  # subject (user info)
    exp: int | None = None  # expiration time

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class KakaoLoginResponse(SQLModel):
    authorization_url: str

    
class UserResponse(BaseModel):
    nickname: str
    email: Optional[str] = None

class UserDetailResponse(UserResponse):
    resume_list: list[ResumeResponse]
    jinro_list: list[JinroResponse]