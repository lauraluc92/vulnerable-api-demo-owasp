from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None
    captcha_answer: int

#protection contre api3 mass assignment
#on retire les champs sensibles (role, blocked) de ce schema de mise a jour
#ainsi, meme si un attaquant les envoie dans le json, ils seront ignores par pydantic
class UserUpdateSecure(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    class Config:
        extra = "forbid"

class UserUpdateAdmin(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    blocked: Optional[int] = None 
    class Config:
        extra = "forbid"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    phone: Optional[str] = None
    address: Optional[str] = None
    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    id: int
    username: str    
    class Config:
        from_attributes = True