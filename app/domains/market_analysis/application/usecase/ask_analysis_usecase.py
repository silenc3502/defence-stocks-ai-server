from app.domains.market_analysis.application.request.analysis_question_request import AnalysisQuestionRequest
from app.domains.market_analysis.application.response.analysis_answer_response import AnalysisAnswerResponse
from app.domains.market_analysis.domain.service.analysis_chain import create_analysis_chain
from app.domains.market_analysis.domain.service.context_builder import (
    build_keywords_context,
    build_recommendations_context,
    build_stocks_context,
)
from app.domains.market_video.adapter.outbound.persistence.market_video_repository import MarketVideoRepository
from app.domains.market_video.adapter.outbound.persistence.video_comment_repository import VideoCommentRepository
from app.domains.market_video.domain.service.defence_filter import MAX_VIDEOS
from app.domains.market_video.domain.service.noun_extractor import extract_nouns
from app.domains.stock_theme.adapter.outbound.persistence.defence_stock_repository import DefenceStockRepository


class AskAnalysisUseCase:
    def __init__(
        self,
        market_video_repository: MarketVideoRepository,
        video_comment_repository: VideoCommentRepository,
        defence_stock_repository: DefenceStockRepository,
    ):
        self.market_video_repository = market_video_repository
        self.video_comment_repository = video_comment_repository
        self.defence_stock_repository = defence_stock_repository

    def execute(self, request: AnalysisQuestionRequest) -> AnalysisAnswerResponse:
        saved_videos = self.market_video_repository.find_all_ordered_by_published_at(MAX_VIDEOS)

        all_texts = []
        for video in saved_videos:
            comments = self.video_comment_repository.find_by_video_id(video.video_id)
            all_texts.extend([c.text for c in comments])

        noun_counts = extract_nouns(all_texts) if all_texts else []
        db_stocks = self.defence_stock_repository.find_all()

        keywords_context = build_keywords_context(noun_counts)
        stocks_context = build_stocks_context(db_stocks)
        recommendations_context = build_recommendations_context(db_stocks, noun_counts)

        chain = create_analysis_chain()

        result = chain.invoke({
            "keywords": keywords_context,
            "stocks": stocks_context,
            "recommendations": recommendations_context,
            "question": request.question,
        })

        return AnalysisAnswerResponse(
            question=request.question,
            answer=result.content,
        )
