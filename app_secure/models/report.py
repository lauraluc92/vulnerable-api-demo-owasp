from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app_secure.database.db import Base
from datetime import datetime

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    reason = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    product_id = Column(Integer, ForeignKey("products.id"))
    reporter_id = Column(Integer, ForeignKey("users.id"))
    product = relationship("Product", back_populates="reports")
    reporter = relationship("User")