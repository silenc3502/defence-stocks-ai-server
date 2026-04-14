"""required_data 키 → handler 매핑 테이블.

Handler 시그니처: `(keyword: Optional[str]) -> str`
  - keyword 는 parsed_query.company (종목명 또는 None)
  - 각 handler 는 None 인 경우 자체 fallback 쿼리를 사용한다
"""
from typing import Callable, Dict, Optional

from app.domains.investment.adapter.outbound.data_source.news_source import fetch_news
from app.domains.investment.adapter.outbound.data_source.stock_source import (
    fetch_stock_data,
)
from app.domains.investment.adapter.outbound.data_source.youtube_source import (
    fetch_youtube,
)

SourceHandler = Callable[[Optional[str]], str]

SOURCE_REGISTRY: Dict[str, SourceHandler] = {
    "뉴스": fetch_news,
    "유튜브": fetch_youtube,
    "종목": fetch_stock_data,
    "방산주": fetch_stock_data,
    # TODO: "재무": fetch_financials,
    # TODO: "시장_데이터": fetch_market_data,
}
