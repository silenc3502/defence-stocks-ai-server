from app.domains.news.adapter.outbound.external.news_search_port import (
    NewsSearchPort,
)
from app.domains.news.application.response.news_search_response import (
    NewsSearchResponse,
)


class SearchNewsUseCase:
    def __init__(self, news_search_port: NewsSearchPort):
        self.news_search_port = news_search_port

    def execute(self, keyword: str, page: int, page_size: int) -> NewsSearchResponse:
        items, total_count = self.news_search_port.search(
            keyword=keyword,
            page=page,
            page_size=page_size,
        )

        return NewsSearchResponse(
            items=items,
            current_page=page,
            page_size=page_size,
            total_count=total_count,
        )
