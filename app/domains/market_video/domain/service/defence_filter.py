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

DEFENCE_KEYWORDS = [
    "방산", "방위산업", "군사", "국방", "무기",
    "미사일", "전쟁", "NATO", "나토", "군비",
    "한화에어로스페이스", "한화오션", "LIG넥스원", "현대로템",
    "한국항공우주", "KAI", "풍산", "한화시스템",
    "방산주", "방산株", "방산 관련주", "군수",
    "전투기", "함정", "잠수함", "탱크", "장갑차",
    "K9", "K2", "천궁", "천무", "현무",
    "우크라이나", "대만", "중동", "안보",
    "폴란드", "수출", "방산 수출",
]

MAX_VIDEOS = 10
SEARCH_DAYS = 7


def contains_defence_keyword(title: str) -> bool:
    title_lower = title.lower()
    return any(keyword.lower() in title_lower for keyword in DEFENCE_KEYWORDS)
