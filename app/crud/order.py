from sqlalchemy.orm import Session, joinedload
from app.models.order import Order
from typing import List

def create_order(db: Session, buyer_id: int, product_id: int, quantity: int) -> Order:
    db_order = Order(
        buyer_id=buyer_id,
        product_id=product_id,
        quantity=quantity)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order_by_id(db: Session, order_id: int) -> Order | None:
    return db.query(Order).options(
        joinedload(Order.product).joinedload(Order.product.seller)
    ).filter(Order.id == order_id).first()

def get_user_orders(db: Session, user_id: int) -> List[Order]:
    return db.query(Order).filter(Order.buyer_id == user_id).all()

def get_all_orders(db: Session) -> List[Order]:
    return db.query(Order).all()