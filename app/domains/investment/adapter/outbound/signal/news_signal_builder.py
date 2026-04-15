"""뉴스 본문 리스트 → NewsEventSignal 변환기.

LLM 에게 긍정·부정 이벤트 + 영향도(high/medium/low) + 핵심 키워드 추출을 요청한다.
"""
import json
import logging
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from app.domains.investment.application.response.news_event_signal import (
    NewsEvent,
    NewsEventSignal,
)
from app.infrastructure.agent.llm import get_chat_llm

logger = logging.getLogger(__name__)

_MAX_CONTENT_CHARS = 800

_SYSTEM_PROMPT = (
    "당신은 투자 뉴스 분석가입니다. 제공된 뉴스들을 분석하여 투자 판단에 "
    "영향을 줄 이벤트를 추출하세요.\n"
    "각 이벤트는 긍정(positive_events) 또는 부정(negative_events) 으로 분류하고, "
    "impact 는 high/medium/low 중 하나로 평가하세요.\n"
    "응답은 반드시 아래 JSON 형식으로만 출력하세요 (다른 텍스트 금지):\n"
    "{\n"
    '  "positive_events": [{"event": "...", "impact": "high|medium|low"}],\n'
    '  "negative_events": [{"event": "...", "impact": "high|medium|low"}],\n'
    '  "keywords": ["...", "..."]\n'
    "}"
)


class NewsSignalBuilder:
    def build(self, news_items: List[Dict[str, Any]]) -> NewsEventSignal:
        """
        :param news_items: [{title, content, source, link, published_at}, ...]
        """
        if not news_items:
            print(f"  [Signal][뉴스] 입력 뉴스 0건 → 빈 신호 반환")
            return self._empty()

        print(f"  [Signal][뉴스] 분석 시작 (뉴스 {len(news_items)}건)")

        blocks = []
        for i, n in enumerate(news_items):
            content = (n.get("content") or "")[:_MAX_CONTENT_CHARS]
            blocks.append(
                f"#{i + 1} 제목: {n.get('title', '')}\n본문: {content}"
            )
        user_prompt = "\n\n".join(blocks)

        try:
            response = get_chat_llm().invoke(
                [
                    SystemMessage(content=_SYSTEM_PROMPT),
                    HumanMessage(content=user_prompt),
                ]
            )
            raw = response.content if isinstance(response.content, str) else str(response.content)
            parsed = self._parse_json(raw)
        except Exception as exc:
            print(f"  [Signal][뉴스] ❌ LLM 호출/파싱 실패: {exc}")
            logger.error("NewsSignalBuilder 실패: %s", exc, exc_info=True)
            return self._empty()

        positive = self._to_events(parsed.get("positive_events", []))
        negative = self._to_events(parsed.get("negative_events", []))
        keywords = [str(k).strip() for k in parsed.get("keywords", []) if k]

        print(f"  [Signal][뉴스] 추출 완료: 긍정 {len(positive)} / 부정 {len(negative)} / 키워드 {len(keywords)}")
        for e in positive[:3]:
            print(f"    + [{e.impact}] {e.event[:80]}")
        for e in negative[:3]:
            print(f"    - [{e.impact}] {e.event[:80]}")

        return NewsEventSignal(
            positive_events=positive,
            negative_events=negative,
            keywords=keywords,
        )

    @staticmethod
    def _parse_json(raw: str) -> dict:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0]
        return json.loads(text.strip())

    @staticmethod
    def _to_events(items: list) -> List[NewsEvent]:
        valid_impacts = {"high", "medium", "low"}
        events: List[NewsEvent] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            event_text = str(item.get("event", "")).strip()
            impact = str(item.get("impact", "medium")).strip().lower()
            if not event_text:
                continue
            if impact not in valid_impacts:
                impact = "medium"
            events.append(NewsEvent(event=event_text, impact=impact))  # type: ignore[arg-type]
        return events

    @staticmethod
    def _empty() -> NewsEventSignal:
        return NewsEventSignal(positive_events=[], negative_events=[], keywords=[])
