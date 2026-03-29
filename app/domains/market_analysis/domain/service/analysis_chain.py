from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.infrastructure.config.settings import settings

SYSTEM_TEMPLATE = """당신은 한국 방산주 투자 분석 전문 AI입니다.

아래 제공된 데이터를 기반으로 사용자의 질문에 답변하세요.
- 제공된 데이터 범위 내에서만 답변하세요.
- 방산/국방/군사/무기/안보와 관련 없는 질문에는 "방산 도메인과 관련 없는 질문입니다. 방산주, 국방, 군사 관련 질문을 해주세요."라고 답변하세요.
- 투자 권유가 아닌 정보 제공 목적임을 명시하세요.
- 한국어로 답변하세요.

=== 현재 트렌드 키워드 (댓글 분석 결과) ===
{keywords}

=== 사전 등록된 방산 종목 목록 ===
{stocks}

=== 추천 종목 (키워드 매칭 결과) ===
{recommendations}
"""

HUMAN_TEMPLATE = "{question}"


def create_analysis_chain():
    llm = ChatOpenAI(
        model="gpt-5-mini",
        api_key=settings.openai_api_key,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_TEMPLATE),
        ("human", HUMAN_TEMPLATE),
    ])

    chain = prompt | llm

    return chain
