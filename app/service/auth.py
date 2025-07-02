from sqlmodel import Session
from app.core import security
from app.crud import user
from app.models.user import User
from app.schemas.auth import Token
from app.service.kakao_auth import KakaoAuth

class AuthService:
    def __init__(self):
        self.kakao_auth = KakaoAuth()

    def get_kakao_login_url(self) -> str:
        return self.kakao_auth.get_authorization_url()

    async def process_kakao_login(
        self, db: Session, code: str
    ) -> Token:
        # 카카오 액세스 토큰 획득
        kakao_access_token = await self.kakao_auth.get_access_token(code)
        if not kakao_access_token:
            raise ValueError("Failed to get access token")
        
        # 카카오 사용자 정보 획득
        kakao_user = await self.kakao_auth.get_user_info(kakao_access_token)
        if not kakao_user:
            raise ValueError("Failed to get user info")

        # DB에서 유저 찾기 또는 생성
        db_user = user.get_by_social_id(db, social_id=kakao_user.get_unique_id())
        
        if db_user:
            refresh_token = security.create_refresh_token(user_info=kakao_user)
            db_user.refresh_token = refresh_token
            db_user = user.update_from_social(
                db, user=db_user
            )
        else:
            # 새로운 유저 생성
            new_user = User(
                social_id=kakao_user.get_unique_id(),
                nickname=kakao_user.nickname,
                email=kakao_user.email,
                profile_image=kakao_user.profile_image,
                refresh_token=security.create_refresh_token(user_info=kakao_user)
            )
            db_user = user.create_from_social(
                db, user=new_user
            )
        
        # JWT 토큰 생성 - UserInfo 객체 전달
        access_token = security.create_access_token(user_info=kakao_user)
        
        return Token(access_token=access_token, refresh_token=db_user.refresh_token), db_user

auth_service = AuthService() 