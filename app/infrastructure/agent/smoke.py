"""LangGraph 멀티 에이전트 그래프 가용성 검증 스모크 실행.

직접 실행:
    python -m app.infrastructure.agent.smoke
    python -m app.infrastructure.agent.smoke "방산주 전망 알려줘"
"""
import logging
import sys

from app.infrastructure.agent.graph import run_agent_workflow


def main(user_input: str = "안녕") -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    result = run_agent_workflow(user_input)

    print("\n===== Plan =====")
    print(result.get("plan"))
    print("\n===== Research =====")
    print(result.get("research"))
    print("\n===== Analysis =====")
    print(result.get("analysis"))
    print(
        f"\n===== Review ===== ({result.get('review')}, iter={result.get('iteration')})"
    )
    print("\n===== Final Output =====")
    print(result.get("final_output"))


if __name__ == "__main__":
    arg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "안녕"
    main(arg)
