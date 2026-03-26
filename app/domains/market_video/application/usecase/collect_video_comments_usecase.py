from app.domains.market_video.adapter.outbound.external.market_video_port import MarketVideoPort
from app.domains.market_video.adapter.outbound.persistence.market_video_repository import MarketVideoRepository
from app.domains.market_video.adapter.outbound.persistence.video_comment_repository import VideoCommentRepository
from app.domains.market_video.application.response.video_comments_response import (
    CollectCommentsResponse,
    CommentItem,
    VideoComments,
)
from app.domains.market_video.domain.entity.video_comment import VideoComment
from app.domains.market_video.domain.service.defence_filter import MAX_VIDEOS

MAX_COMMENTS_PER_VIDEO = 50


class CollectVideoCommentsUseCase:
    def __init__(
        self,
        market_video_port: MarketVideoPort,
        market_video_repository: MarketVideoRepository,
        video_comment_repository: VideoCommentRepository,
    ):
        self.market_video_port = market_video_port
        self.market_video_repository = market_video_repository
        self.video_comment_repository = video_comment_repository

    def execute(self) -> CollectCommentsResponse:
        saved_videos = self.market_video_repository.find_all_ordered_by_published_at(MAX_VIDEOS)

        if not saved_videos:
            return CollectCommentsResponse(videos=[], total_videos=0, total_comments=0)

        video_comments_list = []
        total_comments = 0

        for video in saved_videos:
            try:
                api_comments = self.market_video_port.get_video_comments(
                    video.video_id, MAX_COMMENTS_PER_VIDEO, "relevance"
                )
            except Exception:
                api_comments = []

            self.video_comment_repository.delete_by_video_id(video.video_id)

            for c in api_comments:
                try:
                    entity = VideoComment(
                        comment_id=c.comment_id,
                        video_id=video.video_id,
                        author_name=c.author_name,
                        text=c.text,
                        published_at=c.published_at,
                        like_count=c.like_count,
                    )
                    self.video_comment_repository.save(entity)
                except Exception:
                    pass

            saved_comments = self.video_comment_repository.find_by_video_id(video.video_id)

            items = [
                CommentItem(
                    comment_id=c.comment_id,
                    author_name=c.author_name,
                    text=c.text,
                    published_at=c.published_at,
                    like_count=c.like_count,
                )
                for c in saved_comments
            ]

            video_comments_list.append(
                VideoComments(
                    video_id=video.video_id,
                    title=video.title,
                    comments=items,
                    comment_count=len(items),
                )
            )
            total_comments += len(items)

        return CollectCommentsResponse(
            videos=video_comments_list,
            total_videos=len(video_comments_list),
            total_comments=total_comments,
        )
