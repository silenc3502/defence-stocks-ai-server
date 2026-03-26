from abc import ABC, abstractmethod
from typing import Optional

from app.domains.market_video.domain.entity.market_video import MarketVideo


class MarketVideoRepository(ABC):
    @abstractmethod
    def find_by_video_id(self, video_id: str) -> Optional[MarketVideo]:
        pass

    @abstractmethod
    def save(self, entity: MarketVideo) -> MarketVideo:
        pass

    @abstractmethod
    def update(self, entity: MarketVideo) -> MarketVideo:
        pass

    @abstractmethod
    def delete_all(self) -> None:
        pass

    @abstractmethod
    def find_all_ordered_by_published_at(self, limit: int) -> list[MarketVideo]:
        pass
