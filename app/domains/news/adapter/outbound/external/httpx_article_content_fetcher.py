import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
import trafilatura

from app.domains.news.adapter.outbound.external.article_content_fetcher import (
    ArticleContentFetcher,
)
from app.domains.news.application.exceptions import ArticleFetchError

logger = logging.getLogger(__name__)

_DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; DefenceStocksBot/1.0; "
    "+https://example.com/bot)"
)


class HttpxArticleContentFetcher(ArticleContentFetcher):
    """httpx 로 원문 HTML 을 가져오고 trafilatura 로 본문/제목을 추출한다.

    trafilatura 는 boilerplate(광고/네비/사이드바) 를 제거하고 본문 단락만
    추출하는 전용 라이브러리다. 사이트별 구조에 강건함.
    """

    def __init__(self, timeout_seconds: float = 10.0):
        self._timeout = timeout_seconds

    def fetch(self, link: str) -> Dict[str, Any]:
        try:
            with httpx.Client(
                timeout=self._timeout,
                follow_redirects=True,
                headers={"User-Agent": _DEFAULT_USER_AGENT},
            ) as client:
                response = client.get(link)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "기사 본문 fetch HTTP 오류 (link=%s, status=%s)",
                link,
                exc.response.status_code,
            )
            raise ArticleFetchError(
                f"기사 원문 응답 오류 ({exc.response.status_code})"
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("기사 본문 fetch 네트워크 오류 (link=%s): %s", link, exc)
            raise ArticleFetchError(f"기사 원문 접근 실패: {exc}") from exc

        html_text = response.text
        extracted_title, plain_text = self._extract(html_text, link)

        return {
            "url": link,
            "final_url": str(response.url),
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type"),
            "fetched_at": datetime.now().isoformat(),
            "extracted_title": extracted_title,
            "text": plain_text,
            "html": html_text,
        }

    @staticmethod
    def _extract(html_text: str, url: str) -> tuple[Optional[str], str]:
        try:
            extracted = trafilatura.extract(
                html_text,
                url=url,
                favor_precision=True,
                include_comments=False,
                include_tables=False,
                with_metadata=False,
                output_format="txt",
            )
            text = (extracted or "").strip()
        except Exception as exc:
            logger.debug("trafilatura 본문 추출 실패: %s", exc)
            text = ""

        title: Optional[str] = None
        try:
            metadata = trafilatura.extract_metadata(html_text, default_url=url)
            if metadata is not None and metadata.title:
                title = metadata.title.strip()
        except Exception as exc:
            logger.debug("trafilatura 제목 추출 실패: %s", exc)

        return title, text
