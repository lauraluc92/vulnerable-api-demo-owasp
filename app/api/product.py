from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.crud.product import get_product_by_id, get_all_products
from app.crud.report import create_or_update_user_report, get_reports_by_product_id
from app.schemas.product import ProductResponse
from app.schemas.product import ProductUpdateVulnerable, ProductReportCreate, ProductReportResponse
from app.models.user import User
from app.crud.product import update_product_vulnerable
from app.core.security import get_current_user
from typing import List

router = APIRouter()

#vulnérable api4: endpoint sans rate limiting ni pagination
@router.get("/products", response_model=List[ProductResponse], tags=["Products"])
def list_all_products(db: Session = Depends(get_db)):
    products = get_all_products(db)
    return products

#vulnérable api3: endpoint renvoie trop de données (sensibles)
@router.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

#VULNERABLE API 3 car update_product_vulnerable modifie tout, même "blocked" qui ne devrait pas être modifiable
@router.patch("/products/{product_id}", response_model=ProductResponse, tags=["Users"])
def update_product(product_id: int, product_update: ProductUpdateVulnerable, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = get_product_by_id(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="User unauthorized to perform description modification")
    updated_product = update_product_vulnerable(db, product, product_update)
    return updated_product

@router.get("/products/{product_id}/reports", response_model=List[ProductReportResponse], tags=["Products"])
def get_product_reports(product_id: int, db: Session = Depends(get_db)):
    reports = get_reports_by_product_id(db, product_id)
    return [
        {
            "reporter": report.reporter.username,
            "reporter_id": report.reporter.id,
            "reason": report.reason,
            "timestamp": report.timestamp
        }
        for report in reports
    ]

@router.post("/products/{product_id}/reports", response_model=ProductReportResponse, tags=["Products"])
def report_product(
    product_id: int, 
    report_data: ProductReportCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = create_or_update_user_report(
        db=db,
        product_id=product_id,
        reporter_id=current_user.id, #id de l'user connecté
        reason=report_data.reason
    )
    return {
        "id": report.id,
        "reporter": current_user.username,
        "reporter_id": current_user.id, 
        "reason": report.reason,
        "timestamp": report.timestamp
    }
