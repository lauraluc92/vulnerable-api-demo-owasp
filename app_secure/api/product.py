from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app_secure.database.db import get_db
from app_secure.models.user import User
from app_secure.core.security import get_current_user
from app_secure.core.limiter import limiter
from app_secure.schemas.product import ProductResponseSecure, ProductUpdateSecure, ProductReportCreate, ProductReportResponse
from app_secure.crud.product import get_product_by_id, get_all_products, update_product_secure
from app_secure.crud.report import create_or_update_user_report, get_reports_by_product_id

router = APIRouter()

@router.get("/products", response_model=List[ProductResponseSecure], tags=["Products"])
@limiter.limit("20/minute")
def list_all_products(
    request: Request,
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    #protection API4: limite max pour pagination
    if limit > 50:
        limit = 50
    products = get_all_products(db, skip=skip, limit=limit)
    return products

@router.get("/products/{product_id}", response_model=ProductResponseSecure, tags=["Products"])
@limiter.limit("60/minute")
def read_product(
    request: Request,
    product_id: int, 
    db: Session = Depends(get_db)
):
    product = get_product_by_id(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.patch("/products/{product_id}", response_model=ProductResponseSecure, tags=["Products"])
def update_product(
    product_id: int, 
    product_update: ProductUpdateSecure,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    product = get_product_by_id(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="User unauthorized to perform description modification")
    updated_product = update_product_secure(db, product, product_update)
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