from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app_secure.database.db import get_db
from app_secure.models.user import User
from app_secure.models.order import Order
from app_secure.schemas.order import OrderCreate, OrderResponse
from app_secure.crud.order import create_order, get_order_by_id, get_user_orders
from app_secure.crud.product import get_product_by_id
from app_secure.core.security import get_current_user
from app_secure.core.limiter import limiter

router = APIRouter()
@router.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def read_order(
    order_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    order = get_order_by_id(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.buyer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied. Not your order."
        )
    return order


@router.get("/orders/me", response_model=List[OrderResponse])
def read_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_user_orders(db, user_id=current_user.id)

@router.post("/orders", response_model=OrderResponse, tags=["Orders"])
@limiter.limit("5/minute") #rate limiting sur la création de commande
def place_order(
    request: Request,
    order: OrderCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    product = get_product_by_id(db, order.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Out of stock")    
    existing_order = db.query(Order).filter(
        Order.buyer_id == current_user.id,
        Order.product_id == order.product_id
    ).first()
    if existing_order:
         raise HTTPException(status_code=400, detail="Quota exceeded: maximum 1 item per customer.")
    product.stock -= order.quantity
    db.add(product)
    db_order = create_order(db, current_user.id, order.product_id, order.quantity)
    db.commit()
    return db_order