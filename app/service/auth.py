from sqlmodel import Session
from app.core import security
from app.crud import user_crud
from app.models.user import User
from app.schemas.auth import Token, UserInfo
from app.service.kakao_auth import KakaoAuth

class AuthService:
    def __init__(self):
        self.kakao_auth = KakaoAuth()

    def get_social_login_url(self) -> str:
        return self.kakao_auth.get_authorization_url()

    async def process_social_login(
        self, db: Session, code: str
    ) -> Token:
        # 카카오 액세스 토큰 획득
        kakao_access_token = await self.kakao_auth.get_access_token(code)
        if not kakao_access_token:
            raise ValueError("Failed to get access token")
        
        # 카카오 사용자 정보 획득
        kakao_data = await self.kakao_auth.get_user_info(kakao_access_token)
        if not kakao_data:
            raise ValueError("Failed to get user info")

        # DB에서 유저 찾기 또는 생성
        db_user = user_crud.get_by_social_info(
            db, 
            social_type="kakao",
            social_id=str(kakao_data["id"])  # 카카오에서 받은 ID 그대로 사용
        )
        
        if not db_user:
            # 새로운 유저 생성
            new_user = User(
                social_type="kakao",
                social_id=str(kakao_data["id"]),
                nickname=kakao_data["properties"]["nickname"],
                email=kakao_data["kakao_account"].get("email"),
                profile_image=kakao_data["properties"].get("profile_image"),
            )

            db_user = user_crud.create_from_social(
                db, user=new_user
            )

        # KakaoUserInfo 생성 - id는 DB의 id를, social_id는 카카오 id를 사용
        user_info = UserInfo(
            id=db_user.id,
            social_type="kakao",
            social_id=db_user.social_id,
            nickname=db_user.nickname,
            email=db_user.email,
            profile_image=db_user.profile_image,
        )
        
        # JWT 토큰 생성
        access_token = security.create_access_token(user_info=user_info)
        refresh_token = security.create_refresh_token(user_info=user_info)
        
        # Update refresh token in DB
        db_user.refresh_token = refresh_token
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return Token(access_token=access_token, refresh_token=refresh_token), db_user

auth_service = AuthService() 