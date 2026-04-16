"""Synthesis — 투자 판단을 사용자 친화적 자연어 응답으로 종합.

규칙:
- investment_decision 의 direction/confidence/verdict 는 절대 변경·재계산하지 않는다.
- 답변 근거는 investment_decision.reasons 에만 기반하며, 새로운 근거 생성 금지.
- verdict 는 반드시 직접적 표현 (매수/보유/매도) 으로 사용자에게 전달.
- investment_decision 이 없으면 analysis_result 로 fallback (참고용 명시).
"""
import json
from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage

from app.domains.investment.adapter.outbound.agent.llm_invoker import invoke_llm
from app.domains.investment.adapter.outbound.agent.state import InvestmentState
from app.domains.investment.application.response.investment_decision import (
    InvestmentDecision,
)

# verdict → 한국어 직접 표현
_VERDICT_LABEL = {
    "buy": "매수",
    "hold": "보유",
    "sell": "매도",
}

# confidence 해석 기준
_CONF_HIGH = 0.7
_CONF_MID = 0.4
_LOW_HOLD_THRESHOLD = 0.3

_DISCLAIMER = (
    "\n\n---\n"
    "⚠️ 본 응답은 투자 권유가 아닌 정보 제공 목적이며, "
    "투자 판단의 책임은 전적으로 투자자 본인에게 있습니다."
)


def synthesis_node(state: InvestmentState) -> Dict[str, Any]:
    parsed = state.get("parsed_query") or {}
    decision_payload: Optional[dict] = state.get("investment_decision")
    analysis_result = state.get("analysis_result") or ""
    retrieval_data = state.get("retrieval_data") or ""

    print("\n" + "=" * 60)
    print(f"[Synthesis] 시작")
    print("=" * 60)

    # 단계 1: 입력 State 스냅샷
    print("\n[Synthesis] 단계 1: 입력 State 확인")
    print(f"  - input               : {state.get('input', '')[:80]}")
    print(f"  - parsed_query.company: {parsed.get('company')!r}")
    print(f"  - parsed_query.intent : {parsed.get('intent')!r}")
    print(f"  - investment_decision : {'있음' if decision_payload else '❌ 없음'}")
    print(f"  - analysis_result 길이: {len(analysis_result)}자 (fallback 시 사용)")
    print(f"  - retrieval_data 길이 : {len(retrieval_data)}자 (보조 참고용, 근거에는 미사용)")

    # 단계 2: 경로 선택
    print("\n[Synthesis] 단계 2: 합성 경로 결정")
    if decision_payload:
        print(f"  → investment_decision 기반 경로 (정상 경로)")
        decision = InvestmentDecision(**decision_payload)
        body = _synthesize_from_decision(decision, parsed)
    else:
        print(f"  → analysis_result fallback 경로 (⚠ investment_decision 누락)")
        print(f"  → 출력에 '참고용 분석 결과' 명시 예정")
        body = _synthesize_fallback(analysis_result, parsed)

    # 단계 6: 면책 문구 부착
    print("\n[Synthesis] 단계 6: 면책 문구 부착")
    print(f"  - body 길이 (부착 전) : {len(body)}자")
    final = body + _DISCLAIMER
    print(f"  - final 길이 (부착 후): {len(final)}자 (+{len(_DISCLAIMER)}자)")

    # 단계 7: 최종 pretty-print
    print("\n[Synthesis] 단계 7: 최종 응답 pretty-print")
    _print_synthesis(final, decision_payload)

    print(f"[Synthesis] 완료 → next_agent='done', final_output 적재")
    print("=" * 60)

    return {
        "final_output": final,
        "next_agent": "done",
        "messages": [AIMessage(content=final, name="Synthesis")],
    }


