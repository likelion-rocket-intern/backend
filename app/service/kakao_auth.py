from app.core.config import settings
import httpx

from app.schemas.auth import KakaoUserInfo

class KakaoAuth:
    def __init__(self):
        self.client_id = settings.KAKAO_CLIENT_ID
        self.client_secret = settings.KAKAO_CLIENT_SECRET
        self.redirect_uri = settings.KAKAO_REDIRECT_URI
        self.auth_url = "https://kauth.kakao.com/oauth/authorize"
        self.token_url = "https://kauth.kakao.com/oauth/token"
        self.user_info_url = "https://kapi.kakao.com/v2/user/me"
        
    def get_authorization_url(self, state: str | None = None) -> str:
        """카카오 로그인 페이지 URL 생성"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
        }
        if state:
            params["state"] = state
            
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    async def get_access_token(self, code: str) -> str | None:
        """카카오 액세스 토큰 얻기"""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
        return None
    
    async def get_user_info(self, access_token: str) -> KakaoUserInfo | None:
        """카카오 사용자 정보 얻기"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.user_info_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return KakaoUserInfo(
                    id=str(data["id"]),  # kakao id is int, convert to str
                    nickname=data["properties"]["nickname"],
                    email=data["kakao_account"].get("email"),
                    profile_image=data["properties"].get("profile_image")
                )
            return None