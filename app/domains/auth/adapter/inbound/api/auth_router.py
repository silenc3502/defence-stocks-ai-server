from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domains.auth.adapter.outbound.external.kakao_auth_client import KakaoAuthClient
from app.domains.auth.adapter.outbound.persistence.member_repository_impl import MemberRepositoryImpl
from app.domains.auth.application.request.kakao_login_request import KakaoLoginRequest
from app.domains.auth.application.response.kakao_login_response import KakaoLoginResponse
from app.domains.auth.application.usecase.kakao_login_usecase import KakaoLoginUseCase
from app.infrastructure.database.session import get_db
from app.infrastructure.security.jwt_provider import JwtProvider

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/kakao", response_model=KakaoLoginResponse)
def kakao_login(
    request: KakaoLoginRequest,
    db: Session = Depends(get_db),
):
    repository = MemberRepositoryImpl(db)
    kakao_client = KakaoAuthClient()
    jwt_provider = JwtProvider()
    usecase = KakaoLoginUseCase(repository, kakao_client, jwt_provider)
    return usecase.execute(request)
