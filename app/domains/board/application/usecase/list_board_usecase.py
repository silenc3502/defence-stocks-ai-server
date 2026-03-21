import math

from app.domains.board.adapter.outbound.persistence.board_repository import BoardRepository
from app.domains.board.application.response.board_list_response import BoardItem, BoardListResponse


class ListBoardUseCase:
    def __init__(self, board_repository: BoardRepository):
        self.board_repository = board_repository

    def execute(self, page: int, size: int) -> BoardListResponse:
        boards, total_count = self.board_repository.find_all_with_pagination(page, size)
        total_pages = math.ceil(total_count / size) if size > 0 else 0

        items = [
            BoardItem(
                board_id=board.board_id,
                title=board.title,
                content=board.content,
                account_id=board.account_id,
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
