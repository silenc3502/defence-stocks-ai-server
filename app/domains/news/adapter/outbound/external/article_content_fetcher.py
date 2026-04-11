from abc import ABC, abstractmethod
from typing import Any, Dict


class ArticleContentFetcher(ABC):
    """원문 링크에 접속하여 기사 본문을 가져오는 Port."""

    @abstractmethod
    def fetch(self, link: str) -> Dict[str, Any]:
        """
        :param link: 기사 원문 URL
        :return: JSONB 로 저장 가능한 dict (html, 추출 텍스트, fetched_at 등)
        :raises ArticleFetchError: 네트워크 오류, 4xx/5xx, 파싱 불가
        """
        raise NotImplementedError
