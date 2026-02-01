from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdateVulnerable
from app.core.hashing import get_password_hash, verify_password 
import time

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password,
        role="user",
        blocked=0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if user.blocked > 0:
        current_timestamp = int(time.time())
        if current_timestamp < user.blocked:
            return None
    return user

def update_user_vulnerable(db: Session, db_user: User, user_update: UserUpdateVulnerable) -> User:
    update_data = user_update.model_dump(exclude_unset=True) 
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def promote_user_to_admin(db: Session, user: User) -> User:
    user.role = "admin"
    db.add(user)
    db.commit()
    db.refresh(user)
    return user