from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app_secure.database.db import get_db
from app_secure.schemas.user import UserCreate
from app_secure.crud.user import create_user, authenticate_user, get_user_by_username
from app_secure.core.security import create_access_token
from app_secure.core.limiter import limiter
from app_secure.crud.token import add_token_to_blacklist

router = APIRouter()

#on a besoin de récupérer le token pour le mettre en liste noire
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
@router.post("/register", tags=["Auth"])
@limiter.limit("5/hour") #limitation pour éviter la création de comptes de spam
def register_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    #vérification captcha, défense api6
    #ici le captcha : question statique, qui demande le résultat de 3+5
    #le script d'attaque ne sait pas qu'il faut envoyer ce champ ou ne sait pas le calculer.
    if user.captcha_answer != 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CAPTCHA. Are you a robot?"
        )
    db_user_exists = get_user_by_username(db, username=user.username)
    if db_user_exists:
        raise HTTPException(status_code=400, detail="Username already registered")
    create_user(db=db, user=user)
    return {"message": "User registered successfully."}

@router.post("/login", tags=["Auth"])
@limiter.limit("1000000/minute") #SECURITE API 2: protection contre le brute force
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},)
    #création du token avec expiration gérée dans security.py
    access_token = create_access_token(
        data={"sub": user.username})
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

#vraie déconnexion avec invalidation de token
@router.post("/logout", tags=["Auth"])
def logout_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    add_token_to_blacklist(db, token)
    return {"message": "Logged out successfully (Token invalidated)"}

class EmailSchema(BaseModel):
    email: str

@router.post("/forgot-password")
def forgot_password(data: EmailSchema):
    return {"message": f"A reset email has been sent to {data.email}"}