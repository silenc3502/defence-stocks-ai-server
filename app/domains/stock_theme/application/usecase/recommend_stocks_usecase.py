from app.domains.market_video.adapter.outbound.persistence.market_video_repository import MarketVideoRepository
from app.domains.market_video.adapter.outbound.persistence.video_comment_repository import VideoCommentRepository
from app.domains.market_video.domain.service.defence_filter import MAX_VIDEOS
from app.domains.market_video.domain.service.noun_extractor import extract_nouns
from app.domains.stock_theme.adapter.outbound.persistence.defence_stock_repository import DefenceStockRepository
from app.domains.stock_theme.application.response.stock_recommendation_response import (
    MatchedStock,
    StockRecommendationResponse,
)
from app.domains.stock_theme.domain.service.recommendation_reason import (
    SYSTEM_MESSAGE,
    build_reason_prompt,
)
from app.infrastructure.llm.llm_port import LLMPort

TOP_KEYWORDS = 50


class RecommendStocksUseCase:
    def __init__(
        self,
        market_video_repository: MarketVideoRepository,
        video_comment_repository: VideoCommentRepository,
        defence_stock_repository: DefenceStockRepository,
        llm_port: LLMPort,
    ):
        self.market_video_repository = market_video_repository
        self.video_comment_repository = video_comment_repository
        self.defence_stock_repository = defence_stock_repository
        self.llm_port = llm_port

    def execute(self) -> StockRecommendationResponse:
        saved_videos = self.market_video_repository.find_all_ordered_by_published_at(MAX_VIDEOS)

        all_texts = []
        for video in saved_videos:
            comments = self.video_comment_repository.find_by_video_id(video.video_id)
            all_texts.extend([c.text for c in comments])

        if not all_texts:
            return StockRecommendationResponse(stocks=[], input_keywords_count=0)

        noun_counts = extract_nouns(all_texts)
        top_nouns = [noun for noun, _ in noun_counts[:TOP_KEYWORDS]]
        keyword_set = {kw.lower() for kw in top_nouns}

        db_stocks = self.defence_stock_repository.find_all()

        matched_stocks = []
        for stock in db_stocks:
            theme_set = {t.lower() for t in stock.themes}
            name_keywords = {stock.name.lower()}
            matchable = theme_set | name_keywords

            matched = keyword_set & matchable
            if matched:
                prompt = build_reason_prompt(stock.name, stock.code, stock.themes, sorted(matched))
                try:
                    reason = self.llm_port.generate(prompt, SYSTEM_MESSAGE)
                except Exception:
                    reason = f"{stock.name}은(는) {', '.join(sorted(matched))} 키워드와 관련이 있어 추천되었습니다."

                matched_stocks.append(
                    MatchedStock(
                        name=stock.name,
                        code=stock.code,
                        themes=stock.themes,
                        matched_keywords=sorted(matched),
                        relevance_score=len(matched),
                        reason=reason,
                    )
                )

        matched_stocks.sort(key=lambda x: x.relevance_score, reverse=True)

        return StockRecommendationResponse(
            stocks=matched_stocks,
            input_keywords_count=len(top_nouns),
        )
