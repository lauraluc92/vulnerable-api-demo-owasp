from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateVulnerable
from app.crud.user import get_user_by_id, update_user_vulnerable
from app.core.security import get_current_user

router = APIRouter()

#VULNERABLE API 1 car avec get_user_by_id on peut modifavoir accès à tous les users selon l'id
@router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def read_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


#VULNERABLE API 1 car avec get_user_by_id on a accès à tous les users selon l'id et donc on peut modifier n'importe qui
#VULNERABLE API 3 car update_user_vulnerable modifie tout, même "role" qui ne devrait pas être modifiable
@router.patch("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(user_id: int, user_update: UserUpdateVulnerable, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = update_user_vulnerable(db, user, user_update)
    return updated_user
