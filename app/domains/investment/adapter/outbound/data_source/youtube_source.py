"""유튜브 데이터 소스 (Investment 전용).

- 검색/댓글/키워드 수집은 메모리에서 수행 (market_video 테이블 오염 방지).
- 수집 완료 후 저장:
    MySQL  → investment_youtube_logs (세션 헤더 + 키워드 TOP N)
          → investment_youtube_videos (영상 메타데이터, id 가 cross-DB 키)
    PG    → investment_youtube_video_comments (영상별 댓글 JSONB, id = MySQL videos.id)
- keyword 가 None 이면 기본 방산 쿼리로 fallback.
"""
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.domains.investment.adapter.outbound.persistence.investment_youtube_log_repository_impl import (
    InvestmentYoutubeLogRepositoryImpl,
)
from app.domains.investment.adapter.outbound.persistence.investment_youtube_video_comment_repository_impl import (
    InvestmentYoutubeVideoCommentRepositoryImpl,
)
from app.domains.investment.adapter.outbound.persistence.investment_youtube_video_repository_impl import (
    InvestmentYoutubeVideoRepositoryImpl,
)
from app.domains.market_video.adapter.outbound.external.market_video_client import (
    MarketVideoClient,
)
from app.domains.market_video.domain.service.noun_extractor import extract_nouns
from app.domains.youtube.adapter.outbound.external.youtube_client import YoutubeClient
from app.infrastructure.database.postgres_session import PostgresSessionLocal
from app.infrastructure.database.session import SessionLocal

logger = logging.getLogger(__name__)

_FALLBACK_QUERY = "한국 방산주 방위산업 주식"
_MAX_VIDEOS = 5
_MAX_COMMENTS_PER_VIDEO = 50
_TOP_NOUNS = 30


def fetch_youtube(keyword: Optional[str] = None) -> str:
    query = keyword or _FALLBACK_QUERY
    if keyword:
        print(f"  [유튜브] 사용자 키워드 사용: {query!r}")
    else:
        print(f"  [유튜브] 키워드 없음 → 기본 쿼리 fallback: {query!r}")

    # 1단계: 영상 검색
    print(f"  [유튜브] 1단계: 영상 검색")
    search_result = YoutubeClient().search_videos(query=query, max_results=_MAX_VIDEOS)
    if not search_result.items:
        print(f"  [유튜브] 검색 결과 없음")
        _save_log_only(keyword, query, [])
        return f"(유튜브 검색 결과 없음 — query={query})"

    videos = search_result.items
    print(f"  [유튜브] 영상 {len(videos)}건 수집")
    for i, v in enumerate(videos):
        print(f"    #{i + 1} {v.channel_name} | {v.title[:60]}")

    # 2단계: 각 영상의 댓글 수집
    print(f"  [유튜브] 2단계: 댓글 수집")
    video_client = MarketVideoClient()
    comments_by_youtube_id: Dict[str, List[Any]] = {}
    all_texts: List[str] = []

    for v in videos:
        try:
            comments = video_client.get_video_comments(
                v.video_id, _MAX_COMMENTS_PER_VIDEO, order="relevance"
            )
        except Exception as exc:
            print(f"  [유튜브] 댓글 수집 실패 ({v.video_id}): {exc}")
            comments = []

        comments_by_youtube_id[v.video_id] = comments
        all_texts.extend(c.text for c in comments)
        print(f"    - {v.title[:50]}: {len(comments)}건")

    # 3단계: 키워드 추출
    print(f"  [유튜브] 3단계: 댓글 키워드 추출")
    if all_texts:
        noun_counts = extract_nouns(all_texts)
        top_nouns = noun_counts[:_TOP_NOUNS]
        print(f"  [유튜브] 전체 {len(noun_counts)}개 명사 중 상위 {len(top_nouns)}개")
        for noun, count in top_nouns[:10]:
            print(f"    - {noun}: {count}회")
    else:
        top_nouns = []
        print(f"  [유튜브] 추출할 댓글 없음")

    # 저장
    _persist(keyword, query, videos, comments_by_youtube_id, top_nouns)

    # 결과 포맷
    total_comments = sum(len(cs) for cs in comments_by_youtube_id.values())
    lines = [f"[유튜브 영상: {len(videos)}건 (검색어: {query})]"]
    for v in videos:
        lines.append(f"- {v.title} ({v.channel_name}) {v.video_url}")

    lines.append(f"\n[댓글 수집: {total_comments}건 / {len(videos)}개 영상]")
    for v in videos:
        cs = comments_by_youtube_id.get(v.video_id, [])
        sample = cs[0].text[:80] if cs else "(댓글 없음)"
        lines.append(f"- {v.title[:50]}: {len(cs)}건 (예: {sample})")

    if top_nouns:
        lines.append(f"\n[댓글 키워드 TOP {len(top_nouns)}]")
        for noun, count in top_nouns:
            lines.append(f"- {noun}: {count}회")

    return "\n".join(lines)


