from abc import ABC, abstractmethod
from typing import Optional

from app.domains.board.domain.entity.board import Board


class BoardRepository(ABC):
    @abstractmethod
    def save(self, board: Board) -> Board:
        pass

    @abstractmethod
    def find_by_id(self, board_id: int) -> Optional[Board]:
        pass

    @abstractmethod
    def update(self, board: Board) -> Board:
        pass

    @abstractmethod
    def delete(self, board_id: int) -> None:
        pass

    @abstractmethod
    def find_all_with_pagination(self, page: int, size: int) -> tuple[list[Board], int]:
        pass
