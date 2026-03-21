from fastapi import APIRouter, Cookie, Depends, HTTPException, Query

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.board.application.request.create_board_request import CreateBoardRequest
from app.domains.board.application.response.board_list_response import BoardListResponse
from app.domains.board.application.response.create_board_response import CreateBoardResponse
from app.domains.board.application.usecase.create_board_usecase import CreateBoardUseCase
from app.domains.board.application.usecase.list_board_usecase import ListBoardUseCase
from app.domains.board.application.usecase.read_board_usecase import ReadBoardUseCase
from app.domains.board.dependency import get_create_board_usecase, get_list_board_usecase, get_read_board_usecase, get_session_repository

router = APIRouter(prefix="/board", tags=["Board"])


@router.post("/register", response_model=CreateBoardResponse)
def create_board(
    request: CreateBoardRequest,
    user_token: str = Cookie(None),
    usecase: CreateBoardUseCase = Depends(get_create_board_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    if not user_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    account_id = session_repository.find_by_token(user_token)
    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    try:
        return usecase.execute(request, account_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list", response_model=BoardListResponse)
def list_boards(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    user_token: str = Cookie(None),
    usecase: ListBoardUseCase = Depends(get_list_board_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    if not user_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    account_id = session_repository.find_by_token(user_token)
    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    return usecase.execute(page, size)


@router.get("/{board_id}", response_model=CreateBoardResponse)
def read_board(
    board_id: int,
    user_token: str = Cookie(None),
    usecase: ReadBoardUseCase = Depends(get_read_board_usecase),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    if not user_token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    account_id = session_repository.find_by_token(user_token)
    if account_id is None:
        raise HTTPException(status_code=401, detail="세션이 만료되었거나 유효하지 않습니다.")

    try:
        return usecase.execute(board_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
