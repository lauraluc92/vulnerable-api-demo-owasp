from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SellerResponseSecure(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class ProductResponseSecure(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    blocked: bool
    seller: SellerResponseSecure 
    stock: int
    class Config:
        from_attributes = True

class ProductInOrderResponseSecure(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    blocked: bool
    stock: int
    class Config:
        from_attributes = True

class ProductUpdateSecure(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    stock: int = 10

class ProductReportCreate(BaseModel):
    reason: str

class ProductReportResponse(BaseModel):
    reporter: str
    reporter_id: int
    reason: str
    timestamp: datetime