# ------------------------------------------------------------------
# Primary path — investment_decision 기반
# ------------------------------------------------------------------
def _synthesize_from_decision(decision: InvestmentDecision, parsed: dict) -> str:
    # 단계 3: verdict / confidence 해석
    print("\n[Synthesis] 단계 3: verdict / confidence 해석")
    verdict_ko = _VERDICT_LABEL.get(decision.verdict, decision.verdict)
    confidence_level = _confidence_level(decision.confidence)
    is_low_hold = (decision.verdict == "hold" and decision.confidence <= _LOW_HOLD_THRESHOLD)
    company = parsed.get("company") or "해당 종목"

    print(f"  - verdict={decision.verdict!r} → 한국어 표현: {verdict_ko!r}")
    print(f"  - confidence={decision.confidence:.4f} → 레이블: {confidence_level!r}")
    print(f"    규칙: ≥{_CONF_HIGH}=높은 확신 / ≥{_CONF_MID}=일정 수준 / 나머지=불확실성 높음")
    print(f"  - direction={decision.direction!r} (변경 없이 그대로 사용)")
    print(f"  - low_hold (hold + confidence ≤ {_LOW_HOLD_THRESHOLD}): {is_low_hold}")
    if is_low_hold:
        print(f"    → 프롬프트에 '신호 부족 보수적 판단' 명시 지시 추가")

    # 단계 4: 근거 / 리스크 수집 (reasons 기반)
    print("\n[Synthesis] 단계 4: LLM 에게 전달할 근거 수집 (reasons 기반)")
    print(f"  - reasons.positive ({len(decision.reasons.positive)}건):")
    for r in decision.reasons.positive:
        print(f"      + {r[:80]}")
    print(f"  - reasons.negative ({len(decision.reasons.negative)}건):")
    for r in decision.reasons.negative:
        print(f"      - {r[:80]}")
    print(f"  - risk_factors ({len(decision.risk_factors)}건):")
    for r in decision.risk_factors:
        print(f"      ! {r[:80]}")
    print(f"  ※ reasons 외의 새로운 근거 생성은 프롬프트에서 금지됨")

    system_prompt = (
        "당신은 투자 판단을 사용자 친화적 한국어 답변으로 종합하는 에이전트입니다.\n\n"
        "엄격한 규칙:\n"
        "1. verdict 는 반드시 '매수', '보유', '매도' 중 하나로 직접적이고 명확하게 표현하라. "
        "완곡한 표현(예: '적절해 보입니다', '고민해볼 만합니다')으로 의미를 흐리지 말라.\n"
        "2. reasons.positive / reasons.negative / risk_factors 에 명시된 항목 외에 "
        "새로운 근거를 임의로 만들거나 추측하지 말라.\n"
        "3. verdict, direction, confidence 는 수정·재계산·재해석하지 말고 주어진 값을 그대로 사용하라.\n"
        "4. 응답 구조: 결론 한 줄 → 근거 요약 → 리스크 → 마무리 문장. 2~4개 문단으로 작성.\n"
        "5. 면책 문구는 본문에 포함하지 말라 (시스템이 자동 부착).\n"
    )

    low_hold_note = ""
    if is_low_hold:
        low_hold_note = (
            "\n※ 중요: 이 판단은 수집된 신호가 충분하지 않아 보수적으로 내려진 '보유' 의견이다. "
            "첫 문단에서 '현재 수집된 신호가 부족하여 보수적으로 보유 의견을 제시' 라는 취지를 반드시 포함하라."
        )

    user_payload = {
        "company": company,
        "intent": parsed.get("intent"),
        "verdict_ko": verdict_ko,
        "verdict_raw": decision.verdict,
        "direction": decision.direction,
        "confidence": round(decision.confidence, 3),
        "confidence_level_ko": confidence_level,
        "reasons": {
            "positive": decision.reasons.positive,
            "negative": decision.reasons.negative,
        },
        "risk_factors": decision.risk_factors,
        "rationale": decision.rationale,
    }

    user_prompt = (
        f"아래 투자 판단 결과를 기반으로 한국어 답변을 작성하세요.\n\n"
        f"{json.dumps(user_payload, ensure_ascii=False, indent=2)}\n\n"
        f"작성 지침:\n"
        f"- 첫 문단: '{company}' 에 대해 '{verdict_ko}' 의견이며 확신도는 '{confidence_level}' "
        f"({decision.confidence:.1%}) 수준이라고 직접적으로 명시.{low_hold_note}\n"
        f"- 두번째 문단: reasons.positive / reasons.negative 를 바탕으로 핵심 근거 요약. "
        f"목록에 있는 내용만 사용.\n"
        f"- (risk_factors 가 있을 때) 세번째 문단: 리스크 강조.\n"
        f"- 마무리: 간결한 맺음말 (면책 문구 절대 포함 금지).\n"
    )

    # 단계 5: LLM 호출
    print("\n[Synthesis] 단계 5: LLM 호출로 자연어 답변 합성")
    print(f"  - system_prompt 길이: {len(system_prompt)}자 (엄격한 규칙 5개)")
    print(f"  - user_prompt 길이  : {len(user_prompt)}자")
    print(f"  - low_hold 지시 포함 : {'예' if low_hold_note else '아니오'}")

    body = invoke_llm("Synthesis", system_prompt, user_prompt)
    print(f"\n[Synthesis] 단계 5 완료 — 합성 본문 수신 ({len(body)}자)")
    return body


