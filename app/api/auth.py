from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.user import UserCreate
from app.crud.user import create_user, authenticate_user, get_user_by_username
from app.core.security import create_access_token 
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.limiter import limiter

router = APIRouter()

#ici avec le force=user, on s'inscrit que en tant que user
@router.post("/register", tags=["Auth"])
@limiter.limit("1/hour")
def register_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    db_user_exists = get_user_by_username(db, username=user.username)
    if db_user_exists:
        raise HTTPException(status_code=400, detail="Username already registered")
    create_user(db=db, user=user)
    return {"message": "User registered successfully."}

@router.post("/login", tags=["Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        #vérifier si l'utilisateur existe et est bloqué
        from app.crud.user import get_user_by_username
        existing_user = get_user_by_username(db, form_data.username)
        if existing_user and existing_user.blocked > 0:
            import time
            current_timestamp = int(time.time())
            if current_timestamp < existing_user.blocked:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account locked until {existing_user.blocked}",
                )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role
    }

### VULNERABLE API 2 CAR
#ici c'est un semblant de déconnexion pour l'instant, et donc ça n'invalide pas le token côté serveur
@router.post("/logout", tags=["Auth"])
def logout_user():
    return {"message": "Logged out"}

class EmailSchema(BaseModel):
    email: str
@router.post("/forgot-password", tags=["Auth"])
def forgot_password(data: EmailSchema):
    return {"message": f"A reset email has been sent to {data.email}"}