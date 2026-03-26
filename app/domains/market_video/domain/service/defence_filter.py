DEFENCE_CHANNELS = [
    "UCF8AeLlUbEpKju6v1H6p8Eg",  # 한국경제TV
    "UCbMjg2EvXs_RUGW-KrdM3pw",  # SBS Biz
    "UCTHCOPwqNfZ0uiKOvFyhGwg",  # 연합뉴스TV
    "UCcQTRi69dsVYHN3exePtZ1A",  # KBS News
    "UCG9aFJTZ-lMCHAiO1KJsirg",  # MBN
    "UCsU-I-vHLiaMfV_ceaYz5rQ",  # JTBC News
    "UClErHbdZKUnD1NyIUeQWvuQ",  # 머니투데이
    "UC8Sv6O3Ux8ePVqorx8aOBMg",  # 이데일리TV
    "UCnfwIKyFYRuqZzzKBDt6JOA",  # 매일경제TV
]

# 방산 핵심 키워드 (1개만 매칭되어도 통과)
DEFENCE_PRIMARY_KEYWORDS = [
    "방산", "방위산업", "방산주", "방산株", "방산 관련주",
    "한화에어로스페이스", "한화오션", "한화시스템", "한화디펜스",
    "LIG넥스원", "현대로템", "한국항공우주", "KAI", "풍산",
    "군수산업", "군수업체", "방산 수출", "방산수출",
]

# 방산 보조 키워드 (2개 이상 매칭 시 통과)
DEFENCE_SECONDARY_KEYWORDS = [
    "군사", "국방", "국방부", "미사일", "군비증강",
    "NATO", "나토", "군수", "전투기", "함정", "잠수함",
    "탱크", "장갑차", "K9자주포", "K2전차", "천궁", "천무", "현무",
    "우크라이나 무기", "폴란드 수출",
    "안보 위기", "군사 동맹", "무기 수출", "무기 거래",
]

DEFENCE_SEARCH_QUERIES = [
    "방산주",
    "방위산업",
    "한화에어로스페이스",
    "현대로템",
    "LIG넥스원",
    "방산 수출",
    "국방 군사",
]

MAX_VIDEOS = 10
SEARCH_DAYS = 7


def contains_defence_keyword(title: str) -> bool:
    title_lower = title.lower()

    for keyword in DEFENCE_PRIMARY_KEYWORDS:
        if keyword.lower() in title_lower:
            return True

    secondary_count = sum(1 for kw in DEFENCE_SECONDARY_KEYWORDS if kw.lower() in title_lower)
    return secondary_count >= 2
