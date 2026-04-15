"""뉴스 본문 → 투자 이벤트 신호 산출 UseCase."""
import logging
from typing import Any, Dict, List

from app.domains.investment.adapter.outbound.signal.news_signal_builder import (
    NewsSignalBuilder,
)
from app.domains.investment.application.response.news_event_signal import (
    NewsEventSignal,
)

logger = logging.getLogger(__name__)


class AnalyzeNewsEventsUseCase:
    def __init__(self, signal_builder: NewsSignalBuilder):
        self.signal_builder = signal_builder

    def execute(self, news_items: List[Dict[str, Any]]) -> NewsEventSignal:
        """
        :param news_items: [{title, content, source, link, published_at}, ...]
                           content 키에 본문 텍스트가 있어야 한다.
        """
        return self.signal_builder.build(news_items)
