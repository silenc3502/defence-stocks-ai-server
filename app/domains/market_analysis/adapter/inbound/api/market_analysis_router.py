from fastapi import APIRouter, Cookie, Depends, HTTPException

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.market_analysis.application.request.analysis_question_request import AnalysisQuestionRequest
from app.domains.market_analysis.application.response.analysis_answer_response import AnalysisAnswerResponse
from app.domains.market_analysis.application.usecase.ask_analysis_usecase import AskAnalysisUseCase
from app.domains.market_analysis.dependency import get_ask_analysis_usecase, get_session_repository

router = APIRouter(prefix="/market-analysis", tags=["Market Analysis"])


@router.post("/ask", response_model=AnalysisAnswerResponse)
def ask_analysis(
    request: AnalysisQuestionRequest,
    user_token: str = Cookie(None),
    usecase: AskAnalysisUseCase = Depends(get_ask_analysis_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    if not user_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    account_id = session_repository.find_by_token(user_token)
    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    return usecase.execute(request)
