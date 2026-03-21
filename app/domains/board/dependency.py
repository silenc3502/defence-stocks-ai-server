from fastapi import Depends
from sqlalchemy.orm import Session

from app.domains.account.adapter.outbound.persistence.account_repository import AccountRepository
from app.domains.account.dependency import get_account_repository
from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.auth.adapter.outbound.in_memory.session_repository_impl import SessionRepositoryImpl
from app.domains.board.adapter.outbound.persistence.board_repository import BoardRepository
from app.domains.board.adapter.outbound.persistence.board_repository_impl import BoardRepositoryImpl
from app.domains.board.application.usecase.create_board_usecase import CreateBoardUseCase
from app.domains.board.application.usecase.list_board_usecase import ListBoardUseCase
from app.domains.board.application.usecase.read_board_usecase import ReadBoardUseCase
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.database.session import get_db


def get_board_repository(db: Session = Depends(get_db)) -> BoardRepository:
    return BoardRepositoryImpl(db)


def get_session_repository() -> SessionRepository:
    return SessionRepositoryImpl(get_redis())


def get_create_board_usecase(
    board_repository: BoardRepository = Depends(get_board_repository),
) -> CreateBoardUseCase:
    return CreateBoardUseCase(board_repository)


def get_list_board_usecase(
    board_repository: BoardRepository = Depends(get_board_repository),
    account_repository: AccountRepository = Depends(get_account_repository),
) -> ListBoardUseCase:
    return ListBoardUseCase(board_repository, account_repository)


def get_read_board_usecase(
    board_repository: BoardRepository = Depends(get_board_repository),
) -> ReadBoardUseCase:
    return ReadBoardUseCase(board_repository)
