from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app_secure.database.db import get_db
from app_secure.models.user import User
from app_secure.schemas.user import UserResponse, UserUpdateSecure, UserPublic
from app_secure.crud.user import get_user_by_id, update_user_secure
from app_secure.core.security import get_current_user
from app_secure.core.hashing import verify_password
router = APIRouter()

@router.get("/users/me", response_model=UserResponse, tags=["Users"])
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/users/me", response_model=UserResponse, tags=["Users"])
def update_user_me(
    user_update: UserUpdateSecure,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_update.email is not None:
        if not user_update.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="To change your email address, you must confirm your current password.")
        if not verify_password(user_update.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password.")
    updated_user = update_user_secure(db, current_user, user_update)
    return updated_user

@router.get("/users/{user_id}", response_model=UserPublic, tags=["Users"])
def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


