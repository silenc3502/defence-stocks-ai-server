from fastapi import APIRouter, Cookie, Depends, HTTPException

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.stock_theme.application.response.defence_stock_list_response import DefenceStockListResponse
from app.domains.stock_theme.application.response.stock_recommendation_response import StockRecommendationResponse
from app.domains.stock_theme.application.usecase.list_defence_stocks_usecase import ListDefenceStocksUseCase
from app.domains.stock_theme.application.usecase.recommend_stocks_usecase import RecommendStocksUseCase
from app.domains.stock_theme.dependency import get_list_defence_stocks_usecase, get_recommend_stocks_usecase, get_session_repository

router = APIRouter(prefix="/stock-theme", tags=["Stock Theme"])


@router.get("/recommend", response_model=StockRecommendationResponse)
def recommend_stocks(
    user_token: str = Cookie(None),
    usecase: RecommendStocksUseCase = Depends(get_recommend_stocks_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    if not user_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    account_id = session_repository.find_by_token(user_token)
    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    return usecase.execute()


@router.get("/stocks", response_model=DefenceStockListResponse)
def list_defence_stocks(
    user_token: str = Cookie(None),
    usecase: ListDefenceStocksUseCase = Depends(get_list_defence_stocks_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    if not user_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    account_id = session_repository.find_by_token(user_token)
    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    return usecase.execute()
