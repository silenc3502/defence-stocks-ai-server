from abc import ABC, abstractmethod
from typing import List, Tuple

from app.domains.news_search.application.response.news_search_response import NewsItem


class NewsSearchPort(ABC):
    """뉴스 검색 외부 연동 Port.

    Application Layer 는 이 Port 만을 통해 뉴스를 검색한다.
    """

    @abstractmethod
    def search(
        self,
        keyword: str,
        page: int,
        page_size: int,
    ) -> Tuple[List[NewsItem], int]:
        """
        :param keyword: 검색 키워드
        :param page: 1-based 페이지 번호
        :param page_size: 페이지당 결과 수
        :return: (뉴스 리스트, 전체 결과 수)
        """
        raise NotImplementedError
