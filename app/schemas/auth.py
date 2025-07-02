from typing import Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel
from sqlmodel import SQLModel

class UserInfo(BaseModel, ABC):
    """소셜 로그인 사용자 정보의 추상 기본 클래스"""
    id: str
    nickname: str
    email: Optional[str] = None
    profile_image: Optional[str] = None

    @abstractmethod
    def get_unique_id(self) -> str:
        """소셜 플랫폼의 고유 ID를 반환"""
        pass

class TokenPayload(BaseModel):
    sub: UserInfo  # subject (user info)
    exp: int | None = None  # expiration time

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class KakaoLoginResponse(SQLModel):
    authorization_url: str

class KakaoUserInfo(UserInfo):
    """카카오 사용자 정보"""
    def get_unique_id(self) -> str:
        return f"kakao_{self.id}"
    
class UserResponse(BaseModel):
    nickname: str
    email: Optional[str] = None