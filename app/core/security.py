from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.auth import UserInfo, TokenPayload
from app.models import User
from sqlmodel import Session
from app.crud import user_crud

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def create_access_token(user_info: UserInfo, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    return create_token(user_info, expires_delta)

def create_refresh_token(user_info: UserInfo, expires_delta: timedelta = timedelta(days=7)) -> str:
    return create_token(user_info, expires_delta)

def create_token(user_info: UserInfo, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": int(expire.timestamp()),
        "user_info": user_info.model_dump()
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_token(token: str, session: Session) -> User:
    """Verify the token and return the user if valid."""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_exp": True}  # 만료 시간 검증 명시적 활성화
        )
        user_info = UserInfo(**payload["user_info"])
        
    except ExpiredSignatureError:
        # 토큰이 만료된 경우
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except (InvalidTokenError, ValidationError) as e:
        # 토큰이 유효하지 않은 경우 (서명 불일치, 형식 오류 등)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials: {str(e)}",
        )
    
    user = user_crud.get(session, id=user_info.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
