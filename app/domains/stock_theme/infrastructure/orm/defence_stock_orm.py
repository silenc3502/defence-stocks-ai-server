from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.infrastructure.database.session import Base


class DefenceStockORM(Base):
    __tablename__ = "defence_stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    themes = relationship("DefenceStockThemeORM", back_populates="stock", cascade="all, delete-orphan")


class DefenceStockThemeORM(Base):
    __tablename__ = "defence_stock_themes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("defence_stocks.id"), nullable=False, index=True)
    theme = Column(String(50), nullable=False)
    stock = relationship("DefenceStockORM", back_populates="themes")
