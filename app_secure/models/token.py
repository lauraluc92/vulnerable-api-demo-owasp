from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app_secure.database.base import Base

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    blacklisted_on = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BlacklistedToken(id={self.id}, date={self.blacklisted_on})>"