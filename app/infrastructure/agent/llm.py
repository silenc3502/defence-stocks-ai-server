from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.infrastructure.config.settings import settings

# 기존 OpenAIClient 와 동일한 기본 모델 사용
_DEFAULT_MODEL = "gpt-5-mini"


@lru_cache(maxsize=4)
def get_chat_llm(
    model: str = _DEFAULT_MODEL,
    temperature: float = 0.2,
) -> ChatOpenAI:
    """ChatOpenAI 인스턴스를 캐싱하여 재사용한다.

    노드별로 매번 새로 생성할 필요가 없고, 같은 (model, temperature)
    조합에 대해 단일 인스턴스를 공유한다.
    """
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=model,
        temperature=temperature,
    )
