from fastapi import Depends

from app.domains.account.adapter.outbound.persistence.account_repository import AccountRepository
from app.domains.account.application.usecase.check_account_registration_usecase import CheckAccountRegistrationUseCase
from app.domains.account.dependency import get_account_repository, get_check_account_registration_usecase
from app.domains.auth.adapter.outbound.external.kakao_auth_client import KakaoAuthClient
from app.domains.auth.adapter.outbound.external.kakao_auth_port import KakaoAuthPort
from app.domains.auth.adapter.outbound.in_memory.kakao_token_repository import KakaoTokenRepository
from app.domains.auth.adapter.outbound.in_memory.kakao_token_repository_impl import KakaoTokenRepositoryImpl
from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.auth.adapter.outbound.in_memory.session_repository_impl import SessionRepositoryImpl
from app.domains.auth.adapter.outbound.in_memory.temp_token_repository import TempTokenRepository
from app.domains.auth.adapter.outbound.in_memory.temp_token_repository_impl import TempTokenRepositoryImpl
from app.domains.auth.application.usecase.kakao_login_usecase import KakaoLoginUseCase
from app.domains.auth.application.usecase.get_temp_user_info_usecase import GetTempUserInfoUseCase
from app.domains.auth.application.usecase.request_kakao_access_token_usecase import RequestKakaoAccessTokenUseCase
from app.domains.auth.application.usecase.request_kakao_oauth_link_usecase import RequestKakaoOauthLinkUseCase
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.security.jwt_provider import JwtProvider


def get_kakao_auth_port() -> KakaoAuthPort:
    return KakaoAuthClient()


def get_jwt_provider() -> JwtProvider:
    return JwtProvider()


def get_kakao_login_usecase(
    account_repository: AccountRepository = Depends(get_account_repository),
    kakao_auth_port: KakaoAuthPort = Depends(get_kakao_auth_port),
    jwt_provider: JwtProvider = Depends(get_jwt_provider),
) -> KakaoLoginUseCase:
    return KakaoLoginUseCase(account_repository, kakao_auth_port, jwt_provider)


def get_request_kakao_oauth_link_usecase(
    kakao_auth_port: KakaoAuthPort = Depends(get_kakao_auth_port),
) -> RequestKakaoOauthLinkUseCase:
    return RequestKakaoOauthLinkUseCase(kakao_auth_port)


def get_temp_token_repository() -> TempTokenRepository:
    return TempTokenRepositoryImpl(get_redis())


def get_session_repository() -> SessionRepository:
    return SessionRepositoryImpl(get_redis())


def get_kakao_token_repository() -> KakaoTokenRepository:
    return KakaoTokenRepositoryImpl(get_redis())


def get_request_kakao_access_token_usecase(
    kakao_auth_port: KakaoAuthPort = Depends(get_kakao_auth_port),
    check_account_registration_usecase: CheckAccountRegistrationUseCase = Depends(get_check_account_registration_usecase),
    temp_token_repository: TempTokenRepository = Depends(get_temp_token_repository),
    session_repository: SessionRepository = Depends(get_session_repository),
    kakao_token_repository: KakaoTokenRepository = Depends(get_kakao_token_repository),
) -> RequestKakaoAccessTokenUseCase:
    return RequestKakaoAccessTokenUseCase(
        kakao_auth_port, check_account_registration_usecase,
        temp_token_repository, session_repository, kakao_token_repository,
    )


def get_get_temp_user_info_usecase(
    temp_token_repository: TempTokenRepository = Depends(get_temp_token_repository),
) -> GetTempUserInfoUseCase:
    return GetTempUserInfoUseCase(temp_token_repository)
