from sqlalchemy.orm import Session, joinedload
from app.models.product import Product
from app.schemas.product import ProductUpdateVulnerable

def get_product_by_id(db: Session, product_id: int) -> Product | None:
    return db.query(Product).options(
        joinedload(Product.seller)
    ).filter(Product.id == product_id).first()

def get_all_products(db: Session):
    return db.query(Product).options(
        joinedload(Product.seller)
    ).all() 

def update_product_vulnerable(db: Session, db_product: Product, product_update: ProductUpdateVulnerable) -> Product:
    update_data = product_update.model_dump(exclude_unset=True) 
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

