"""투자 판단 Analyzer.

규칙:
- direction / confidence / verdict 는 deterministic rule 기반 (동일 입력 → 동일 출력).
- LLM 은 rationale (서술형 설명) 생성에만 사용된다.
- 입력 신호가 부족하면 보수적 기본값(hold, confidence≤0.3)을 반환한다.

공식:
  news_score = Σ(positive impact weight) - Σ(negative impact weight)
      threshold = 1.5 (기본)

  direction =
      bullish   if news_score >  threshold
      bearish   if news_score < -threshold
      neutral   otherwise

  confidence = sigmoid(W_NEWS * |news_score| + W_SENT * |sentiment_score|)
      W_NEWS = 0.5, W_SENT = 1.0 (뉴스 = 주 신호, 유튜브 sentiment = 보조)

  verdict =
      buy     if direction=bullish and confidence>0.6
      sell    if direction=bearish and confidence>0.6
      hold    otherwise
"""
import json
import logging
import math
from typing import Any, Dict, Optional, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from app.domains.investment.application.response.investment_decision import (
    DecisionReasons,
    InvestmentDecision,
)
from app.domains.investment.application.response.news_event_signal import (
    NewsEventSignal,
)
from app.domains.investment.application.response.youtube_sentiment_signal import (
    YoutubeSentimentSignal,
)
from app.infrastructure.agent.llm import get_chat_llm

logger = logging.getLogger(__name__)

# Impact → score 가중치
_IMPACT_WEIGHT = {"high": 3.0, "medium": 2.0, "low": 1.0}

# 규칙 파라미터 (튜닝 가능)
_NEWS_DIRECTION_THRESHOLD = 1.5
_W_NEWS = 0.5
_W_SENTIMENT = 1.0
_VERDICT_CONFIDENCE_CUTOFF = 0.6

# 신호 부족 기준
_MIN_COMMENT_VOLUME = 20
_FALLBACK_CONFIDENCE = 0.2

_RATIONALE_SYSTEM_PROMPT = (
    "당신은 투자 판단 결과를 자연스러운 한국어 문장으로 설명하는 분석가입니다.\n"
    "판단 결과(direction, confidence, verdict, reasons, risk_factors)를 받아 2-4문장으로 간결하게 "
    "근거를 요약하세요. 판단 자체를 변경하거나 다른 verdict 를 제안하지 말고, 주어진 판단을 설명만 하세요.\n"
    "투자 권유가 아닌 정보 제공임을 명시할 필요는 없습니다 (상위에서 처리됨)."
)


def _sigmoid(x: float) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


