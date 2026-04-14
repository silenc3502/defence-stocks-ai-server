from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CollectedInvestmentNewsItem(BaseModel):
    id: int                              # MySQL investment_news.id (= PG investment_news_contents.id)
    title: str
    source: Optional[str] = None
    link: str
    published_at: Optional[datetime] = None
    content: str                         # ArticleContentFetcher 가 추출한 본문 텍스트


class CollectInvestmentNewsResponse(BaseModel):
    keyword: Optional[str]               # 입력 종목명 (None 가능)
    query_used: str                      # 실제 검색에 사용된 쿼리 (fallback 적용 후)
    items: List[CollectedInvestmentNewsItem]
    total_searched: int                  # SERP 가 반환한 총 결과 수
    success_count: int                   # 본문 수집 + DB 저장 성공 건수
    failure_count: int                   # 부분 실패 건수
