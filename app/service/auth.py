from sqlmodel import Session
from app.core import security
from app.crud import user_crud
from app.models.user import User
from app.schemas.auth import Token, UserInfo, UserDetailResponse
from app.service.kakao_auth import KakaoAuth
from app.crud import resume_crud, crud_jinro
from app.schemas.resume import ResumeDetailResponse, Keyword
from app.schemas.jinro import JinroResponse

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
    
    def get_user_detail(self, db: Session, user_id: int) -> UserDetailResponse:
        user = user_crud.get_by_id(db, user_id)
        resume_list = resume_crud.get_by_user_id(db, user_id)
        jinro_list = crud_jinro.get_by_userid(db, user_id)


                # 디버깅 로그 추가
        print(f"=== User 디버깅 ===")
        print(f"User ID: {user.id}")
        print(f"Nickname: {user.nickname}")
        print(f"Email: {user.email}")
        print(f"Profile Image: {user.profile_image}")
        print(f"Profile Image type: {type(user.profile_image)}")
        
        return UserDetailResponse(
            id=user.id,
            nickname=user.nickname,
            email=user.email,
            profile_image=user.profile_image,
            resume_list=[
                ResumeDetailResponse(
                    id=resume.id,
                    user_id=resume.user_id,
                    version=resume.version,
                    original_filename=resume.original_filename,
                    upload_filename=resume.upload_filename,
                    file_url=resume.file_url,
                    keywords=[
                        Keyword(
                            keyword=kw.keyword,
                            similar_to=kw.similar_to,
                            similarity=float(kw.similarity),
                            frequency=kw.frequency
                        ) for kw in resume.resume_keywords
                    ],
                    analysis_result=resume.analysis_result,
                    created_at=resume.created_at
                )
                for resume in resume_list
            ],
            jinro_list=[
                JinroResponse(
                    id=jinro.id,
                    user_id=jinro.user_id,
                    version=jinro.version,
                    created_at=jinro.created_at,
                    jinro_results=jinro.jinro_results
                )
                for jinro in jinro_list
            ]
        )
auth_service = AuthService() 