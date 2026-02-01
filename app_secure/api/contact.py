from fastapi import APIRouter, Depends, HTTPException, status
from app_secure.core.security import get_current_user
from pydantic import BaseModel
from typing import List
from app_secure.models.user import User

router = APIRouter()
contact_messages_db = []

class ContactMessage(BaseModel):
    email: str
    content: str

#endpoint public, tout le monde peut poster, pas besoin de token
@router.post("/contact", tags=["Public"])
def send_contact_message(msg: ContactMessage):
    contact_messages_db.append(msg)
    return {"status": "Message sent successfully"}