# ------------------------------------------------------------------
# Internal — 저장
# ------------------------------------------------------------------
def _persist(
    keyword: Optional[str],
    query_used: str,
    videos: List[Any],
    comments_by_youtube_id: Dict[str, List[Any]],
    top_nouns: List[tuple],
) -> None:
    """저장 순서:
       1) MySQL 로그 헤더 INSERT → log_id
       2) MySQL 영상 메타데이터 INSERT (각 row id 획득)
       3) PG 에 영상별 댓글 INSERT (id = MySQL 영상 row id)
    """
    try:
        log_id = _save_log_header(keyword, query_used, videos, comments_by_youtube_id, top_nouns)
        print(f"  [유튜브][DB] investment_youtube_logs 저장 (id={log_id})")

        yt_id_to_mysql_pk = _save_videos(log_id, videos, comments_by_youtube_id)
        print(f"  [유튜브][DB] investment_youtube_videos 저장 완료 ({len(yt_id_to_mysql_pk)}건)")

        _save_comments_to_pg(yt_id_to_mysql_pk, comments_by_youtube_id)
        print(f"  [유튜브][PG] investment_youtube_video_comments 저장 완료")

    except Exception as exc:
        print(f"  [유튜브] ❌ DB 저장 실패 (파이프라인은 계속): {exc}")
        print(f"  [유튜브] traceback:\n{traceback.format_exc()}")
        logger.error("investment YouTube 저장 실패: %s", exc, exc_info=True)


def _save_log_header(
    keyword: Optional[str],
    query_used: str,
    videos: List[Any],
    comments_by_youtube_id: Dict[str, List[Any]],
    top_nouns: List[tuple],
) -> int:
    keywords_top = [
        {"noun": noun, "count": count, "rank": i + 1}
        for i, (noun, count) in enumerate(top_nouns)
    ]
    comment_count = sum(len(cs) for cs in comments_by_youtube_id.values())

    db = SessionLocal()
    try:
        repo = InvestmentYoutubeLogRepositoryImpl(db)
        return repo.save(
            keyword=keyword,
            query_used=query_used,
            video_count=len(videos),
            comment_count=comment_count,
            keyword_count=len(top_nouns),
            keywords_top=keywords_top,
        )
    finally:
        db.close()


def _save_videos(
    log_id: int,
    videos: List[Any],
    comments_by_youtube_id: Dict[str, List[Any]],
) -> Dict[str, int]:
    """영상 메타데이터를 MySQL 에 저장하고 {youtube_video_id: mysql_pk} 맵을 반환."""
    result: Dict[str, int] = {}
    db = SessionLocal()
    try:
        repo = InvestmentYoutubeVideoRepositoryImpl(db)
        for v in videos:
            pk = repo.save(
                log_id=log_id,
                video_id=v.video_id,
                title=v.title,
                channel_name=v.channel_name,
                video_url=v.video_url,
                thumbnail_url=v.thumbnail_url,
                # YoutubeVideoItem.published_at 은 "2024-01-15T10:30:00Z" 형식의 str
                # → MySQL DateTime 컬럼에 맞게 datetime 으로 변환
                published_at=_parse_iso_datetime(v.published_at),
                comment_count=len(comments_by_youtube_id.get(v.video_id, [])),
            )
            result[v.video_id] = pk
    finally:
        db.close()
    return result


def _parse_iso_datetime(value: Any) -> Optional[datetime]:
    """YouTube API 의 ISO 8601 Z 문자열을 datetime 으로 파싱."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _save_comments_to_pg(
    yt_id_to_mysql_pk: Dict[str, int],
    comments_by_youtube_id: Dict[str, List[Any]],
) -> None:
    """영상별 댓글을 PG JSONB 에 저장. id 는 MySQL 영상 PK."""
    db = PostgresSessionLocal()
    try:
        repo = InvestmentYoutubeVideoCommentRepositoryImpl(db)
        for youtube_video_id, mysql_pk in yt_id_to_mysql_pk.items():
            comments = comments_by_youtube_id.get(youtube_video_id, [])
            comments_payload = [
                {
                    "comment_id": c.comment_id,
                    "author_name": c.author_name,
                    "text": c.text,
                    "like_count": c.like_count,
                    "published_at": c.published_at.isoformat() if c.published_at else None,
                }
                for c in comments
            ]
            repo.save(
                video_pk=mysql_pk,
                video_id=youtube_video_id,
                comments=comments_payload,
            )
    finally:
        db.close()


def _save_log_only(keyword: Optional[str], query_used: str, top_nouns: List[tuple]) -> None:
    """검색 결과 없을 때 로그 헤더만 저장."""
    try:
        _save_log_header(keyword, query_used, videos=[], comments_by_youtube_id={}, top_nouns=top_nouns)
    except Exception as exc:
        logger.error("빈 로그 저장 실패: %s", exc, exc_info=True)
