from app.domains.stock_theme.domain.entity.defence_stock import DefenceStock
from app.domains.stock_theme.infrastructure.orm.defence_stock_orm import DefenceStockORM, DefenceStockThemeORM


class DefenceStockMapper:
    @staticmethod
    def to_entity(orm: DefenceStockORM) -> DefenceStock:
        return DefenceStock(
            id=orm.id,
            name=orm.name,
            code=orm.code,
            themes=[t.theme for t in orm.themes],
        )

    @staticmethod
    def to_orm(entity: DefenceStock) -> DefenceStockORM:
        orm = DefenceStockORM(
            name=entity.name,
            code=entity.code,
        )
        orm.themes = [DefenceStockThemeORM(theme=t) for t in entity.themes]
        return orm
