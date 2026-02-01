from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app_secure.database.base import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String)
    blocked = Column(Boolean, default=False)
    stock = Column(Integer, default=100)
    seller_id = Column(Integer, ForeignKey("users.id"))
    seller = relationship("User", back_populates="products")
    reports = relationship("Report", back_populates="product", cascade="all, delete-orphan")