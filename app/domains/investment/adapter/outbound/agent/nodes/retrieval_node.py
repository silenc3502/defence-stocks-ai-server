"""Retrieval — required_data 기반 데이터 소스 병렬 호출.

설계:
- SOURCE_REGISTRY 에 등록된 핸들러를 ThreadPoolExecutor 로 동시에 호출한다.
- 핸들러 인터페이스(`Callable[[Optional[str]], str]`) 는 변경하지 않는다 — 새 소스를
  추가할 때 추가 작업 불필요.
- 각 핸들러는 외부 API + DB 를 호출하는 I/O bound 작업이라 GIL 영향 없이 병렬화 효과를 얻는다.
- 핸들러별 로그는 `[Retrieval][<소스명>]` prefix 로 식별 가능하게 출력된다.
- 전체 wait 에 타임아웃을 적용 — 초과 핸들러는 timeout 으로 표시, 나머지는 정상 반영.
- 결과는 `required_data` 입력 순서대로 합쳐진다 (실행 완료 순서 무관).
"""
import concurrent.futures
import logging
import threading
import time
from typing import Any, Dict, Optional, Tuple

from langchain_core.messages import AIMessage

from app.domains.investment.adapter.outbound.agent.state import InvestmentState
from app.domains.investment.adapter.outbound.data_source.source_registry import (
    SOURCE_REGISTRY,
)

logger = logging.getLogger(__name__)

_HANDLER_TIMEOUT_SECONDS = 30.0


def retrieval_node(state: InvestmentState) -> Dict[str, Any]:
    parsed = state.get("parsed_query") or {}
    required_data = parsed.get("required_data", [])
    # company 가 없으면 None 을 그대로 handler 에 전달 → handler 자체 fallback
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
    results: Dict[str, Tuple[str, str, float]] = {}  # key → (status, text, elapsed)

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(valid_keys),
        thread_name_prefix="retrieval",
    ) as executor:
        future_to_key = {
            executor.submit(_invoke_handler, key, keyword): key
            for key in valid_keys
        }

        # 전체 wait 에 타임아웃 적용 — 모든 핸들러가 동시 시작이므로
        # 가장 느린 핸들러 기준으로 timeout 작용
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
                    _HANDLER_TIMEOUT_SECONDS,
                )
                print(f"[Retrieval][{key}] ⏱ 타임아웃 ({_HANDLER_TIMEOUT_SECONDS:.0f}s)")
            else:
                try:
                    results[key] = future.result()
                except Exception as exc:
                    results[key] = ("failed", f"[{key}] (수집 실패: {exc})", 0.0)
                    print(f"[Retrieval][{key}] ❌ 결과 수신 중 예외: {exc}")

    overall_elapsed = time.monotonic() - overall_start

    # required_data 입력 순서대로 결과 모음 (실행 완료 순서 무관)
    sections: list[str] = []
    for key in required_data:
        if key in invalid_keys:
            sections.append(f"[{key}] (미구현 — 향후 확장 예정)")
        elif key in results:
            sections.append(results[key][1])

    data = "\n\n".join(sections) if sections else "(수집된 데이터 없음)"

    # 타이밍 / 효과 측정 로그
    elapsed_per_source = {k: r[2] for k, r in results.items()}
    sequential_estimate = sum(elapsed_per_source.values())
    saved = max(0.0, sequential_estimate - overall_elapsed)
    speedup = (sequential_estimate / overall_elapsed) if overall_elapsed > 0 else 0.0

    print(f"\n[Retrieval] 병렬 실행 완료")
    print(f"[Retrieval] 전체 소요: {overall_elapsed:.2f}s")
    print(f"[Retrieval] 핸들러별 소요:")
    for key, elapsed in elapsed_per_source.items():
        status = results[key][0]
        print(f"  [Retrieval][{key}] {status} — {elapsed:.2f}s")
    print(f"[Retrieval] 순차 실행 시 예상: {sequential_estimate:.2f}s")
    print(f"[Retrieval] 절약: {saved:.2f}s (speedup x{speedup:.2f})")
    print(f"[Retrieval] 최종 retrieval_data 길이: {len(data)}자")
    print("=" * 60)

    return {
        "retrieval_data": data,
        "messages": [AIMessage(content=data, name="Retrieval")],
    }


# ------------------------------------------------------------------
# 병렬 실행용 wrapper
# ------------------------------------------------------------------
def _invoke_handler(key: str, keyword: Optional[str]) -> Tuple[str, str, float]:
    """단일 핸들러를 호출하고 (status, text, elapsed) 를 반환.

    예외는 캡처하여 failure 로 변환 — 한 핸들러 실패가 다른 핸들러를 막지 않음.
    """
    handler = SOURCE_REGISTRY[key]
    thread_name = threading.current_thread().name
    print(f"[Retrieval][{key}] 호출 시작 (thread={thread_name})")
    start = time.monotonic()
    try:
        text = handler(keyword)
    except Exception as exc:
        elapsed = time.monotonic() - start
        print(f"[Retrieval][{key}] ❌ 실패 ({elapsed:.2f}s): {exc}")
        logger.error("[Retrieval][%s] 호출 실패: %s", key, exc, exc_info=True)
        return ("failed", f"[{key}] (수집 실패: {exc})", elapsed)
    elapsed = time.monotonic() - start
    print(f"[Retrieval][{key}] ✅ 성공 ({elapsed:.2f}s, {len(text)}자)")
    return ("success", text, elapsed)


def _empty_result() -> Dict[str, Any]:
    data = "(수집된 데이터 없음)"
    return {
        "retrieval_data": data,
        "messages": [AIMessage(content=data, name="Retrieval")],
    }
