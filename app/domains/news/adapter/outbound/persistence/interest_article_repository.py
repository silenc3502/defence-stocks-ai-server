from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class InterestArticleRepository(ABC):
    """관심 기사 메타데이터 저장소 Port (MySQL)."""

    @abstractmethod
    def exists(self, account_id: int, link: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        account_id: int,
        title: str,
        source: Optional[str],
        link: str,
        published_at: Optional[datetime],
    ) -> int:
        """
        :return: article_id
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, article_id: int) -> None:
        raise NotImplementedError
