from abc import ABC, abstractmethod
from typing import Optional

from app.domains.stock_theme.domain.entity.defence_stock import DefenceStock


class DefenceStockRepository(ABC):
    @abstractmethod
    def save(self, entity: DefenceStock) -> DefenceStock:
        pass

    @abstractmethod
    def find_by_code(self, code: str) -> Optional[DefenceStock]:
        pass

    @abstractmethod
    def find_all(self) -> list[DefenceStock]:
        pass

    @abstractmethod
    def count(self) -> int:
        pass
