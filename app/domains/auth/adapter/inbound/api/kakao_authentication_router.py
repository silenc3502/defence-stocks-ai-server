from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import RedirectResponse

from app.domains.auth.application.response.kakao_access_token_response import KakaoAccessTokenResponse
from app.domains.auth.application.usecase.request_kakao_access_token_usecase import RequestKakaoAccessTokenUseCase
from app.domains.auth.application.usecase.request_kakao_oauth_link_usecase import RequestKakaoOauthLinkUseCase
from app.domains.auth.dependency import get_request_kakao_access_token_usecase, get_request_kakao_oauth_link_usecase
from app.infrastructure.config.settings import settings

router = APIRouter(prefix="/kakao-authentication", tags=["Kakao Authentication"])


@router.get("/request-oauth-link")
def request_oauth_link(
    usecase: RequestKakaoOauthLinkUseCase = Depends(get_request_kakao_oauth_link_usecase),
):
    oauth_url = usecase.execute()
    return RedirectResponse(url=oauth_url)


@router.get("/request-access-token-after-redirection", response_model=KakaoAccessTokenResponse)
def request_access_token_after_redirection(
    code: str,
    usecase: RequestKakaoAccessTokenUseCase = Depends(get_request_kakao_access_token_usecase),
):
    if not code:
        raise HTTPException(status_code=400, detail="인가 코드가 누락되었습니다.")

    result = usecase.execute(code)
    frontend_url = settings.cors_allowed_frontend_url

    if result.is_registered:
        print(f"exist user")
        query_params = urlencode({
            "nickname": result.nickname,
            "email": result.email,
            "account_id": result.account_id,
        })
        redirect_url = f"{frontend_url}?{query_params}"
        response = RedirectResponse(url=redirect_url)
        response.set_cookie(
            key="user_token",
            value=result.user_token,
            httponly=True,
            samesite="lax",
        )
    else:
        print(f"new user")
        redirect_url = f"{frontend_url}/auth-callback"
        response = RedirectResponse(url=redirect_url)
        response.set_cookie(
            key="temp_token",
            value=result.temp_token,
            httponly=True,
            max_age=5 * 60,
            samesite="lax",
        )

    return response
