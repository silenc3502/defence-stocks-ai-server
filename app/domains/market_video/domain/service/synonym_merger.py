from collections import Counter

# 동의어 매핑: { 변환 대상: 대표 키워드 }
# 키에 해당하는 단어가 나오면 값(대표 키워드)으로 통합
SYNONYM_MAP = {
    # 방산 관련
    "방산株": "방산주",
    "방산 관련주": "방산주",
    "방위산업": "방산",
    "군수산업": "방산",
    "군수업체": "방산",
    "군수": "방산",

    # 기업명 통합
    "한화에어로": "한화에어로스페이스",
    "한화에어": "한화에어로스페이스",
    "한국항공우주": "KAI",
    "한국항공": "KAI",

    # 무기 체계
    "K9자주포": "K9",
    "K2전차": "K2",

    # 국가/지역
    "미국": "미국",
    "북한": "북한",
    "우크라": "우크라이나",

    # 주식 관련
    "주가": "주식",
    "주식시장": "주식",
    "증시": "주식",
    "코스피": "주식",
    "코스닥": "주식",
    "종목": "주식",
    "상장": "주식",

    # 경제 관련
    "수출액": "수출",
    "수출량": "수출",
    "방산수출": "방산 수출",

    # 군사 관련
    "국방부": "국방",
    "국방비": "국방",
    "군비증강": "군비",
    "군사력": "군사",
}


def merge_synonyms(noun_counts: list[tuple[str, int]]) -> list[tuple[str, int]]:
    merged = Counter()

    for noun, count in noun_counts:
        representative = SYNONYM_MAP.get(noun, noun)
        merged[representative] += count

    return merged.most_common()
