from sqlalchemy.orm import Session
from app_secure.models.token import BlacklistedToken

def is_token_blacklisted(db: Session, token: str) -> bool:
    return db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first() is not None

def add_token_to_blacklist(db: Session, token: str) -> BlacklistedToken:
    if is_token_blacklisted(db, token):
        return
    db_token = BlacklistedToken(token=token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token