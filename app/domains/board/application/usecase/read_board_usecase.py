from app.domains.board.adapter.outbound.persistence.board_repository import BoardRepository
from app.domains.board.application.response.create_board_response import CreateBoardResponse


class ReadBoardUseCase:
    def __init__(self, board_repository: BoardRepository):
        self.board_repository = board_repository

    def execute(self, board_id: int) -> CreateBoardResponse:
        board = self.board_repository.find_by_id(board_id)
        if board is None:
            raise ValueError("게시물을 찾을 수 없습니다.")

        return CreateBoardResponse(
            board_id=board.board_id,
            title=board.title,
            content=board.content,
            account_id=board.account_id,
            created_at=board.created_at,
            updated_at=board.updated_at,
        )
