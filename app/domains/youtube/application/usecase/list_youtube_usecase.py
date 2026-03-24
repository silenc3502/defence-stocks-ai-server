from typing import Optional

from app.domains.youtube.adapter.outbound.external.youtube_port import YoutubePort
from app.domains.youtube.application.response.youtube_list_response import (
    YoutubeListResponse,
    YoutubeVideoResponse,
)

SEARCH_QUERY = "한국 방산주 방위산업 주식"
MAX_RESULTS = 9


class ListYoutubeUseCase:
    def __init__(self, youtube_port: YoutubePort):
        self.youtube_port = youtube_port

    def execute(self, page_token: Optional[str] = None) -> YoutubeListResponse:
        result = self.youtube_port.search_videos(SEARCH_QUERY, MAX_RESULTS, page_token)

        items = [
            YoutubeVideoResponse(
                video_id=item.video_id,
                title=item.title,
                thumbnail_url=item.thumbnail_url,
                channel_name=item.channel_name,
                published_at=item.published_at,
                video_url=item.video_url,
            )
            for item in result.items
        ]

        return YoutubeListResponse(
            items=items,
            next_page_token=result.next_page_token,
            prev_page_token=result.prev_page_token,
            total_results=result.total_results,
        )
