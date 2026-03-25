from datetime import datetime, timedelta, timezone

from app.domains.market_video.adapter.outbound.external.market_video_port import MarketVideoPort
from app.domains.market_video.application.response.market_video_list_response import (
    MarketVideoItem,
    MarketVideoListResponse,
)
from app.domains.market_video.domain.service.defence_filter import (
    DEFENCE_CHANNELS,
    MAX_VIDEOS,
    SEARCH_DAYS,
    contains_defence_keyword,
)


class ListMarketVideoUseCase:
    def __init__(self, market_video_port: MarketVideoPort):
        self.market_video_port = market_video_port

    def execute(self) -> MarketVideoListResponse:
        if not DEFENCE_CHANNELS:
            return MarketVideoListResponse(items=[], total_count=0)

        published_after = (datetime.now(timezone.utc) - timedelta(days=SEARCH_DAYS)).isoformat()

        all_videos = []
        for channel_id in DEFENCE_CHANNELS:
            try:
                videos = self.market_video_port.get_channel_videos(channel_id, published_after, max_results=10)
                print(f"[market-video] 채널 {channel_id}: {len(videos)}개 영상 조회")
                for v in videos:
                    print(f"  - {v.title}")
            except Exception as e:
                print(f"[market-video] 채널 {channel_id} 조회 실패: {e}")
                continue
            all_videos.extend(videos)

        print(f"[market-video] 전체 영상 수: {len(all_videos)}")

        filtered_videos = [v for v in all_videos if contains_defence_keyword(v.title)]
        print(f"[market-video] 방산 키워드 필터 후: {len(filtered_videos)}개")

        if not filtered_videos:
            return MarketVideoListResponse(items=[], total_count=0)

        video_ids = [v.video_id for v in filtered_videos]
        stats = self.market_video_port.get_video_statistics(video_ids)

        for video in filtered_videos:
            video.view_count = stats.get(video.video_id, 0)

        filtered_videos.sort(key=lambda v: (v.published_at, v.view_count or 0), reverse=True)
        top_videos = filtered_videos[:MAX_VIDEOS]

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
            for v in top_videos
        ]

        return MarketVideoListResponse(items=items, total_count=len(items))
