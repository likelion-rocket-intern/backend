from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from app.api.deps import SessionDep, CurrentUser
from app.schemas.auth import KakaoLoginResponse, UserResponse
from app.service.auth import auth_service

router = APIRouter(tags=["auth"])

@router.get("/kakao/login")
async def kakao_login() -> KakaoLoginResponse:
    authorization_url = auth_service.get_social_login_url()
    return KakaoLoginResponse(authorization_url=authorization_url)

@router.get("/kakao/callback")
async def kakao_callback(
    session: SessionDep,
    response: Response,
    code: str = Query(..., description="카카오 인증 코드")
) -> UserResponse:
    """카카오 로그인 콜백 처리"""
    try:
        token, user = await auth_service.process_social_login(session, code)
        
        # access 토큰을 쿠키에 설정
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=30 * 60  # 30분
        )
        
        # refresh 토큰을 쿠키에 설정
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7일
        )
        
        return UserResponse(
            nickname=user.nickname,
            email=user.email
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/logout")
async def logout(
    response: Response
) -> dict[str, str]:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logout successful"}

@router.get("/me")
async def get_me(current_user:CurrentUser) -> UserResponse:
    return current_user