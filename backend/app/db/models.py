from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    searches = relationship("SearchHistory", back_populates="user")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticker = Column(String, nullable=False)
    verdict = Column(String)
    investment_score = Column(Float)
    latest_price = Column(Float)
    searched_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="searches")


class WatchlistItem(Base):
    __tablename__ = "watchlist"
    __table_args__ = (
        UniqueConstraint("user_id", "ticker", name="uq_watchlist_user_ticker"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    ticker = Column(String, nullable=False)
    last_verdict = Column(String)
    previous_verdict = Column(String)
    last_score = Column(Float)
    last_price = Column(Float)
    added_at = Column(DateTime, default=datetime.utcnow)
    last_checked_at = Column(DateTime)
    changed_at = Column(DateTime)