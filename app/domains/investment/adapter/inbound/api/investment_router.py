from fastapi import APIRouter, Cookie, Depends, HTTPException

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.investment.application.request.investment_decision_request import (
    InvestmentDecisionRequest,
)
from app.domains.investment.application.response.investment_decision_response import (
    InvestmentDecisionResponse,
)
from app.domains.investment.application.usecase.investment_decision_usecase import (
    InvestmentDecisionUseCase,
)
from app.domains.investment.dependency import (
    get_investment_decision_usecase,
    get_session_repository,
)
from app.infrastructure.agent.exceptions import AgentInvocationError

router = APIRouter(prefix="/investment", tags=["Investment"])


@router.post("/decision", response_model=InvestmentDecisionResponse)
def create_investment_decision(
    request: InvestmentDecisionRequest,
    user_token: str = Cookie(None),
    usecase: InvestmentDecisionUseCase = Depends(get_investment_decision_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    if not user_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    account_id = session_repository.find_by_token(user_token)
    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    try:
        return usecase.execute(query=request.query)
    except AgentInvocationError as e:
        raise HTTPException(status_code=502, detail=f"투자 판단 처리 실패: {e}")
