from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class InvestmentNewsRepository(ABC):
    """투자 뉴스 메타데이터 저장소 Port (MySQL)."""

    @abstractmethod
    def save(
        self,
        keyword: Optional[str],
        query_used: str,
        title: str,
        source: Optional[str],
        link: str,
        published_at: Optional[datetime],
    ) -> int:
        """:return: 저장된 row id (PG 의 cross-DB 키로 사용됨)"""
        raise NotImplementedError

    @abstractmethod
    def delete(self, news_id: int) -> None:
        """PG 저장 실패 시 정합성 회복용 롤백 삭제."""
        raise NotImplementedError