# ------------------------------------------------------------------
# Fallback path — investment_decision 누락 시
# ------------------------------------------------------------------
def _synthesize_fallback(analysis_result: str, parsed: dict) -> str:
    company = parsed.get("company") or "해당 종목"

    print("\n[Synthesis] 단계 3 (fallback): analysis_result 상태 검증")
    print(f"  - company               : {company!r}")
    print(f"  - analysis_result 길이  : {len(analysis_result)}자")
    print(f"  - analysis_result 비어있음: {not analysis_result.strip()}")

    if not analysis_result.strip():
        print(f"  → 둘 다 없음 → 재시도 안내 메시지 생성")
        return (
            f"⚠️ 참고용 분석 결과\n\n"
            f"현재 {company} 에 대한 정량 투자 판단과 보조 분석이 모두 확보되지 않았습니다. "
            f"신호 수집을 재시도하거나 더 구체적인 질문으로 다시 시도해 주세요."
        )

    print("\n[Synthesis] 단계 4 (fallback): '참고용' prefix 를 analysis_result 앞에 부착")
    prefix = (
        f"⚠️ 참고용 분석 결과 — 정량 투자 판단 미산출\n"
        f"({company} 에 대한 구조화된 투자 판단(verdict/direction/confidence)이 산출되지 않아, "
        f"LLM 기반 보조 분석 결과를 그대로 제공합니다.)\n\n"
    )
    body = prefix + analysis_result
    print(f"  - prefix 길이: {len(prefix)}자")
    print(f"  - body 길이  : {len(body)}자 (fallback 은 LLM 호출 없이 직접 구성)")
    return body


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _confidence_level(confidence: float) -> str:
    """confidence → 한국어 해석 레이블."""
    if confidence >= _CONF_HIGH:
        return "높은 확신"
    if confidence >= _CONF_MID:
        return "일정 수준의 가능성"
    return "불확실성이 높은 상태"


def _print_synthesis(final: str, decision_payload: Optional[dict]) -> None:
    print()
    print("┌" + "─" * 60 + "┐")
    print("│ [Synthesis] 최종 응답 생성 결과")
    print("├" + "─" * 60 + "┤")
    if decision_payload:
        verdict = decision_payload.get("verdict")
        verdict_ko = _VERDICT_LABEL.get(verdict, verdict)
        confidence = decision_payload.get("confidence", 0.0)
        direction = decision_payload.get("direction")
        level = _confidence_level(confidence)
        print(f"│ verdict       : {verdict} ({verdict_ko})")
        print(f"│ direction     : {direction}")
        print(f"│ confidence    : {confidence:.4f} ({confidence:.1%}) → {level}")
        print(f"│ 경로           : investment_decision 기반")
    else:
        print(f"│ 경로           : analysis_result fallback (참고용)")
    print(f"│ 전체 길이       : {len(final)}자")
    print("├" + "─" * 60 + "┤")
    print(f"│ 본문 미리보기 (앞 500자):")
    for line in final[:500].splitlines():
        print(f"│   {line}")
    print("└" + "─" * 60 + "┘")
    print()
