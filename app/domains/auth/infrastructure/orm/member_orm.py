from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.infrastructure.database.session import Base


class MemberORM(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kakao_id = Column(String(64), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
