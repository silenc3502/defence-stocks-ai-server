from app.domains.market_video.adapter.outbound.persistence.market_video_repository import MarketVideoRepository
from app.domains.market_video.adapter.outbound.persistence.video_comment_repository import VideoCommentRepository
from app.domains.market_video.domain.service.defence_filter import MAX_VIDEOS
from app.domains.market_video.domain.service.noun_extractor import extract_nouns
from app.domains.stock_theme.application.response.stock_recommendation_response import (
    MatchedStock,
    MatchedTheme,
    StockRecommendationResponse,
)
from app.domains.stock_theme.domain.service.defence_stock_mapping import (
    find_stocks_by_keywords,
    find_themes_by_keywords,
)

TOP_KEYWORDS = 50


class RecommendStocksUseCase:
    def __init__(
        self,
        market_video_repository: MarketVideoRepository,
        video_comment_repository: VideoCommentRepository,
    ):
        self.market_video_repository = market_video_repository
        self.video_comment_repository = video_comment_repository

    def execute(self) -> StockRecommendationResponse:
        saved_videos = self.market_video_repository.find_all_ordered_by_published_at(MAX_VIDEOS)

        all_texts = []
        for video in saved_videos:
            comments = self.video_comment_repository.find_by_video_id(video.video_id)
            all_texts.extend([c.text for c in comments])

        if not all_texts:
            return StockRecommendationResponse(stocks=[], themes=[], input_keywords_count=0)

        noun_counts = extract_nouns(all_texts)
        top_nouns = [noun for noun, _ in noun_counts[:TOP_KEYWORDS]]

        matched_stocks = find_stocks_by_keywords(top_nouns)
        matched_themes = find_themes_by_keywords(top_nouns)

        stocks = [
            MatchedStock(**s) for s in matched_stocks
        ]
        themes = [
            MatchedTheme(**t) for t in matched_themes
        ]

        return StockRecommendationResponse(
            stocks=stocks,
            themes=themes,
            input_keywords_count=len(top_nouns),
        )
