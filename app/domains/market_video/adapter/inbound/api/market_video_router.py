from fastapi import APIRouter, Cookie, Depends, HTTPException, Query

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.market_video.application.response.market_video_list_response import MarketVideoListResponse
from app.domains.market_video.application.response.noun_extraction_response import NounExtractionResponse
from app.domains.market_video.application.response.video_comments_response import CollectCommentsResponse
from app.domains.market_video.application.usecase.collect_video_comments_usecase import CollectVideoCommentsUseCase
from app.domains.market_video.application.usecase.extract_nouns_usecase import ExtractNounsUseCase
from app.domains.market_video.application.usecase.list_market_video_usecase import ListMarketVideoUseCase
from app.domains.market_video.dependency import get_collect_video_comments_usecase, get_extract_nouns_usecase, get_list_market_video_usecase, get_session_repository

router = APIRouter(prefix="/market-video", tags=["Market Video"])


@router.get("/list", response_model=MarketVideoListResponse)
def list_market_videos(
    user_token: str = Cookie(None),
    usecase: ListMarketVideoUseCase = Depends(get_list_market_video_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    print(f"[market-video] user_token: {user_token}")

    if not user_token:
        print("[market-video] user_token이 None입니다")
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    print(f"[market-video] Redis 조회 키: session:{user_token}")
    account_id = session_repository.find_by_token(user_token)
    print(f"[market-video] Redis 조회 결과 account_id: {account_id}")

    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    return usecase.execute()


@router.get("/comments/collect", response_model=CollectCommentsResponse)
def collect_video_comments(
    user_token: str = Cookie(None),
    usecase: CollectVideoCommentsUseCase = Depends(get_collect_video_comments_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    if not user_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    account_id = session_repository.find_by_token(user_token)
    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    return usecase.execute()


@router.get("/nouns/extract", response_model=NounExtractionResponse)
def extract_nouns_from_comments(
    top_n: int = Query(30, ge=1, le=200),
    user_token: str = Cookie(None),
    usecase: ExtractNounsUseCase = Depends(get_extract_nouns_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    if not user_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    account_id = session_repository.find_by_token(user_token)
    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    return usecase.execute(top_n)
