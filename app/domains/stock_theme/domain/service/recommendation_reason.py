SYSTEM_MESSAGE = (
    "당신은 한국 방산주 투자 분석 전문가입니다. "
    "주어진 종목, 테마, 키워드 정보를 바탕으로 "
    "해당 종목이 왜 추천되었는지 2~3문장으로 간결하게 설명해주세요. "
    "투자 권유가 아닌 정보 제공 목적임을 유의하세요."
)


def build_reason_prompt(name: str, code: str, themes: list[str], matched_keywords: list[str]) -> str:
    return (
        f"종목명: {name} (종목코드: {code})\n"
        f"관련 테마: {', '.join(themes)}\n"
        f"매칭된 키워드: {', '.join(matched_keywords)}\n\n"
        f"위 정보를 바탕으로 이 종목이 현재 방산 시장 트렌드에서 "
        f"왜 주목받을 수 있는지 추천 이유를 2~3문장으로 작성해주세요."
    )
