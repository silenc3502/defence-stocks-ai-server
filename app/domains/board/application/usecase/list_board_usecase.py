import math

from app.domains.account.adapter.outbound.persistence.account_repository import AccountRepository
from app.domains.board.adapter.outbound.persistence.board_repository import BoardRepository
from app.domains.board.application.response.board_list_response import BoardItem, BoardListResponse


class ListBoardUseCase:
    def __init__(self, board_repository: BoardRepository, account_repository: AccountRepository):
        self.board_repository = board_repository
        self.account_repository = account_repository

    def execute(self, page: int, size: int) -> BoardListResponse:
        boards, total_count = self.board_repository.find_all_with_pagination(page, size)
        total_pages = math.ceil(total_count / size) if size > 0 else 0

        account_ids = list({board.account_id for board in boards})
        nickname_map = {}
        for account_id in account_ids:
            account = self.account_repository.find_by_id(account_id)
            nickname_map[account_id] = account.name if account else "알 수 없음"

        items = [
            BoardItem(
                board_id=board.board_id,
                title=board.title,
                content=board.content,
                nickname=nickname_map.get(board.account_id, "알 수 없음"),
                created_at=board.created_at,
                updated_at=board.updated_at,
            )
            for board in boards
        ]

        return BoardListResponse(
            items=items,
            current_page=page,
            total_pages=total_pages,
            total_count=total_count,
        )
