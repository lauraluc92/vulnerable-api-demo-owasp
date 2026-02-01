from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app_secure.schemas.product import ProductInOrderResponseSecure

class OrderCreate(BaseModel):
    product_id: int
    quantity: int = 1

class OrderResponse(BaseModel):
    id: int
    buyer_id: int 
    product_id: int
    quantity: int
    created_at: datetime
    #défense api3
    product: Optional[ProductInOrderResponseSecure]
    
    class Config:
        from_attributes = True