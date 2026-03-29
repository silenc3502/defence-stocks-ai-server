from dataclasses import dataclass, field


@dataclass
class DefenceStock:
    name: str
    code: str
    themes: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


# 한국 방산주 종목 목록
DEFENCE_STOCKS = [
    DefenceStock(
        name="한화에어로스페이스",
        code="012450",
        themes=["항공엔진", "우주발사체", "자주포", "방산수출"],
        keywords=["한화에어로스페이스", "한화에어로", "항공엔진", "우주", "K9", "자주포", "폴란드", "방산수출"],
    ),
    DefenceStock(
        name="한화오션",
        code="042660",
        themes=["함정", "잠수함", "해군"],
        keywords=["한화오션", "함정", "잠수함", "해군", "구축함", "호위함", "상륙함"],
    ),
    DefenceStock(
        name="한화시스템",
        code="272210",
        themes=["전자전", "감시정찰", "위성", "UAM"],
        keywords=["한화시스템", "전자전", "감시", "정찰", "위성", "레이더", "UAM"],
    ),
    DefenceStock(
        name="LIG넥스원",
        code="079550",
        themes=["미사일", "유도무기", "방공"],
        keywords=["LIG넥스원", "넥스원", "미사일", "유도무기", "천궁", "천무", "현무", "방공", "대공"],
    ),
    DefenceStock(
        name="현대로템",
        code="064350",
        themes=["전차", "장갑차", "철도"],
        keywords=["현대로템", "K2", "전차", "장갑차", "K2전차", "보병전투차"],
    ),
    DefenceStock(
        name="KAI(한국항공우주)",
        code="047810",
        themes=["전투기", "헬기", "항공"],
        keywords=["KAI", "한국항공우주", "한국항공", "전투기", "KF-21", "수리온", "헬기", "보라매"],
    ),
    DefenceStock(
        name="풍산",
        code="103140",
        themes=["탄약", "포탄"],
        keywords=["풍산", "탄약", "포탄", "화약", "155mm"],
    ),
    DefenceStock(
        name="한화",
        code="000880",
        themes=["화약", "방산지주"],
        keywords=["한화", "한화그룹", "방산지주"],
    ),
    DefenceStock(
        name="STX엔진",
        code="077970",
        themes=["함정엔진", "선박엔진"],
        keywords=["STX엔진", "함정엔진", "선박엔진", "디젤엔진"],
    ),
    DefenceStock(
        name="빅텍",
        code="065450",
        themes=["방탄", "방호", "보호장비"],
        keywords=["빅텍", "방탄", "방호", "보호장비", "방탄복"],
    ),
    DefenceStock(
        name="퍼스텍",
        code="010820",
        themes=["전자전", "통신", "군통신"],
        keywords=["퍼스텍", "전자전", "군통신", "전술통신"],
    ),
    DefenceStock(
        name="스페코",
        code="013810",
        themes=["전력", "국방전력"],
        keywords=["스페코", "전력", "국방전력", "군용전원"],
    ),
    DefenceStock(
        name="한국카본",
        code="017960",
        themes=["복합소재", "항공소재"],
        keywords=["한국카본", "복합소재", "탄소섬유", "항공소재"],
    ),
    DefenceStock(
        name="아이쓰리시스템",
        code="214430",
        themes=["적외선", "광학", "감시장비"],
        keywords=["아이쓰리시스템", "적외선", "광학", "열상", "감시장비"],
    ),
]

# 테마별 키워드 매핑: 테마 → 관련 키워드 목록
THEME_KEYWORDS = {
    "미사일": ["미사일", "유도무기", "천궁", "천무", "현무", "방공", "대공", "ICBM", "탄도미사일"],
    "전투기": ["전투기", "KF-21", "보라매", "공군", "스텔스", "전투항공"],
    "함정": ["함정", "잠수함", "구축함", "호위함", "해군", "상륙함", "항공모함"],
    "전차": ["전차", "장갑차", "K2", "K2전차", "보병전투차", "육군"],
    "자주포": ["자주포", "K9", "K9자주포", "포병", "곡사포"],
    "탄약": ["탄약", "포탄", "화약", "155mm", "탄환"],
    "항공": ["항공", "헬기", "수리온", "항공엔진", "UAM"],
    "우주": ["우주", "위성", "발사체", "누리호", "우주발사체"],
    "전자전": ["전자전", "레이더", "감시", "정찰", "통신", "열상", "적외선"],
    "방산수출": ["방산수출", "방산 수출", "폴란드", "수출", "NATO", "나토"],
    "안보": ["안보", "국방", "군사", "군비", "전쟁", "휴전", "국방비"],
    "중동": ["중동", "이란", "이스라엘", "사우디"],
    "우크라이나": ["우크라이나", "러시아", "NATO", "나토"],
}


def find_stocks_by_keywords(keywords: list[str]) -> list[dict]:
    keyword_set = {kw.lower() for kw in keywords}
    results = []

    for stock in DEFENCE_STOCKS:
        stock_keywords = {kw.lower() for kw in stock.keywords}
        matched = keyword_set & stock_keywords

        if matched:
            results.append({
                "name": stock.name,
                "code": stock.code,
                "themes": stock.themes,
                "matched_keywords": sorted(matched),
                "relevance_score": len(matched),
            })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results


def find_themes_by_keywords(keywords: list[str]) -> list[dict]:
    keyword_set = {kw.lower() for kw in keywords}
    results = []

    for theme, theme_kws in THEME_KEYWORDS.items():
        theme_kw_set = {kw.lower() for kw in theme_kws}
        matched = keyword_set & theme_kw_set

        if matched:
            results.append({
                "theme": theme,
                "matched_keywords": sorted(matched),
                "relevance_score": len(matched),
            })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results
