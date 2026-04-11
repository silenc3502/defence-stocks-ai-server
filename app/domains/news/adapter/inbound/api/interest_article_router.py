from fastapi import APIRouter, Cookie, Depends, HTTPException

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.news.application.exceptions import (
    ArticleFetchError,
    DuplicateInterestArticleError,
    InterestArticleContentPersistError,
)
from app.domains.news.application.request.save_interest_article_request import (
    SaveInterestArticleRequest,
)
from app.domains.news.application.response.save_interest_article_response import (
    SaveInterestArticleResponse,
)
from app.domains.news.application.usecase.save_interest_article_usecase import (
    SaveInterestArticleUseCase,
)
from app.domains.news.dependency import (
    get_save_interest_article_usecase,
    get_session_repository,
)

router = APIRouter(prefix="/news/interest-articles", tags=["NewsInterestArticle"])


@router.post("", response_model=SaveInterestArticleResponse, status_code=201)
def save_interest_article(
    request: SaveInterestArticleRequest,
    user_token: str = Cookie(None),
    usecase: SaveInterestArticleUseCase = Depends(get_save_interest_article_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    if not user_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    account_id = session_repository.find_by_token(user_token)
    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    try:
        return usecase.execute(request=request, account_id=account_id)
    except DuplicateInterestArticleError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ArticleFetchError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except InterestArticleContentPersistError as e:
        raise HTTPException(status_code=500, detail=str(e))
