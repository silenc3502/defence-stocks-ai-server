from sqlalchemy.orm import Session

from app.domains.stock_theme.adapter.outbound.persistence.defence_stock_repository_impl import DefenceStockRepositoryImpl
from app.domains.stock_theme.domain.entity.defence_stock import DefenceStock

SEED_DATA = [
    DefenceStock(name="한화에어로스페이스", code="012450", themes=["전투기", "미사일", "자주포", "방산수출"]),
    DefenceStock(name="LIG넥스원", code="079550", themes=["미사일", "방공", "유도무기"]),
    DefenceStock(name="한국항공우주(KAI)", code="047810", themes=["전투기", "항공", "헬기"]),
    DefenceStock(name="한화시스템", code="272210", themes=["레이더", "전자전", "위성", "UAM"]),
    DefenceStock(name="한화오션", code="042660", themes=["함정", "잠수함", "해군"]),
    DefenceStock(name="현대로템", code="064350", themes=["전차", "장갑차", "철도"]),
    DefenceStock(name="풍산", code="103140", themes=["탄약", "포탄"]),
    DefenceStock(name="한화", code="000880", themes=["방산지주", "화약"]),
    DefenceStock(name="STX엔진", code="077970", themes=["함정엔진", "선박엔진"]),
    DefenceStock(name="빅텍", code="065450", themes=["방탄", "방호", "보호장비"]),
    DefenceStock(name="퍼스텍", code="010820", themes=["군통신", "전자전"]),
    DefenceStock(name="스페코", code="013810", themes=["국방전력", "전력"]),
    DefenceStock(name="한국카본", code="017960", themes=["복합소재", "항공소재"]),
    DefenceStock(name="아이쓰리시스템", code="214430", themes=["적외선", "광학", "감시장비"]),
    DefenceStock(name="LIG넥스원우", code="079560", themes=["미사일", "방공"]),
    DefenceStock(name="한화에어로스페이스우", code="012451", themes=["전투기", "미사일"]),
    DefenceStock(name="현대위아", code="011210", themes=["포탄", "자주포", "엔진"]),
    DefenceStock(name="삼성SDI", code="006400", themes=["배터리", "군용배터리"]),
    DefenceStock(name="한컴인텔리전스", code="030520", themes=["군사SW", "지휘통제"]),
    DefenceStock(name="넥스트칩", code="092600", themes=["영상처리", "감시"]),
]


def seed_defence_stocks(db: Session) -> None:
    repo = DefenceStockRepositoryImpl(db)

    if repo.count() > 0:
        return

    for stock in SEED_DATA:
        repo.save(stock)
