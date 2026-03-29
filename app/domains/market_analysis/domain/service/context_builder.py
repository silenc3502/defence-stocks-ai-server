from app.domains.market_video.domain.service.noun_extractor import extract_nouns
from app.domains.stock_theme.domain.entity.defence_stock import DefenceStock


def build_keywords_context(noun_counts: list[tuple[str, int]], top_n: int = 30) -> str:
    if not noun_counts:
        return "키워드 데이터 없음"

    lines = [f"- {noun}: {count}회" for noun, count in noun_counts[:top_n]]
    return "\n".join(lines)


def build_stocks_context(stocks: list[DefenceStock]) -> str:
    if not stocks:
        return "등록된 종목 없음"

    lines = []
    for s in stocks:
        lines.append(f"- {s.name} ({s.code}) | 테마: {', '.join(s.themes)}")
    return "\n".join(lines)


def build_recommendations_context(
    stocks: list[DefenceStock],
    noun_counts: list[tuple[str, int]],
    top_n: int = 50,
) -> str:
    if not stocks or not noun_counts:
        return "추천 데이터 없음"

    keyword_set = {noun.lower() for noun, _ in noun_counts[:top_n]}

    lines = []
    for stock in stocks:
        theme_set = {t.lower() for t in stock.themes}
        name_keywords = {stock.name.lower()}
        matchable = theme_set | name_keywords
        matched = keyword_set & matchable

        if matched:
            lines.append(
                f"- {stock.name} ({stock.code}) | 매칭 키워드: {', '.join(sorted(matched))} | 관련도: {len(matched)}"
            )

    if not lines:
        return "매칭된 추천 종목 없음"

    lines.sort(key=lambda x: x.count(","), reverse=True)
    return "\n".join(lines)
