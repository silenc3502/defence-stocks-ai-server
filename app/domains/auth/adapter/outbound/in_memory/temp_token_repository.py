from abc import ABC, abstractmethod
from typing import Optional


class TempTokenRepository(ABC):
    @abstractmethod
    def save(self, token: str, data: dict) -> None:
        pass

    @abstractmethod
    def find_by_token(self, token: str) -> Optional[dict]:
        pass

    @abstractmethod
    def delete(self, token: str) -> None:
        pass
