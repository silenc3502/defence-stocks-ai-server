from abc import ABC, abstractmethod
from typing import Any, Dict


class InterestArticleContentRepository(ABC):
    """관심 기사 본문/비정형 원본 데이터 저장소 Port (PostgreSQL JSONB)."""

    @abstractmethod
    def save(
        self,
        article_id: int,
        account_id: int,
        link: str,
        raw: Dict[str, Any],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, article_id: int) -> None:
        raise NotImplementedError
