from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class InvestmentNewsContentRepository(ABC):
    """투자 뉴스 본문 JSONB 저장소 Port (PostgreSQL)."""

    @abstractmethod
    def save(self, news_id: int, link: str, raw: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, news_id: int) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
