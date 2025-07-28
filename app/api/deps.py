from collections.abc import Generator
from typing import Annotated
from datetime import datetime

import jwt
from fastapi import Depends, HTTPException, status, Cookie, Response
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import User
from app.schemas.auth import UserInfo, TokenPayload

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

async def get_access_token(access_token: str | None = Cookie(None)) -> str | None:
    return access_token

async def get_refresh_token(refresh_token: str | None = Cookie(None)) -> str | None:
    return refresh_token

SessionDep = Annotated[Session, Depends(get_db)]
AccessTokenDep = Annotated[str | None, Depends(get_access_token)]
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
    access_token: AccessTokenDep,
    refresh_token: RefreshTokenDep,
    response: Response
) -> User:
    print("=== Debug Token Info ===")
    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
    print("=====================")
    
    # 토큰이 둘 다 없으면 인증되지 않음
    if not access_token and not refresh_token:
        print("No tokens provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    # Access token이 있으면 먼저 검증 시도
    if access_token:
        try:
            print("Verifying access token...")
            user = security.verify_token(access_token, session)
            print("Access token is valid")
            return user
        except HTTPException as e:
            print(f"=== Access Token Verification Error ===")
            print(f"Error: {str(e.detail)}")
            print(f"Status Code: {e.status_code}")
            print("=====================================")
            
            # Access token이 만료되었거나 유효하지 않은 경우
            # 401 (만료) 또는 403 (유효하지 않음) 모두 refresh token으로 시도
            if refresh_token and e.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]:
                print("Attempting to refresh token...")
                try:
                    # Refresh token 검증
                    user = security.verify_token(refresh_token, session)
                    print("Refresh token is valid, creating new access token...")
                    
                    # 새로운 access token 생성
                    new_access_token = create_new_access_token(user)
                    
                    # 새로운 access token을 쿠키에 설정
                    response.set_cookie(
                        key="access_token",
                        value=new_access_token,
                        httponly=True,
                        secure=True,
                        samesite="lax",
                        max_age= 30 * 60
                    )
                    print("=== New Access Token Created ===")
                    print(f"New token: {new_access_token[:50]}...")
                    return user
                    
                except HTTPException as refresh_error:
                    print(f"=== Refresh Token Verification Error ===")
                    print(f"Error: {str(refresh_error.detail)}")
                    print("======================================")
                    # Refresh token도 유효하지 않음
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Both access token and refresh token are invalid",
                    )
            else:
                # Refresh token이 없거나 다른 에러인 경우 원래 에러를 그대로 던짐
                raise e
    
    # Access token이 없고 refresh token만 있는 경우
    elif refresh_token:
        print("No access token, trying refresh token...")
        try:
            user = security.verify_token(refresh_token, session)
            new_access_token = create_new_access_token(user)
            
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=30 * 60
            )
            print("Created new access token from refresh token")
            return user
            
        except HTTPException:
            print("Refresh token is invalid")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid",
            )

CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user