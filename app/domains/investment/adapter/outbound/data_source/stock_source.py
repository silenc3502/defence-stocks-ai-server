"""종목 데이터 소스 — ListDefenceStocksUseCase 재사용.

방산주 종목 전체 리스트를 반환한다. keyword 와 무관하게 항상 전체 방산주
데이터를 조회한다 (keyword 는 다른 handler 와의 signature 통일 목적).
"""
from typing import Any, Dict, Optional, Tuple

from app.domains.stock_theme.adapter.outbound.persistence.defence_stock_repository_impl import (
    DefenceStockRepositoryImpl,
)
from app.domains.stock_theme.application.usecase.list_defence_stocks_usecase import (
    ListDefenceStocksUseCase,
)
from app.infrastructure.database.session import SessionLocal


def fetch_stock_data(keyword: Optional[str] = None) -> Tuple[str, Optional[Dict[str, Any]]]:
    print(f"  [종목] ListDefenceStocksUseCase 호출 (keyword={keyword!r}, 항상 전체 조회)")
    db = SessionLocal()
    try:
        usecase = ListDefenceStocksUseCase(DefenceStockRepositoryImpl(db))
        result = usecase.execute()
    finally:
        db.close()

    print(f"  [종목] 결과: {result.total_count}건")
    if not result.stocks:
        print("  [종목] 종목 데이터 없음")
        return "(종목 데이터 없음)", None

    lines = [f"[방산주 종목 리스트: {result.total_count}건]"]
    for i, s in enumerate(result.stocks):
        lines.append(f"- {s.name} ({s.code}): {', '.join(s.themes)}")
        print(f"  [종목] #{i + 1} {s.name} ({s.code})")

    # 종목 소스는 signal payload 없음 (방향성 신호 아님)
    return "\n".join(lines), None
