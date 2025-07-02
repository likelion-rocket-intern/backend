from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.auth import UserInfo, TokenPayload
from app.models import User
from sqlmodel import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def create_access_token(user_info: UserInfo, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    return create_token(user_info, expires_delta)

def create_refresh_token(user_info: UserInfo, expires_delta: timedelta = timedelta(days=7)) -> str:
    return create_token(user_info, expires_delta)

def create_token(user_info: UserInfo, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = TokenPayload(
        exp=int(expire.timestamp()),
        sub=user_info
    )
    encoded_jwt = jwt.encode(to_encode.model_dump(), settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_token(token: str, session: Session) -> User:
    """Verify the token and return the user if valid."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