class InvestmentDecisionAnalyzer:
    def analyze(
        self,
        youtube_signal: Optional[YoutubeSentimentSignal],
        news_signal: Optional[NewsEventSignal],
        company: Optional[str],
        intent: Optional[str],
    ) -> InvestmentDecision:
        print("\n  " + "━" * 58)
        print(f"  [Decision] 투자 판단 산출 시작")
        print(f"  [Decision] company={company!r}, intent={intent!r}")

        # 입력 신호 요약 (계산 전)
        self._print_input_summary(youtube_signal, news_signal)

        # 1. 보수적 fallback — 신호 부족
        print("\n  [Decision] 단계 1: 신호 충분성 체크")
        insufficient, reason = self._check_sufficiency(youtube_signal, news_signal)
        if insufficient:
            print(f"  [Decision] ⚠ 신호 부족: {reason}")
            print(f"  [Decision] → 보수적 기본값 (hold, confidence=0.2)")
            return self._insufficient_decision(company, intent)
        print(f"  [Decision] ✓ 신호 충분 — 규칙 기반 계산 진행")
        assert news_signal is not None  # type guard

        # 2. news_score — 가중치 기반 합산
        print("\n  [Decision] 단계 2: news_score 계산 (IMPACT 가중치)")
        news_score = self._compute_news_score(news_signal, verbose=True)
        print(f"  [Decision] → news_score = {news_score:+.2f} (threshold=±{_NEWS_DIRECTION_THRESHOLD})")

        # 3. direction — news 만 적용
        print("\n  [Decision] 단계 3: direction 결정 (news_score vs threshold)")
        if news_score > _NEWS_DIRECTION_THRESHOLD:
            direction: str = "bullish"
            print(f"  [Decision] {news_score:+.2f} > +{_NEWS_DIRECTION_THRESHOLD} → bullish")
        elif news_score < -_NEWS_DIRECTION_THRESHOLD:
            direction = "bearish"
            print(f"  [Decision] {news_score:+.2f} < -{_NEWS_DIRECTION_THRESHOLD} → bearish")
        else:
            direction = "neutral"
            print(f"  [Decision] |{news_score:+.2f}| ≤ {_NEWS_DIRECTION_THRESHOLD} → neutral")

        # 4. confidence — sigmoid(W_NEWS*|news| + W_SENT*|sentiment|)
        print("\n  [Decision] 단계 4: confidence 계산 (sigmoid)")
        sent_score = youtube_signal.sentiment_score if youtube_signal else 0.0
        news_term = _W_NEWS * abs(news_score)
        sent_term = _W_SENTIMENT * abs(sent_score)
        raw_confidence = news_term + sent_term
        confidence = _sigmoid(raw_confidence)
        print(f"  [Decision]   news term : {_W_NEWS} * |{news_score:+.2f}| = {news_term:.3f}")
        print(f"  [Decision]   sent term : {_W_SENTIMENT} * |{sent_score:+.3f}| = {sent_term:.3f}")
        print(f"  [Decision]   sigmoid({raw_confidence:.3f}) = {confidence:.4f}")

        # 5. verdict
        print("\n  [Decision] 단계 5: verdict 결정 (direction + confidence)")
        if direction == "bullish" and confidence > _VERDICT_CONFIDENCE_CUTOFF:
            verdict: str = "buy"
            print(f"  [Decision] bullish & confidence {confidence:.4f} > {_VERDICT_CONFIDENCE_CUTOFF} → buy")
        elif direction == "bearish" and confidence > _VERDICT_CONFIDENCE_CUTOFF:
            verdict = "sell"
            print(f"  [Decision] bearish & confidence {confidence:.4f} > {_VERDICT_CONFIDENCE_CUTOFF} → sell")
        else:
            verdict = "hold"
            if direction == "neutral":
                print(f"  [Decision] direction=neutral → hold")
            else:
                print(f"  [Decision] confidence {confidence:.4f} ≤ {_VERDICT_CONFIDENCE_CUTOFF} → hold (방향은 {direction} 이나 신뢰도 부족)")

        # 6. reasons / risk_factors
        print("\n  [Decision] 단계 6: reasons / risk_factors 수집")
        reasons = self._build_reasons(news_signal, youtube_signal)
        risk_factors = self._build_risk_factors(news_signal, youtube_signal, direction)
        print(f"  [Decision]   positive reasons : {len(reasons.positive)}건")
        print(f"  [Decision]   negative reasons : {len(reasons.negative)}건")
        print(f"  [Decision]   risk_factors     : {len(risk_factors)}건")

        # 7. rationale — LLM (판단에 영향 없음)
        print("\n  [Decision] 단계 7: rationale LLM 생성")
        rationale = self._generate_rationale(
            direction, confidence, verdict,
            reasons, risk_factors, company, intent,
        )
        print(f"  [Decision]   rationale 길이: {len(rationale)}자")

        print("  " + "━" * 58)

        return InvestmentDecision(
            direction=direction,  # type: ignore[arg-type]
            confidence=confidence,
            verdict=verdict,  # type: ignore[arg-type]
            reasons=reasons,
            risk_factors=risk_factors,
            rationale=rationale,
        )

    @staticmethod
    def _print_input_summary(
        yt: Optional[YoutubeSentimentSignal],
        news: Optional[NewsEventSignal],
    ) -> None:
        print("  [Decision] 입력 신호 요약:")
        if news:
            print(f"  [Decision]   NewsEventSignal  : +{len(news.positive_events)}건 / -{len(news.negative_events)}건, keywords={len(news.keywords)}")
        else:
            print(f"  [Decision]   NewsEventSignal  : 없음")
        if yt:
            dist = yt.sentiment_distribution
            print(f"  [Decision]   YoutubeSignal    : volume={yt.volume}, score={yt.sentiment_score:+.3f}, 분포(+{dist.positive:.1%}/={dist.neutral:.1%}/-{dist.negative:.1%})")
        else:
            print(f"  [Decision]   YoutubeSignal    : 없음")

    # ------------------------------------------------------------------
    # Rule helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _check_sufficiency(
        yt: Optional[YoutubeSentimentSignal],
        news: Optional[NewsEventSignal],
    ) -> Tuple[bool, str]:
        """(insufficient, reason) 반환."""
        if news is None:
            return True, "NewsEventSignal 자체가 없음"
        news_events = len(news.positive_events) + len(news.negative_events)
        if news_events == 0:
            return True, f"뉴스 이벤트 0건 (positive={len(news.positive_events)}, negative={len(news.negative_events)})"
        return False, ""

    @staticmethod
    def _compute_news_score(news: NewsEventSignal, verbose: bool = False) -> float:
        pos_total = 0.0
        for e in news.positive_events:
            w = _IMPACT_WEIGHT.get(e.impact, 0.0)
            pos_total += w
            if verbose:
                print(f"  [Decision]   + [{e.impact:^6s}] (+{w:.1f}) {e.event[:60]}")
        neg_total = 0.0
        for e in news.negative_events:
            w = _IMPACT_WEIGHT.get(e.impact, 0.0)
            neg_total += w
            if verbose:
                print(f"  [Decision]   - [{e.impact:^6s}] (-{w:.1f}) {e.event[:60]}")
        if verbose:
            print(f"  [Decision]   ── pos 합: +{pos_total:.1f}  /  neg 합: -{neg_total:.1f}")
        return pos_total - neg_total

    @staticmethod
    def _build_reasons(
        news: NewsEventSignal,
        yt: Optional[YoutubeSentimentSignal],
    ) -> DecisionReasons:
        positive = [f"[뉴스·{e.impact}] {e.event}" for e in news.positive_events]
        negative = [f"[뉴스·{e.impact}] {e.event}" for e in news.negative_events]

        if yt and yt.bullish_keywords:
            positive.append(
                f"[유튜브] 긍정 댓글 키워드: {', '.join(yt.bullish_keywords[:5])}"
            )
        if yt and yt.bearish_keywords:
            negative.append(
                f"[유튜브] 부정 댓글 키워드: {', '.join(yt.bearish_keywords[:5])}"
            )
        return DecisionReasons(positive=positive, negative=negative)

    @staticmethod
    def _build_risk_factors(
        news: NewsEventSignal,
        yt: Optional[YoutubeSentimentSignal],
        direction: str,
    ) -> list:
        risks: list = []

        # 고위험 부정 이벤트
        high_negatives = [e for e in news.negative_events if e.impact == "high"]
        if high_negatives:
            risks.append(
                f"고위험(high impact) 부정 이벤트 {len(high_negatives)}건 존재"
            )

        # 댓글 감성 역행
        if yt and yt.volume >= _MIN_COMMENT_VOLUME:
            if direction == "bullish" and yt.sentiment_distribution.negative > 0.4:
                risks.append(
                    f"뉴스는 긍정이나 유튜브 댓글 부정 비율 {yt.sentiment_distribution.negative:.1%}"
                )
            if direction == "bearish" and yt.sentiment_distribution.positive > 0.4:
                risks.append(
                    f"뉴스는 부정이나 유튜브 댓글 긍정 비율 {yt.sentiment_distribution.positive:.1%}"
                )

        # 낮은 신호 강도 (양쪽 모두 미미)
        if direction == "neutral":
            risks.append("방향성 신호가 약해 판단이 보수적")

        return risks

    @staticmethod
    def _insufficient_decision(company: Optional[str], intent: Optional[str]) -> InvestmentDecision:
        return InvestmentDecision(
            direction="neutral",
            confidence=_FALLBACK_CONFIDENCE,
            verdict="hold",
            reasons=DecisionReasons(positive=[], negative=[]),
            risk_factors=["수집된 신호가 충분하지 않음 (보수적 hold)"],
            rationale=(
                f"{company or '해당 종목'} 에 대한 뉴스/댓글 신호가 부족하여 "
                "의미 있는 방향성을 판단하기 어렵습니다. 보수적으로 보유(hold) 의견을 유지합니다."
            ),
        )

    # ------------------------------------------------------------------
    # LLM rationale (판단에 영향 없음, 설명만)
    # ------------------------------------------------------------------
    def _generate_rationale(
        self,
        direction: str,
        confidence: float,
        verdict: str,
        reasons: DecisionReasons,
        risk_factors: list,
        company: Optional[str],
        intent: Optional[str],
    ) -> str:
        payload = {
            "company": company,
            "intent": intent,
            "direction": direction,
            "confidence": round(confidence, 4),
            "verdict": verdict,
            "reasons": {"positive": reasons.positive, "negative": reasons.negative},
            "risk_factors": risk_factors,
        }
        user_prompt = (
            "아래 투자 판단 결과를 2~4문장으로 자연스럽게 설명하세요.\n\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)
        )
        print(f"  [Decision]   LLM 요청 payload: direction={direction}, verdict={verdict}, confidence={confidence:.4f}")
        try:
            response = get_chat_llm().invoke(
                [
                    SystemMessage(content=_RATIONALE_SYSTEM_PROMPT),
                    HumanMessage(content=user_prompt),
                ]
            )
            text = response.content if isinstance(response.content, str) else str(response.content)
            result = text.strip()
            print(f"  [Decision]   LLM 응답 (앞 200자): {result[:200]}")
            return result
        except Exception as exc:
            print(f"  [Decision]   ❌ rationale LLM 실패, fallback 문장 사용: {exc}")
            logger.error("Rationale LLM 실패: %s", exc, exc_info=True)
            return self._fallback_rationale(direction, confidence, verdict, company)

    @staticmethod
    def _fallback_rationale(direction: str, confidence: float, verdict: str, company: Optional[str]) -> str:
        return (
            f"{company or '해당 종목'} 에 대한 수집 신호를 종합한 결과 방향성은 "
            f"'{direction}', 신뢰도는 {confidence:.2f}, 최종 의견은 '{verdict}' 입니다."
        )
