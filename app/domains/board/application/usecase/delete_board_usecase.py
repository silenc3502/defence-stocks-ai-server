from app.domains.board.adapter.outbound.persistence.board_repository import BoardRepository


class DeleteBoardUseCase:
    def __init__(self, board_repository: BoardRepository):
        self.board_repository = board_repository

    def execute(self, board_id: int, account_id: int) -> None:
        board = self.board_repository.find_by_id(board_id)
        if board is None:
            raise ValueError("게시물을 찾을 수 없습니다.")

        if board.account_id != account_id:
            raise PermissionError("본인이 작성한 게시물만 삭제할 수 있습니다.")

        self.board_repository.delete(board_id)
