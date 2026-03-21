import logging
import uuid

from app.domains.account.application.usecase.check_account_registration_usecase import CheckAccountRegistrationUseCase
from app.domains.auth.adapter.outbound.external.kakao_auth_port import KakaoAuthPort
from app.domains.auth.adapter.outbound.in_memory.kakao_token_repository import KakaoTokenRepository
from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.auth.adapter.outbound.in_memory.temp_token_repository import TempTokenRepository
from app.domains.auth.application.response.kakao_access_token_response import KakaoAccessTokenResponse

logger = logging.getLogger(__name__)


class RequestKakaoAccessTokenUseCase:
    def __init__(
        self,
        kakao_auth_port: KakaoAuthPort,
        check_account_registration_usecase: CheckAccountRegistrationUseCase,
        temp_token_repository: TempTokenRepository,
        session_repository: SessionRepository,
        kakao_token_repository: KakaoTokenRepository,
    ):
        self.kakao_auth_port = kakao_auth_port
        self.check_account_registration_usecase = check_account_registration_usecase
        self.temp_token_repository = temp_token_repository
        self.session_repository = session_repository
        self.kakao_token_repository = kakao_token_repository

    def execute(self, authorization_code: str) -> KakaoAccessTokenResponse:
        token_info = self.kakao_auth_port.get_kakao_access_token(authorization_code)
        user_info = self.kakao_auth_port.get_kakao_user_info(token_info.access_token)

        logger.info("Kakao 사용자 정보 - 닉네임: %s, 이메일: %s", user_info.name, user_info.email)

        registration = self.check_account_registration_usecase.execute(user_info.email)

        temp_token = None
        user_token = None

        if registration.is_registered:
            user_token = str(uuid.uuid4())
            self.session_repository.save(user_token, registration.account_id)
            self.kakao_token_repository.save(registration.account_id, token_info.access_token)
            logger.info("기존 회원 로그인 - account_id: %d, user_token: %s...", registration.account_id, user_token[:8])
        else:
            temp_token = str(uuid.uuid4())
            self.temp_token_repository.save(temp_token, {
                "kakao_access_token": token_info.access_token,
                "kakao_id": user_info.kakao_id,
                "nickname": user_info.name,
                "email": user_info.email,
            })
            logger.info("임시 토큰 발급 - token: %s...", temp_token[:8])

        return KakaoAccessTokenResponse(
            access_token=token_info.access_token,
            refresh_token=token_info.refresh_token,
            expires_in=token_info.expires_in,
            kakao_id=user_info.kakao_id,
            nickname=user_info.name,
            email=user_info.email,
            is_registered=registration.is_registered,
            account_id=registration.account_id,
            temp_token=temp_token,
            user_token=user_token,
        )
