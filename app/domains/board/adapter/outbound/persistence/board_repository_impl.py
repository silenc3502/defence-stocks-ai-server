from sqlalchemy.orm import Session

from app.domains.board.adapter.outbound.persistence.board_repository import BoardRepository
from app.domains.board.domain.entity.board import Board
from app.domains.board.infrastructure.mapper.board_mapper import BoardMapper
from app.domains.board.infrastructure.orm.board_orm import BoardORM


class BoardRepositoryImpl(BoardRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, board: Board) -> Board:
        orm = BoardMapper.to_orm(board)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return BoardMapper.to_entity(orm)

    def find_all_with_pagination(self, page: int, size: int) -> tuple[list[Board], int]:
        total_count = self.db.query(BoardORM).count()
        offset = (page - 1) * size
        orms = (
            self.db.query(BoardORM)
            .order_by(BoardORM.id.desc())
            .offset(offset)
            .limit(size)
            .all()
        )
        boards = [BoardMapper.to_entity(orm) for orm in orms]
        return boards, total_count
