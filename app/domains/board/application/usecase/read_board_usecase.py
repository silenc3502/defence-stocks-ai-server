from app.domains.account.adapter.outbound.persistence.account_repository import AccountRepository
from app.domains.board.adapter.outbound.persistence.board_repository import BoardRepository
from app.domains.board.application.response.read_board_response import ReadBoardResponse


class ReadBoardUseCase:
    def __init__(self, board_repository: BoardRepository, account_repository: AccountRepository):
        self.board_repository = board_repository
        self.account_repository = account_repository

    def execute(self, board_id: int) -> ReadBoardResponse:
        board = self.board_repository.find_by_id(board_id)
        if board is None:
            raise ValueError("게시물을 찾을 수 없습니다.")

        account = self.account_repository.find_by_id(board.account_id)
        nickname = account.name if account else "알 수 없음"

        return ReadBoardResponse(
            board_id=board.board_id,
            title=board.title,
            content=board.content,
            nickname=nickname,
            created_at=board.created_at,
            updated_at=board.updated_at,
        )
