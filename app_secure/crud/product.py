from sqlalchemy.orm import Session, joinedload
from typing import List
from app_secure.models.product import Product
from app_secure.schemas.product import ProductCreate, ProductUpdateSecure

def get_product_by_id(db: Session, product_id: int) -> Product | None:
    return db.query(Product).options(joinedload(Product.seller)).filter(Product.id == product_id).first()

#skip et limit pour gérer la pagination demandée par le routeur
def get_all_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    return db.query(Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate, seller_id: int) -> Product:
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        stock=product.stock,
        seller_id=seller_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

#modif pour api3
def update_product_secure(db: Session, db_product: Product, product_update: ProductUpdateSecure):
    #update uniquement champs envoyés par l'utilisateur
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product