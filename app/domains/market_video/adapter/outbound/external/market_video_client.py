from datetime import datetime

import httpx

from app.domains.market_video.adapter.outbound.external.market_video_port import (
    ChannelVideoItem,
    MarketVideoPort,
    VideoCommentItem,
)
from app.infrastructure.config.settings import settings

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_COMMENTS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"


class MarketVideoClient(MarketVideoPort):
    def get_channel_videos(self, channel_id: str, published_after: str, max_results: int, query: str = "") -> list[ChannelVideoItem]:
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "order": "date",
            "publishedAfter": published_after,
            "maxResults": max_results,
            "key": settings.youtube_api_key,
        }
        if query:
            params["q"] = query

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

    def get_video_comments(self, video_id: str, max_results: int, order: str = "relevance") -> list[VideoCommentItem]:
        collected = []
        seen_ids = set()
        page_token = None

        while len(collected) < max_results:
            params = {
                "part": "snippet",
                "videoId": video_id,
                "maxResults": min(100, max_results - len(collected)),
                "order": order,
                "textFormat": "plainText",
                "key": settings.youtube_api_key,
            }
            if page_token:
                params["pageToken"] = page_token

            try:
                response = httpx.get(YOUTUBE_COMMENTS_URL, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError:
                return collected

            data = response.json()

            for item in data.get("items", []):
                comment_id = item["id"]
                if comment_id in seen_ids:
                    continue
                seen_ids.add(comment_id)

                snippet = item["snippet"]["topLevelComment"]["snippet"]
                text = snippet.get("textDisplay", "").strip()
                if not text:
                    continue

                collected.append(
                    VideoCommentItem(
                        comment_id=comment_id,
                        author_name=snippet["authorDisplayName"],
                        text=text,
                        published_at=datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")),
                        like_count=snippet.get("likeCount", 0),
                    )
                )

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return collected
