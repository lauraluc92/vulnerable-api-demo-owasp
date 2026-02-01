from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app_secure.database.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="user")
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    blocked = Column(Integer, default=0)
    products = relationship("Product", back_populates="seller")
    orders = relationship("Order", back_populates="buyer")