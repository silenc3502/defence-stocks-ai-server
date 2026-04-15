"""유튜브 댓글 → 투자 심리 신호 산출 UseCase.

입력 소스 2가지 지원:
  - 메모리 댓글 리스트 (실시간 수집 직후 호출)
  - 저장된 PostgreSQL investment_youtube_video_comments (video_pks 또는 log_id)
"""
import logging
from typing import List, Optional

from app.domains.investment.adapter.outbound.persistence.investment_youtube_video_comment_repository import (
    InvestmentYoutubeVideoCommentRepository,
)
from app.domains.investment.adapter.outbound.signal.youtube_signal_builder import (
    YoutubeSignalBuilder,
)
from app.domains.investment.application.response.youtube_sentiment_signal import (
    YoutubeSentimentSignal,
)

logger = logging.getLogger(__name__)


class AnalyzeYoutubeSentimentUseCase:
    def __init__(
        self,
        signal_builder: YoutubeSignalBuilder,
        comment_repository: Optional[InvestmentYoutubeVideoCommentRepository] = None,
    ):
        """
        :param signal_builder: 필수
        :param comment_repository: `video_pks` 입력을 쓸 때만 필요 (PG 조회용)
        """
        self.signal_builder = signal_builder
        self.comment_repository = comment_repository

    def execute(
        self,
        comments: Optional[List[str]] = None,
        video_pks: Optional[List[int]] = None,
        top_n: int = 10,
    ) -> YoutubeSentimentSignal:
        """
        :param comments: 직접 전달하는 댓글 텍스트 리스트 (fast path)
        :param video_pks: PG 에서 로드할 MySQL 영상 PK 리스트 (slow path)
        :param top_n: 감성 그룹별 키워드 TOP N
        """
        if comments is None and video_pks is None:
            raise ValueError("comments 또는 video_pks 중 하나는 반드시 제공되어야 합니다")

        if comments is None:
            comments = self._load_from_storage(video_pks or [])

        return self.signal_builder.build(comments, top_n=top_n)

    def _load_from_storage(self, video_pks: List[int]) -> List[str]:
        if self.comment_repository is None:
            raise ValueError("video_pks 입력에는 comment_repository 가 필요합니다")

        texts: List[str] = []
        for pk in video_pks:
            payload = self.comment_repository.find_by_video_pk(pk)
            if not payload:
                continue
            for c in payload:
                text = c.get("text") if isinstance(c, dict) else None
                if text:
                    texts.append(text)
        print(f"  [Sentiment] PG 에서 {len(texts)}건 댓글 로드 (영상 {len(video_pks)}개)")
        return texts
