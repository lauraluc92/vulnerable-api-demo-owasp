from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderResponse
from app.crud.order import create_order, get_order_by_id, get_user_orders
from app.crud.product import get_product_by_id
from app.core.security import get_current_user

from typing import List

router = APIRouter()

@router.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def read_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = get_order_by_id(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/orders/user/{target_user_id}", response_model=List[OrderResponse], tags=["Orders"])
def read_user_orders(target_user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_user_orders(db, user_id=target_user_id)

@router.post("/orders", response_model=OrderResponse, tags=["Orders"])
def place_order(order: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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