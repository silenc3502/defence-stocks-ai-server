from app.domains.stock_theme.adapter.outbound.persistence.defence_stock_repository import DefenceStockRepository
from app.domains.stock_theme.application.response.defence_stock_list_response import (
    DefenceStockItem,
    DefenceStockListResponse,
)


class ListDefenceStocksUseCase:
    def __init__(self, defence_stock_repository: DefenceStockRepository):
        self.defence_stock_repository = defence_stock_repository

    def execute(self) -> DefenceStockListResponse:
        stocks = self.defence_stock_repository.find_all()

        items = [
            DefenceStockItem(
                name=s.name,
                code=s.code,
                themes=s.themes,
            )
            for s in stocks
        ]

        return DefenceStockListResponse(
            stocks=items,
            total_count=len(items),
        )
