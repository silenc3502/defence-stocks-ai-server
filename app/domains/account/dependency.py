from fastapi import Depends
from sqlalchemy.orm import Session

from app.domains.account.adapter.outbound.persistence.account_repository import AccountRepository
from app.domains.account.adapter.outbound.persistence.account_repository_impl import AccountRepositoryImpl
from app.domains.account.application.usecase.check_account_registration_usecase import CheckAccountRegistrationUseCase
from app.domains.account.application.usecase.sign_up_with_temp_token_usecase import SignUpWithTempTokenUseCase
from app.domains.auth.adapter.outbound.in_memory.kakao_token_repository_impl import KakaoTokenRepositoryImpl
from app.domains.auth.adapter.outbound.in_memory.session_repository_impl import SessionRepositoryImpl
from app.domains.auth.adapter.outbound.in_memory.temp_token_repository_impl import TempTokenRepositoryImpl
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.database.session import get_db


def get_account_repository(db: Session = Depends(get_db)) -> AccountRepository:
    return AccountRepositoryImpl(db)


def get_check_account_registration_usecase(
    account_repository: AccountRepository = Depends(get_account_repository),
) -> CheckAccountRegistrationUseCase:
    return CheckAccountRegistrationUseCase(account_repository)


def get_sign_up_with_temp_token_usecase(
    account_repository: AccountRepository = Depends(get_account_repository),
) -> SignUpWithTempTokenUseCase:
    redis_client = get_redis()
    return SignUpWithTempTokenUseCase(
        temp_token_repository=TempTokenRepositoryImpl(redis_client),
        account_repository=account_repository,
        session_repository=SessionRepositoryImpl(redis_client),
        kakao_token_repository=KakaoTokenRepositoryImpl(redis_client),
    )
