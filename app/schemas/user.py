from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserUpdateVulnerable(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    blocked: Optional[int] = None
    role: Optional[str] = None 

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    blocked: int
    
    class Config:
        from_attributes = True