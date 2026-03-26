from app.domains.market_video.adapter.outbound.persistence.video_comment_repository import VideoCommentRepository
from app.domains.market_video.adapter.outbound.persistence.market_video_repository import MarketVideoRepository
from app.domains.market_video.application.response.noun_extraction_response import (
    NounExtractionResponse,
    NounFrequency,
)
from app.domains.market_video.domain.service.defence_filter import MAX_VIDEOS
from app.domains.market_video.domain.service.noun_extractor import extract_nouns


class ExtractNounsUseCase:
    def __init__(
        self,
        market_video_repository: MarketVideoRepository,
        video_comment_repository: VideoCommentRepository,
    ):
        self.market_video_repository = market_video_repository
        self.video_comment_repository = video_comment_repository

    def execute(self) -> NounExtractionResponse:
        saved_videos = self.market_video_repository.find_all_ordered_by_published_at(MAX_VIDEOS)

        all_texts = []
        for video in saved_videos:
            comments = self.video_comment_repository.find_by_video_id(video.video_id)
            all_texts.extend([c.text for c in comments])

        if not all_texts:
            return NounExtractionResponse(nouns=[], total_nouns=0, total_comments=0)

        noun_counts = extract_nouns(all_texts)

        nouns = [
            NounFrequency(noun=noun, count=count)
            for noun, count in noun_counts
        ]

        return NounExtractionResponse(
            nouns=nouns,
            total_nouns=len(nouns),
            total_comments=len(all_texts),
        )
