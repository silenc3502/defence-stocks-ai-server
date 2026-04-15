"""Retrieval — required_data 기반 데이터 소스 병렬 호출 + 신호 수집.

각 핸들러는 (text, signal_payload) 튜플을 반환한다.
- text 는 retrieval_data 에 합쳐짐
- signal_payload 는 SIGNAL_STATE_KEY 매핑으로 state 에 적재됨 (Analyzer 소비용)
"""
import concurrent.futures
import logging
import threading
import time
from typing import Any, Dict, Optional, Tuple

from langchain_core.messages import AIMessage

from app.domains.investment.adapter.outbound.agent.state import InvestmentState
from app.domains.investment.adapter.outbound.data_source.source_registry import (
    SIGNAL_STATE_KEY,
    SOURCE_REGISTRY,
)

logger = logging.getLogger(__name__)

_HANDLER_TIMEOUT_SECONDS = 30.0

# (status, text, signal_payload, elapsed)
_HandlerResult = Tuple[str, str, Optional[Dict[str, Any]], float]


def retrieval_node(state: InvestmentState) -> Dict[str, Any]:
    parsed = state.get("parsed_query") or {}
    required_data = parsed.get("required_data", [])
    keyword = parsed.get("company")

    print("\n" + "=" * 60)
    print(f"[Retrieval] 시작 (병렬 실행)")
    print(f"[Retrieval] keyword: {keyword!r}")
    print(f"[Retrieval] required_data: {required_data}")
    print(f"[Retrieval] 핸들러 타임아웃: {_HANDLER_TIMEOUT_SECONDS:.0f}s")
    print("=" * 60)

    if not required_data:
        return _empty_result()

    valid_keys = [k for k in required_data if k in SOURCE_REGISTRY]
    invalid_keys = [k for k in required_data if k not in SOURCE_REGISTRY]

    if invalid_keys:
        print(f"[Retrieval] 미구현 소스 (건너뜀): {invalid_keys}")

    if not valid_keys:
        print(f"[Retrieval] 호출 가능한 소스 없음")
        return _empty_result()

    # 병렬 실행
    overall_start = time.monotonic()
    results: Dict[str, _HandlerResult] = {}

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(valid_keys),
        thread_name_prefix="retrieval",
    ) as executor:
        future_to_key = {
            executor.submit(_invoke_handler, key, keyword): key
            for key in valid_keys
        }
        done, not_done = concurrent.futures.wait(
            future_to_key.keys(),
            timeout=_HANDLER_TIMEOUT_SECONDS,
        )

        for future, key in future_to_key.items():
            if future in not_done:
                future.cancel()
                results[key] = (
                    "timeout",
                    f"[{key}] (타임아웃 — {_HANDLER_TIMEOUT_SECONDS:.0f}s 초과)",
                    None,
                    _HANDLER_TIMEOUT_SECONDS,
                )
                print(f"[Retrieval][{key}] ⏱ 타임아웃 ({_HANDLER_TIMEOUT_SECONDS:.0f}s)")
            else:
                try:
                    results[key] = future.result()
                except Exception as exc:
                    results[key] = ("failed", f"[{key}] (수집 실패: {exc})", None, 0.0)
                    print(f"[Retrieval][{key}] ❌ 결과 수신 중 예외: {exc}")

    overall_elapsed = time.monotonic() - overall_start

    # 텍스트 합치기 — required_data 입력 순서 유지
    sections: list[str] = []
    for key in required_data:
        if key in invalid_keys:
            sections.append(f"[{key}] (미구현 — 향후 확장 예정)")
        elif key in results:
            sections.append(results[key][1])

    data = "\n\n".join(sections) if sections else "(수집된 데이터 없음)"

    # 신호 payload 를 State 에 매핑
    state_updates: Dict[str, Any] = {
        "retrieval_data": data,
        "messages": [AIMessage(content=data, name="Retrieval")],
    }
    for key, (_status, _text, signal, _elapsed) in results.items():
        state_field = SIGNAL_STATE_KEY.get(key)
        if state_field and signal:
            state_updates[state_field] = signal
            print(f"[Retrieval][{key}] signal → state.{state_field} 저장")

    # 타이밍 로그
    elapsed_per_source = {k: r[3] for k, r in results.items()}
    sequential_estimate = sum(elapsed_per_source.values())
    saved = max(0.0, sequential_estimate - overall_elapsed)
    speedup = (sequential_estimate / overall_elapsed) if overall_elapsed > 0 else 0.0

    print(f"\n[Retrieval] 병렬 실행 완료")
    print(f"[Retrieval] 전체 소요: {overall_elapsed:.2f}s")
    print(f"[Retrieval] 핸들러별 소요:")
    for key, elapsed in elapsed_per_source.items():
        status = results[key][0]
        has_signal = "signal ✓" if results[key][2] else "signal ✗"
        print(f"  [Retrieval][{key}] {status} — {elapsed:.2f}s ({has_signal})")
    print(f"[Retrieval] 순차 실행 시 예상: {sequential_estimate:.2f}s")
    print(f"[Retrieval] 절약: {saved:.2f}s (speedup x{speedup:.2f})")
    print(f"[Retrieval] 최종 retrieval_data 길이: {len(data)}자")
    print("=" * 60)

    return state_updates


def _invoke_handler(key: str, keyword: Optional[str]) -> _HandlerResult:
    """단일 핸들러를 호출하고 (status, text, signal_payload, elapsed) 반환."""
    handler = SOURCE_REGISTRY[key]
    thread_name = threading.current_thread().name
    print(f"[Retrieval][{key}] 호출 시작 (thread={thread_name})")
    start = time.monotonic()
    try:
        result = handler(keyword)
    except Exception as exc:
        elapsed = time.monotonic() - start
        print(f"[Retrieval][{key}] ❌ 실패 ({elapsed:.2f}s): {exc}")
        logger.error("[Retrieval][%s] 호출 실패: %s", key, exc, exc_info=True)
        return ("failed", f"[{key}] (수집 실패: {exc})", None, elapsed)
    elapsed = time.monotonic() - start

    # 핸들러는 (text, signal) 튜플을 반환 — 구버전 호환 방어
    if isinstance(result, tuple) and len(result) == 2:
        text, signal = result
    else:
        text, signal = str(result), None

    print(f"[Retrieval][{key}] ✅ 성공 ({elapsed:.2f}s, {len(text)}자, signal={'있음' if signal else '없음'})")
    return ("success", text, signal, elapsed)


def _empty_result() -> Dict[str, Any]:
    data = "(수집된 데이터 없음)"
    return {
        "retrieval_data": data,
        "messages": [AIMessage(content=data, name="Retrieval")],
    }
