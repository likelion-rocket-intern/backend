from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, RedirectResponse
from app.api.deps import SessionDep, CurrentUser
from app.schemas.auth import KakaoLoginResponse, UserDetailResponse
from app.service.auth import auth_service
from app.core.config import settings

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
) -> Response:
    """카카오 로그인 콜백 처리"""
    try:
        token, user = await auth_service.process_social_login(session, code)
        
        # access 토큰을 쿠키에 설정
        response = RedirectResponse(url=f"{settings.FRONTEND_HOST}")
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            secure=settings.USE_HTTPS,  # 환경에 따라 설정
            samesite="lax",
            domain=settings.COOKIE_DOMAIN,  # 쿠키 도메인 설정
            max_age=30 * 60  # 30분
        )
        
        # refresh 토큰을 쿠키에 설정
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token, 
            httponly=True,
            secure=settings.USE_HTTPS,  # 환경에 따라 설정
            samesite="lax",
            domain=settings.COOKIE_DOMAIN,  # 쿠키 도메인 설정
            max_age=7 * 24 * 60 * 60  # 7일
        )
        
        return response
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
async def get_me(current_user:CurrentUser, session: SessionDep) -> UserDetailResponse:

    current_user = auth_service.get_user_detail(session, current_user.id)

    return current_user