import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import httpx
from lxml import html as lxml_html

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
    """httpx 로 원문 HTML 을 가져오고 lxml 로 제목/본문 텍스트를 추출한다.

    사이트별 구조가 제각각이므로 `<title>` + 모든 `<p>` 텍스트 를 단순 결합하는
    naive 추출 방식을 사용한다. 원본 HTML 도 함께 저장하여 추후 재파싱 여지를 남긴다.
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
        extracted_title, plain_text = self._extract(html_text)

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
    def _extract(html_text: str) -> Tuple[Optional[str], str]:
        try:
            doc = lxml_html.fromstring(html_text)
        except Exception as exc:
            logger.debug("HTML 파싱 실패: %s", exc)
            return None, ""

        title_els = doc.xpath("//title/text()")
        title = title_els[0].strip() if title_els else None

        paragraphs = doc.xpath("//p//text()")
        text = "\n".join(p.strip() for p in paragraphs if p.strip())

        return title, text
