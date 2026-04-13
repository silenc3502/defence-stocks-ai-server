"""투자 질문을 구조화된 쿼리 데이터(company, intent, required_data)로 변환한다.

LLM 에게 JSON 응답을 요청하고 파싱한다.
파싱 실패 시 1회 재시도 후에도 실패하면 QueryParseError 를 발생시킨다.
"""
import json
import logging
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from app.domains.investment.adapter.outbound.agent.state import ParsedQuery
from app.infrastructure.agent.exceptions import AgentInvocationError
from app.infrastructure.agent.llm import get_chat_llm

logger = logging.getLogger(__name__)

_MAX_PARSE_RETRIES = 1

_SYSTEM_PROMPT = """\
당신은 투자 질문 파서입니다.
사용자의 자연어 투자 질문을 분석하여 아래 JSON 형식으로만 응답하세요.
다른 텍스트는 절대 포함하지 마세요.

{
  "company": "종목명 또는 null",
  "intent": "매수_판단 | 리스크_분석 | 전망_조회 | 비교_분석 | 일반_질의",
  "required_data": ["뉴스", "재무", "시장_데이터", "업종_동향"]
}

규칙:
- company: 특정 종목이 언급되면 종목명, 없으면(테마·섹터·일반) null
- intent: 질문 의도에 가장 가까운 것 하나 선택
- required_data: 답변에 필요한 정보 유형을 배열로 나열 (1개 이상)
"""


class QueryParseError(AgentInvocationError):
    """투자 질문 파싱 실패."""


def parse_investment_query(query: str) -> ParsedQuery:
    """사용자 투자 질문을 구조화된 ParsedQuery 로 변환한다.

    :raises QueryParseError: LLM 호출 실패 또는 JSON 파싱 실패 (재시도 포함)
    """
    print("=" * 60)
    print(f"[QueryParser] 입력 질문: {query}")
    print("=" * 60)

    last_error: Optional[Exception] = None

    for attempt in range(_MAX_PARSE_RETRIES + 1):
        try:
            raw_text = _call_llm(query)
            print(f"[QueryParser] LLM 원시 응답 (attempt={attempt + 1}):")
            print(raw_text)
            print("-" * 60)

            parsed = _parse_json(raw_text)
            result = _validate(parsed)

            print(f"[QueryParser] 파싱 결과:")
            print(f"  company       = {result['company']}")
            print(f"  intent        = {result['intent']}")
            print(f"  required_data = {result['required_data']}")
            print("=" * 60)

            return result

        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            last_error = exc
            print(f"[QueryParser] 파싱 실패 (attempt={attempt + 1}): {exc}")
            if attempt < _MAX_PARSE_RETRIES:
                print("[QueryParser] 재시도...")

    raise QueryParseError(f"투자 질문 파싱 실패: {last_error}") from last_error


def _call_llm(query: str) -> str:
    try:
        response = get_chat_llm().invoke(
            [
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(content=query),
            ]
        )
    except Exception as exc:
        raise QueryParseError(f"QueryParser LLM 호출 실패: {exc}") from exc
    return response.content if isinstance(response.content, str) else str(response.content)


def _parse_json(raw: str) -> dict:
    """LLM 응답에서 JSON 블록을 추출하여 파싱한다."""
    text = raw.strip()
    # 마크다운 코드 블록 감싸기 대응
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


def _validate(data: dict) -> ParsedQuery:
    """파싱된 dict 를 ParsedQuery 타입에 맞게 검증·정규화한다."""
    company = data.get("company")
    if company in ("null", "None", "", None):
        company = None

    intent = data.get("intent", "일반_질의")
    if not isinstance(intent, str) or not intent.strip():
        intent = "일반_질의"

    required_data = data.get("required_data", [])
    if not isinstance(required_data, list) or len(required_data) == 0:
        required_data = ["뉴스"]

    return ParsedQuery(
        company=company,
        intent=intent.strip(),
        required_data=[str(d).strip() for d in required_data if d],
    )
