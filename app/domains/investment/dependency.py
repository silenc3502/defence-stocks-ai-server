from fastapi import Depends

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.auth.adapter.outbound.in_memory.session_repository_impl import (
    SessionRepositoryImpl,
)
from app.domains.investment.application.usecase.investment_decision_usecase import (
    InvestmentDecisionUseCase,
)
from app.infrastructure.cache.redis_client import get_redis


def get_session_repository() -> SessionRepository:
    return SessionRepositoryImpl(get_redis())


def get_investment_decision_usecase() -> InvestmentDecisionUseCase:
    return InvestmentDecisionUseCase()
