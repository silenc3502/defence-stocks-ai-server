from datetime import datetime, timedelta, timezone

from app.domains.market_video.adapter.outbound.external.market_video_port import MarketVideoPort
from app.domains.market_video.adapter.outbound.persistence.market_video_repository import MarketVideoRepository
from app.domains.market_video.application.response.market_video_list_response import (
    MarketVideoItem,
    MarketVideoListResponse,
)
from app.domains.market_video.domain.entity.market_video import MarketVideo
from app.domains.market_video.domain.service.defence_filter import (
    DEFENCE_CHANNELS,
    DEFENCE_SEARCH_QUERIES,
    MAX_VIDEOS,
    SEARCH_DAYS,
    contains_defence_keyword,
)


class ListMarketVideoUseCase:
    def __init__(self, market_video_port: MarketVideoPort, market_video_repository: MarketVideoRepository):
        self.market_video_port = market_video_port
        self.market_video_repository = market_video_repository

    def execute(self) -> MarketVideoListResponse:
        if not DEFENCE_CHANNELS:
            return self._build_response_from_db()

        published_after = (datetime.now(timezone.utc) - timedelta(days=SEARCH_DAYS)).isoformat()

        all_videos = []
        seen_video_ids = set()
        for channel_id in DEFENCE_CHANNELS:
            for query in DEFENCE_SEARCH_QUERIES:
                try:
                    videos = self.market_video_port.get_channel_videos(channel_id, published_after, max_results=5, query=query)
                except Exception:
                    continue
                for v in videos:
                    if v.video_id not in seen_video_ids:
                        seen_video_ids.add(v.video_id)
                        all_videos.append(v)

        filtered_videos = [v for v in all_videos if contains_defence_keyword(v.title)]

        if filtered_videos:
            video_ids = [v.video_id for v in filtered_videos]
            stats = self.market_video_port.get_video_statistics(video_ids)

            for video in filtered_videos:
                video.view_count = stats.get(video.video_id, 0)

            filtered_videos.sort(key=lambda v: (v.published_at, v.view_count or 0), reverse=True)
            top_videos = filtered_videos[:MAX_VIDEOS]

            self.market_video_repository.delete_all()
            for v in top_videos:
                self._save_video(v)

        return self._build_response_from_db()

    def _save_video(self, v) -> None:
        try:
            entity = MarketVideo(
                video_id=v.video_id,
                title=v.title,
                channel_name=v.channel_name,
                published_at=v.published_at,
                view_count=v.view_count or 0,
                thumbnail_url=v.thumbnail_url,
                video_url=v.video_url,
            )
            self.market_video_repository.save(entity)
        except Exception:
            pass

    def _build_response_from_db(self) -> MarketVideoListResponse:
        saved_videos = self.market_video_repository.find_all_ordered_by_published_at(MAX_VIDEOS)

        items = [
            MarketVideoItem(
                video_id=v.video_id,
                title=v.title,
                thumbnail_url=v.thumbnail_url,
                channel_name=v.channel_name,
                published_at=v.published_at,
                video_url=v.video_url,
                view_count=v.view_count,
            )
            for v in saved_videos
        ]

        return MarketVideoListResponse(items=items, total_count=len(items))
