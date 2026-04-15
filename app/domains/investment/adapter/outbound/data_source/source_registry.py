"""required_data 키 → handler 매핑 테이블.

Handler 시그니처: `(keyword: Optional[str]) -> Tuple[str, Optional[Dict]]`
  - 반환값은 (text_summary, signal_payload) 튜플
  - text_summary 는 Retrieval Agent 의 retrieval_data 에 포함될 텍스트
  - signal_payload 는 구조화된 지표(dict). 없으면 None.
    Analyzer / Analysis Agent 가 별도로 소비한다.
"""
from typing import Any, Callable, Dict, Optional, Tuple

from app.domains.investment.adapter.outbound.data_source.news_source import fetch_news
from app.domains.investment.adapter.outbound.data_source.stock_source import (
    fetch_stock_data,
)
from app.domains.investment.adapter.outbound.data_source.youtube_source import (
    fetch_youtube,
)

SourceResult = Tuple[str, Optional[Dict[str, Any]]]
SourceHandler = Callable[[Optional[str]], SourceResult]

SOURCE_REGISTRY: Dict[str, SourceHandler] = {
    "뉴스": fetch_news,
    "유튜브": fetch_youtube,
    "종목": fetch_stock_data,
    "방산주": fetch_stock_data,
    # TODO: "재무": fetch_financials,
    # TODO: "시장_데이터": fetch_market_data,
}

# 신호 payload 를 State 에 저장할 때 쓰는 키 매핑
SIGNAL_STATE_KEY: Dict[str, str] = {
    "뉴스": "news_signal",
    "유튜브": "youtube_signal",
}
