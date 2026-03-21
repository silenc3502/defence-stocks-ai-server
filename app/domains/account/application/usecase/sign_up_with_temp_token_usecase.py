import logging
import uuid

from app.domains.account.adapter.outbound.persistence.account_repository import AccountRepository
from app.domains.account.application.request.sign_up_request import SignUpRequest
from app.domains.account.application.response.sign_up_response import SignUpResponse
from app.domains.account.domain.entity.account import Account
from app.domains.auth.adapter.outbound.in_memory.kakao_token_repository import KakaoTokenRepository
from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.auth.adapter.outbound.in_memory.temp_token_repository import TempTokenRepository

logger = logging.getLogger(__name__)


class SignUpWithTempTokenUseCase:
    def __init__(
        self,
        temp_token_repository: TempTokenRepository,
        account_repository: AccountRepository,
        session_repository: SessionRepository,
        kakao_token_repository: KakaoTokenRepository,
    ):
        self.temp_token_repository = temp_token_repository
        self.account_repository = account_repository
        self.session_repository = session_repository
        self.kakao_token_repository = kakao_token_repository

    def execute(self, temp_token: str, request: SignUpRequest) -> tuple[SignUpResponse, str]:
        temp_data = self.temp_token_repository.find_by_token(temp_token)
        if temp_data is None:
            raise ValueError("임시 토큰이 만료되었거나 존재하지 않습니다.")

        account = Account(
            email=request.email,
            kakao_id=temp_data["kakao_id"],
            name=request.nickname,
        )
        account = self.account_repository.save(account)

        self.temp_token_repository.delete(temp_token)

        user_token = str(uuid.uuid4())
        self.session_repository.save(user_token, account.account_id)
        self.kakao_token_repository.save(account.account_id, temp_data["kakao_access_token"])

        logger.info("회원 가입 완료 - account_id: %d, user_token: %s...", account.account_id, user_token[:8])

        return SignUpResponse(nickname=request.nickname, email=request.email), user_token
