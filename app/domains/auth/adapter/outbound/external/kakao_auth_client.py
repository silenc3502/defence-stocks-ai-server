import httpx

from app.domains.auth.adapter.outbound.external.kakao_auth_port import KakaoAuthPort, KakaoUserInfo
from app.infrastructure.config.settings import settings


class KakaoAuthClient(KakaoAuthPort):
    def get_kakao_access_token(self, authorization_code: str) -> str:
        response = httpx.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.kakao_client_id,
                "redirect_uri": settings.kakao_redirect_uri,
                "code": authorization_code,
            },
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def get_kakao_user_info(self, kakao_access_token: str) -> KakaoUserInfo:
        response = httpx.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {kakao_access_token}"},
        )
        response.raise_for_status()
        data = response.json()
        kakao_account = data.get("kakao_account", {})
        return KakaoUserInfo(
            kakao_id=str(data["id"]),
            name=kakao_account.get("profile", {}).get("nickname", ""),
            email=kakao_account.get("email", ""),
        )
