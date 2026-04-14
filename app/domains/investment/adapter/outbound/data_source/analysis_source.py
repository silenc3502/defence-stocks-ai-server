"""시장 분석 데이터 소스 — AskAnalysisUseCase 재사용."""
import logging

from app.domains.market_analysis.application.request.analysis_question_request import (
    AnalysisQuestionRequest,
)
from app.domains.market_analysis.application.usecase.ask_analysis_usecase import (
    AskAnalysisUseCase,
)
from app.domains.market_video.adapter.outbound.persistence.market_video_repository_impl import (
    MarketVideoRepositoryImpl,
)
from app.domains.market_video.adapter.outbound.persistence.video_comment_repository_impl import (
    VideoCommentRepositoryImpl,
)
from app.domains.stock_theme.adapter.outbound.persistence.defence_stock_repository_impl import (
    DefenceStockRepositoryImpl,
)
from app.infrastructure.database.session import SessionLocal

logger = logging.getLogger(__name__)


def run_ask_analysis(question: str) -> str:
    """DB 의 댓글 키워드 + 종목 데이터로 LLM 분석 체인 실행."""
    print(f"  [시장분석] AskAnalysisUseCase 호출")
    db = SessionLocal()
    try:
        usecase = AskAnalysisUseCase(
            market_video_repository=MarketVideoRepositoryImpl(db),
            video_comment_repository=VideoCommentRepositoryImpl(db),
            defence_stock_repository=DefenceStockRepositoryImpl(db),
        )
        result = usecase.execute(AnalysisQuestionRequest(question=question))
        print(f"  [시장분석] 결과 길이: {len(result.answer)}자")
        return result.answer
    except Exception as exc:
        print(f"  [시장분석] ❌ 실패: {exc}")
        logger.error("AskAnalysisUseCase 실패: %s", exc, exc_info=True)
        return f"(기존 분석 UseCase 실패: {exc})"
    finally:
        db.close()
