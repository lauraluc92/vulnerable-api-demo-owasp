from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app_secure.database.db import get_db
from app_secure.models.user import User
from app_secure.schemas.user import UserResponse, UserUpdateAdmin
from app_secure.core.security import get_current_user
from app_secure.crud.user import get_all_users, get_user_by_id, update_user_secure
from app_secure.crud.order import get_all_orders
from app_secure.api.contact import contact_messages_db, ContactMessage

router = APIRouter()

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        #on renvoie 403 Forbidden.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrator privileges required."
        )
    return current_user

@router.get("/users", response_model=List[UserResponse], tags=["Admin"])
def list_all_users_admin(
    db: Session = Depends(get_db), 
    current_admin: User = Depends(get_current_admin)
):
    users = get_all_users(db)
    return users

@router.get("/users/{user_id}", response_model=UserResponse, tags=["Admin"])
def read_user_by_id_admin(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_admin)
):
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=UserResponse, tags=["Admin"])
def update_user_by_admin(
    user_id: int,
    user_update: UserUpdateAdmin,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = update_user_secure(db, user, user_update)
    return updated_user

@router.get("/orders", tags=["Admin"])
def list_all_orders_admin(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return get_all_orders(db)

@router.delete("/users/{user_id}", tags=["Admin"])
def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):  
    return {
        "message": f"User ID:{user_id} successfully 'deleted'.",
        "deleted_by": current_admin.username,
    }

@router.post("/promote/{user_id}", tags=["Admin"])
def promote_user_to_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
): 
    target_user = get_user_by_id(db, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = promote_user_to_admin(db, target_user)
    return {
        "message": f"Success: User {updated_user.username} (ID {user_id}) is now ADMIN.",
        "promoted_by": current_admin.username,
        "warning": "Please log in again to get a new token."
    }

###protection api8
#on exige une authentification Admin + la protection CORS du main.py
@router.get("/stats", tags=["Admin"])
def get_financial_stats_internal(
    current_admin: User = Depends(get_current_admin)
):
    return {
        "status": "CONFIDENTIAL",
        "total_revenue": 154300.50,
        "active_carts": 42,
        "buyer": "The President",
        "server_load": "12%",
        "top_selling_product": "iPhone 16"
    }

#seul admin peut lire les messages
@router.get("/messages", response_model=List[ContactMessage], tags=["Admin"])
def read_all_messages(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to administrators.")
    return contact_messages_db