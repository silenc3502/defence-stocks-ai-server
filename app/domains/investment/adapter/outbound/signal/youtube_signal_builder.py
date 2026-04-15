"""유튜브 댓글 리스트 → YoutubeSentimentSignal 변환기."""
import logging
from typing import List

from app.domains.investment.adapter.outbound.signal.sentiment_analyzer import (
    SentimentAnalyzer,
)
from app.domains.investment.application.response.youtube_sentiment_signal import (
    SentimentDistribution,
    YoutubeSentimentSignal,
)
from app.domains.market_video.domain.service.noun_extractor import extract_nouns

logger = logging.getLogger(__name__)

_TOP_N = 10


class YoutubeSignalBuilder:
    def __init__(self, analyzer: SentimentAnalyzer):
        self.analyzer = analyzer

    def build(self, comments: List[str], top_n: int = _TOP_N) -> YoutubeSentimentSignal:
        if not comments:
            print(f"  [Signal][유튜브] 입력 댓글 0건 → 빈 신호 반환")
            return self._empty()

        print(f"  [Signal][유튜브] 분석 시작 (댓글 {len(comments)}건)")
        labels = self.analyzer.classify(comments)

        positive = [c for c, l in zip(comments, labels) if l == "positive"]
        neutral = [c for c, l in zip(comments, labels) if l == "neutral"]
        negative = [c for c, l in zip(comments, labels) if l == "negative"]

        total = len(comments)
        pos_ratio = len(positive) / total
        neu_ratio = len(neutral) / total
        neg_ratio = len(negative) / total
        score = (len(positive) - len(negative)) / total  # -1 ~ +1

        print(f"  [Signal][유튜브] 분포: 긍정 {pos_ratio:.1%} / 중립 {neu_ratio:.1%} / 부정 {neg_ratio:.1%}")
        print(f"  [Signal][유튜브] score = {score:+.3f}")

        bullish = self._top_nouns(positive, top_n)
        bearish = self._top_nouns(negative, top_n)
        topics = self._top_nouns(comments, top_n)

        print(f"  [Signal][유튜브] bullish_keywords: {bullish[:5]}{'...' if len(bullish) > 5 else ''}")
        print(f"  [Signal][유튜브] bearish_keywords: {bearish[:5]}{'...' if len(bearish) > 5 else ''}")

        return YoutubeSentimentSignal(
            sentiment_distribution=SentimentDistribution(
                positive=pos_ratio, neutral=neu_ratio, negative=neg_ratio
            ),
            sentiment_score=score,
            bullish_keywords=bullish,
            bearish_keywords=bearish,
            topics=topics,
            volume=total,
        )

    @staticmethod
    def _top_nouns(texts: List[str], top_n: int) -> List[str]:
        if not texts:
            return []
        try:
            nouns = extract_nouns(texts)
        except Exception as exc:
            logger.warning("명사 추출 실패: %s", exc)
            return []
        return [noun for noun, _ in nouns[:top_n]]

    @staticmethod
    def _empty() -> YoutubeSentimentSignal:
        return YoutubeSentimentSignal(
            sentiment_distribution=SentimentDistribution(positive=0.0, neutral=0.0, negative=0.0),
            sentiment_score=0.0,
            bullish_keywords=[],
            bearish_keywords=[],
            topics=[],
            volume=0,
        )
