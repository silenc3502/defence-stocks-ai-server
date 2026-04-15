"""LLM 배치 기반 감성 분류기.

50~250 개 댓글을 배치(50씩) + 스레드 병렬(4)로 처리하여 10초 이내 목표.
실패한 배치는 해당 범위를 "neutral" 로 fallback 한다 (부분 실패 허용).
"""
import concurrent.futures
import json
import logging
from typing import List, Literal

from langchain_core.messages import HumanMessage, SystemMessage

from app.infrastructure.agent.llm import get_chat_llm

logger = logging.getLogger(__name__)

SentimentLabel = Literal["positive", "neutral", "negative"]

_BATCH_SIZE = 50
_MAX_WORKERS = 4
_SYSTEM_PROMPT = (
    "당신은 투자 관련 유튜브 댓글을 분석하는 감성 분류기입니다. "
    "각 댓글을 'positive', 'neutral', 'negative' 중 하나로 분류하세요.\n"
    "기준:\n"
    "- positive: 매수·상승·호재·기대감·긍정적 전망 등\n"
    "- negative: 매도·하락·악재·실망·부정적 전망·비판 등\n"
    "- neutral: 정보 전달·질문·판단 어려움·관련성 낮음 등\n"
    "응답은 JSON 배열 형식의 분류 라벨만 출력하세요. 다른 텍스트는 절대 포함하지 마세요.\n"
    "예시: [\"positive\", \"neutral\", \"negative\", ...]"
)


class SentimentAnalyzer:
    def __init__(self, batch_size: int = _BATCH_SIZE, max_workers: int = _MAX_WORKERS):
        self.batch_size = batch_size
        self.max_workers = max_workers

    def classify(self, comments: List[str]) -> List[SentimentLabel]:
        """댓글 리스트를 동일 길이의 라벨 리스트로 분류."""
        if not comments:
            return []

        # 배치로 분할
        batches: List[List[str]] = [
            comments[i:i + self.batch_size]
            for i in range(0, len(comments), self.batch_size)
        ]
        print(f"  [Sentiment] 댓글 {len(comments)}건을 {len(batches)}개 배치로 분류 시작 (batch_size={self.batch_size}, workers={self.max_workers})")

        results: List[List[SentimentLabel]] = [[] for _ in batches]

        def process(idx: int) -> None:
            batch = batches[idx]
            try:
                results[idx] = self._classify_batch(batch)
            except Exception as exc:
                print(f"  [Sentiment] 배치 {idx} 실패, neutral 로 fallback: {exc}")
                logger.warning("감성 분류 배치 %d 실패: %s", idx, exc)
                results[idx] = ["neutral"] * len(batch)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(self.max_workers, len(batches)),
            thread_name_prefix="sentiment",
        ) as executor:
            list(executor.map(process, range(len(batches))))

        labels: List[SentimentLabel] = [label for batch_labels in results for label in batch_labels]
        print(f"  [Sentiment] 분류 완료: {len(labels)}건")
        return labels

    def _classify_batch(self, batch: List[str]) -> List[SentimentLabel]:
        numbered = "\n".join(f"{i + 1}. {c[:500]}" for i, c in enumerate(batch))
        user_prompt = f"다음 댓글을 순서대로 분류하세요 (총 {len(batch)}건):\n{numbered}"

        response = get_chat_llm().invoke(
            [
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]
        )
        text = response.content if isinstance(response.content, str) else str(response.content)
        parsed = self._parse_labels(text)

        # 길이 보정 — LLM 이 N 개를 보장하지 않을 수 있음
        if len(parsed) < len(batch):
            parsed = parsed + ["neutral"] * (len(batch) - len(parsed))
        elif len(parsed) > len(batch):
            parsed = parsed[:len(batch)]

        # 값 검증
        valid = {"positive", "neutral", "negative"}
        return [p if p in valid else "neutral" for p in parsed]

    @staticmethod
    def _parse_labels(raw: str) -> List[str]:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0]
        text = text.strip()
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            raise ValueError(f"배열이 아님: {type(parsed)}")
        return [str(p).strip().lower() for p in parsed]
