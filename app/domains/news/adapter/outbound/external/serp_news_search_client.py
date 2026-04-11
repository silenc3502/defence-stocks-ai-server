import logging
from datetime import datetime
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
            source=self._extract_source(entry.get("source")),
            link=entry.get("link") or "",
            published_at=self._parse_published_at(entry),
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
    def _parse_published_at(entry: dict) -> Optional[datetime]:
        """`iso_date` (ISO 8601) 를 우선 사용하고, 없으면 파싱하지 않는다."""
        iso_date = entry.get("iso_date")
        if isinstance(iso_date, str) and iso_date:
            try:
                # "2026-04-06T02:37:00Z" 형태 지원
                return datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
            except ValueError:
                logger.debug("뉴스 iso_date 파싱 실패: %s", iso_date)
        return None
