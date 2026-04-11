import logging
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any, List, Optional, Tuple

from app.domains.news.adapter.outbound.external.news_search_port import (
    NewsSearchPort,
)
from app.domains.news.application.response.news_search_response import NewsItem
from app.infrastructure.external.serp.serp_api_client import SerpAPIClient

logger = logging.getLogger(__name__)


class SerpNewsSearchClient(NewsSearchPort):
    """SerpAPI (google_news 엔진) 기반 뉴스 검색 Adapter.

    NewsSearchPort 의 구체 구현체. SERP API 응답을 NewsItem 으로 변환하고
    최신 게시 시간순으로 정렬한 뒤 요청된 페이지를 잘라 반환한다.
    """

    def __init__(self, serp_client: SerpAPIClient):
        self._serp_client = serp_client

    def search(
        self,
        keyword: str,
        page: int,
        page_size: int,
    ) -> Tuple[List[NewsItem], int]:
        raw = self._serp_client.search(
            query=keyword,
            engine="google_news",
            hl="ko",
            gl="kr",
        )

        news_results: List[dict] = raw.get("news_results") or []
        flattened = list(self._flatten_results(news_results))

        items = [self._to_news_item(entry) for entry in flattened]
        items.sort(key=lambda item: item.published_at or datetime.min, reverse=True)

        total_count = len(items)
        if total_count == 0:
            return [], 0

        start = (page - 1) * page_size
        end = start + page_size
        return items[start:end], total_count

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _flatten_results(news_results: List[dict]) -> List[dict]:
        """google_news 엔진은 'stories' 서브리스트를 가진 묶음 형식이 섞여 있다.
        flatten 하여 평탄화한 개별 뉴스 dict 만 남긴다."""
        flat: List[dict] = []
        for entry in news_results:
            stories = entry.get("stories")
            if isinstance(stories, list) and stories:
                flat.extend(stories)
            else:
                flat.append(entry)
        return flat

    def _to_news_item(self, entry: dict) -> NewsItem:
        return NewsItem(
            title=entry.get("title") or "",
            summary=entry.get("snippet") or entry.get("description"),
            source=self._extract_source(entry.get("source")),
            link=entry.get("link") or "",
            published_at=self._parse_published_at(entry.get("date")),
        )

    @staticmethod
    def _extract_source(source: Any) -> Optional[str]:
        if source is None:
            return None
        if isinstance(source, str):
            return source
        if isinstance(source, dict):
            return source.get("name") or source.get("title")
        return None

    @staticmethod
    def _parse_published_at(value: Any) -> Optional[datetime]:
        if not value or not isinstance(value, str):
            return None
        try:
            return parsedate_to_datetime(value)
        except (TypeError, ValueError):
            logger.debug("뉴스 게시 시간 파싱 실패: %s", value)
            return None
