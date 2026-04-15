"""Analysis — 신호 기반 deterministic 투자 판단 + LLM 보강 분석."""
from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage

from app.domains.investment.adapter.outbound.agent.llm_invoker import invoke_llm
from app.domains.investment.adapter.outbound.agent.state import InvestmentState
from app.domains.investment.adapter.outbound.data_source.analysis_source import (
    run_ask_analysis,
)
from app.domains.investment.adapter.outbound.signal.investment_decision_analyzer import (
    InvestmentDecisionAnalyzer,
)
from app.domains.investment.application.response.investment_decision import (
    InvestmentDecision,
)
from app.domains.investment.application.response.news_event_signal import (
    NewsEventSignal,
)
from app.domains.investment.application.response.youtube_sentiment_signal import (
    YoutubeSentimentSignal,
)


def analysis_node(state: InvestmentState) -> Dict[str, Any]:
    parsed = state.get("parsed_query") or {}
    retrieval_data = state.get("retrieval_data") or ""

    print("\n" + "=" * 60)
    print(f"[Analysis] 시작")
    print(f"[Analysis] intent: {parsed.get('intent')}")
    print(f"[Analysis] retrieval_data 길이: {len(retrieval_data)}자")
    print(f"[Analysis] youtube_signal: {'있음' if state.get('youtube_signal') else '없음'}")
    print(f"[Analysis] news_signal: {'있음' if state.get('news_signal') else '없음'}")
    print("=" * 60)

    # 1. Deterministic 투자 판단 — 규칙 기반 (LLM 은 rationale 에만 개입)
    decision = _run_decision_analyzer(state)
    _print_decision(decision)

    # 2. 기존 AskAnalysisUseCase — 댓글 키워드 + 종목 DB 기반 LLM 분석 (보조 근거)
    print("[Analysis] AskAnalysisUseCase 보조 분석 호출")
    base_analysis = run_ask_analysis(state["input"])
    print(f"[Analysis] 보조 분석 결과 길이: {len(base_analysis)}자")

    # 3. 최종 analysis_result 텍스트 합성 — deterministic 판단 + 보조 분석
    combined = _compose_analysis_text(decision, base_analysis, retrieval_data)
    print(f"[Analysis] 최종 analysis_result 길이: {len(combined)}자")
    print("=" * 60)

    return {
        "analysis_result": combined,
        "investment_decision": decision.model_dump(),
        "messages": [AIMessage(content=combined, name="Analysis")],
    }


# ------------------------------------------------------------------
# Decision
# ------------------------------------------------------------------
def _run_decision_analyzer(state: InvestmentState) -> InvestmentDecision:
    parsed = state.get("parsed_query") or {}
    yt_payload = state.get("youtube_signal")
    news_payload = state.get("news_signal")

    yt_signal: Optional[YoutubeSentimentSignal] = (
        YoutubeSentimentSignal(**yt_payload) if yt_payload else None
    )
    news_signal: Optional[NewsEventSignal] = (
        NewsEventSignal(**news_payload) if news_payload else None
    )

    analyzer = InvestmentDecisionAnalyzer()
    return analyzer.analyze(
        youtube_signal=yt_signal,
        news_signal=news_signal,
        company=parsed.get("company"),
        intent=parsed.get("intent"),
    )


# ------------------------------------------------------------------
# Pretty-print
# ------------------------------------------------------------------
def _print_decision(decision: InvestmentDecision) -> None:
    print()
    print("  " + "┌" + "─" * 58 + "┐")
    print(f"  │ [InvestmentDecision]                                     │")
    print("  " + "├" + "─" * 58 + "┤")
    print(f"  │ direction    : {decision.direction}")
    print(f"  │ confidence   : {decision.confidence:.4f} ({decision.confidence:.1%})")
    print(f"  │ verdict      : {decision.verdict}")
    print("  " + "├" + "─" * 58 + "┤")
    print(f"  │ reasons.positive ({len(decision.reasons.positive)}):")
    for r in decision.reasons.positive:
        print(f"  │   + {r}")
    print(f"  │ reasons.negative ({len(decision.reasons.negative)}):")
    for r in decision.reasons.negative:
        print(f"  │   - {r}")
    print(f"  │ risk_factors ({len(decision.risk_factors)}):")
    for r in decision.risk_factors:
        print(f"  │   ! {r}")
    print("  " + "├" + "─" * 58 + "┤")
    print(f"  │ rationale:")
    for line in (decision.rationale or "").splitlines() or [""]:
        print(f"  │   {line}")
    print("  " + "└" + "─" * 58 + "┘")
    print()


# ------------------------------------------------------------------
# Final text composition
# ------------------------------------------------------------------
def _compose_analysis_text(
    decision: InvestmentDecision,
    base_analysis: str,
    retrieval_data: str,
) -> str:
    lines = [
        "[투자 판단 결과]",
        f"- direction : {decision.direction}",
        f"- confidence: {decision.confidence:.3f}",
        f"- verdict   : {decision.verdict}",
        "",
        f"[판단 근거 — rationale]",
        decision.rationale,
        "",
    ]
    if decision.reasons.positive:
        lines.append("[긍정 요인]")
        lines.extend(f"- {r}" for r in decision.reasons.positive)
        lines.append("")
    if decision.reasons.negative:
        lines.append("[부정 요인]")
        lines.extend(f"- {r}" for r in decision.reasons.negative)
        lines.append("")
    if decision.risk_factors:
        lines.append("[리스크]")
        lines.extend(f"- {r}" for r in decision.risk_factors)
        lines.append("")

    lines.append("[참고 분석 (댓글 키워드 + 종목 기반)]")
    lines.append(base_analysis)

    return "\n".join(lines)
