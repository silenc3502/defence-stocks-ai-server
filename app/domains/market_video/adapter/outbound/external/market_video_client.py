from datetime import datetime

import httpx

from app.domains.market_video.adapter.outbound.external.market_video_port import (
    ChannelVideoItem,
    MarketVideoPort,
)
from app.infrastructure.config.settings import settings

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


class MarketVideoClient(MarketVideoPort):
    def get_channel_videos(self, channel_id: str, published_after: str, max_results: int) -> list[ChannelVideoItem]:
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "order": "date",
            "publishedAfter": published_after,
            "maxResults": max_results,
            "key": settings.youtube_api_key,
        }

        response = httpx.get(YOUTUBE_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()

        items = []
        for item in data.get("items", []):
            snippet = item["snippet"]
            video_id = item["id"]["videoId"]
            items.append(
                ChannelVideoItem(
                    video_id=video_id,
                    title=snippet["title"],
                    thumbnail_url=snippet["thumbnails"]["high"]["url"],
                    channel_name=snippet["channelTitle"],
                    published_at=datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")),
                    video_url=f"https://www.youtube.com/watch?v={video_id}",
                )
            )

        return items

    def get_video_statistics(self, video_ids: list[str]) -> dict[str, int]:
        if not video_ids:
            return {}

        params = {
            "part": "statistics",
            "id": ",".join(video_ids),
            "key": settings.youtube_api_key,
        }

        response = httpx.get(YOUTUBE_VIDEOS_URL, params=params)
        response.raise_for_status()
        data = response.json()

        result = {}
        for item in data.get("items", []):
            video_id = item["id"]
            view_count = int(item["statistics"].get("viewCount", 0))
            result[video_id] = view_count

        return result
