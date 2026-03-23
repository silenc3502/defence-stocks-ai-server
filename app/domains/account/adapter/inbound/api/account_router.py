from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, Depends, Form, HTTPException
from starlette.responses import RedirectResponse

from app.domains.account.application.request.sign_up_request import SignUpRequest
from app.domains.account.application.usecase.sign_up_with_temp_token_usecase import SignUpWithTempTokenUseCase
from app.domains.account.dependency import get_sign_up_with_temp_token_usecase
from app.infrastructure.config.settings import settings

router = APIRouter(prefix="/account", tags=["Account"])


@router.post("/sign-up")
def sign_up(
    nickname: str = Form(...),
    email: str = Form(...),
    temp_token: str = Cookie(None),
    usecase: SignUpWithTempTokenUseCase = Depends(get_sign_up_with_temp_token_usecase),
):
    if not temp_token:
        raise HTTPException(status_code=400, detail="임시 토큰이 누락되었습니다.")

    request = SignUpRequest(nickname=nickname, email=email)

    try:
        result, user_token = usecase.execute(temp_token, request)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    query_params = urlencode({
        "nickname": result.nickname,
        "email": result.email,
    })
    redirect_url = f"{settings.cors_allowed_frontend_url}?{query_params}"
    response = RedirectResponse(url=redirect_url)
    response.set_cookie(
        key="user_token",
        value=user_token,
        httponly=True,
        samesite="lax",
    )
    response.delete_cookie(key="temp_token")
    return response
