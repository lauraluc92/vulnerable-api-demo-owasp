from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.product import ProductInOrderResponse

class OrderCreate(BaseModel):
    product_id: int
    quantity: int = 1


class OrderResponse(BaseModel):
    id: int
    buyer_id: int #faille pai1
    product_id: int
    quantity: int
    created_at: datetime
    #détails produits inclus
    product: Optional[ProductInOrderResponse]
    
    class Config:
        from_attributes = True