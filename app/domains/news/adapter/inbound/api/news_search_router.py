from fastapi import APIRouter, Cookie, Depends, HTTPException, Query

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.news.application.response.news_search_response import (
    NewsSearchResponse,
)
from app.domains.news.application.usecase.search_news_usecase import (
    SearchNewsUseCase,
)
from app.domains.news.dependency import (
    get_search_news_usecase,
    get_session_repository,
)
from app.infrastructure.external.serp.serp_exceptions import (
    SerpAPIRequestError,
    SerpAPIResponseError,
)

router = APIRouter(prefix="/news", tags=["NewsSearch"])


@router.get("/search", response_model=NewsSearchResponse)
def search_news(
    keyword: str = Query(..., min_length=1, description="검색 키워드"),
    page: int = Query(1, ge=1, description="페이지 번호 (1-based)"),
    size: int = Query(10, ge=1, le=50, description="페이지 크기"),
    user_token: str = Cookie(None),
    usecase: SearchNewsUseCase = Depends(get_search_news_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    if not user_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    account_id = session_repository.find_by_token(user_token)
    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    try:
        return usecase.execute(keyword=keyword, page=page, page_size=size)
    except SerpAPIResponseError as e:
        raise HTTPException(status_code=502, detail=f"뉴스 검색 응답 오류: {e}")
    except SerpAPIRequestError as e:
        raise HTTPException(status_code=503, detail=f"뉴스 검색 서비스 일시 오류: {e}")
