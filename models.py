from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from database import Base

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    salt = Column(String, nullable=False)
    creator_choice_hash = Column(String, nullable=False)
    names_json = Column(Text, nullable=False)  # JSON-encoded array of candidate names
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)