from collections.abc import Generator
from typing import Annotated
from datetime import datetime

import jwt
from fastapi import Depends, HTTPException, status, Cookie, Response
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from app.schemas.auth import UserInfo

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_refresh_token(refresh_token: str | None = Cookie(None)) -> str | None:
    return refresh_token


RefreshTokenDep = Annotated[str | None, Depends(get_refresh_token)]


def create_new_access_token(user: User) -> str:
    # Convert User model to UserInfo schema
    user_info = UserInfo(
        id=user.id,
        email=user.email,
        nickname=user.nickname,
        social_id=user.social_id
    )
    return security.create_access_token(user_info=user_info)


def get_current_user(
    session: SessionDep, 
    token: TokenDep, 
    refresh_token: RefreshTokenDep,
    response: Response
) -> User:
    try:
        return security.verify_token(token, session)
    except HTTPException as e:
        if e.status_code == status.HTTP_403_FORBIDDEN and refresh_token:
            try:
                # Validate refresh token
                user = security.verify_token(refresh_token, session)
                # Create new access token with full user info
                new_access_token = create_new_access_token(user)
                # Set new access token in cookie
                response.set_cookie(
                    key="access_token",
                    value=new_access_token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    max_age=30 * 60  # 30분
                )
                return user
            except HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Both access token and refresh token are invalid",
                )
        raise e


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
