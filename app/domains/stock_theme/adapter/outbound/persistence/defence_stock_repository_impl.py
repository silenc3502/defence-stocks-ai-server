from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.domains.stock_theme.adapter.outbound.persistence.defence_stock_repository import DefenceStockRepository
from app.domains.stock_theme.domain.entity.defence_stock import DefenceStock
from app.domains.stock_theme.infrastructure.mapper.defence_stock_mapper import DefenceStockMapper
from app.domains.stock_theme.infrastructure.orm.defence_stock_orm import DefenceStockORM


class DefenceStockRepositoryImpl(DefenceStockRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, entity: DefenceStock) -> DefenceStock:
        orm = DefenceStockMapper.to_orm(entity)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return DefenceStockMapper.to_entity(orm)

    def find_by_code(self, code: str) -> Optional[DefenceStock]:
        orm = (
            self.db.query(DefenceStockORM)
            .options(joinedload(DefenceStockORM.themes))
            .filter(DefenceStockORM.code == code)
            .first()
        )
        if orm is None:
            return None
        return DefenceStockMapper.to_entity(orm)

    def find_all(self) -> list[DefenceStock]:
        orms = (
            self.db.query(DefenceStockORM)
            .options(joinedload(DefenceStockORM.themes))
            .all()
        )
        return [DefenceStockMapper.to_entity(orm) for orm in orms]

    def count(self) -> int:
        return self.db.query(DefenceStockORM).count()
