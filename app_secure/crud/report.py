from sqlalchemy.orm import Session
from app_secure.models.report import Report
from datetime import datetime

def get_reports_by_product_id(db: Session, product_id: int):
    return db.query(Report).filter(Report.product_id == product_id).all()

def get_report_by_user_and_product(db: Session, user_id: int, product_id: int):
    return db.query(Report).filter(
        Report.product_id == product_id,
        Report.reporter_id == user_id
    ).first()

def create_or_update_user_report(db: Session, product_id: int, reporter_id: int, reason: str) -> Report:
    existing_report = get_report_by_user_and_product(db, reporter_id, product_id)
    if existing_report:
        existing_report.reason = reason
        existing_report.timestamp = datetime.utcnow()
    else:
        existing_report = Report(
            product_id=product_id,
            reporter_id=reporter_id,
            reason=reason,
            timestamp=datetime.utcnow()
        )
        db.add(existing_report)

    db.commit()
    db.refresh(existing_report)
    return existing_report
