from pydantic import BaseModel
from typing import Optional
from datetime import datetime
#vulnerabilité api3 car le schéma pydantic renvoie trop de données meme sensibles
class SellerResponseVulnerable(BaseModel):
    id: int
    username: str
    email: str
    role: str
    phone: Optional[str] = None
    address: Optional[str] = None
    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    blocked: bool
    seller: SellerResponseVulnerable 
    stock: int
    class Config:
        from_attributes = True

class ProductInOrderResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    blocked: bool
    stock: int
    class Config:
        from_attributes = True

class ProductUpdateVulnerable(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    blocked: Optional[bool] = None #le problème ici pour API3 mass assignment

#ajout pour scénario signalement
class ProductReportCreate(BaseModel):
    reason: str

class ProductReportResponse(BaseModel):
    reporter: str
    reporter_id: int
    reason: str
    timestamp: datetime