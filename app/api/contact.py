from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from pydantic import BaseModel
from typing import List
from app.models.user import User

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

#seul admin peut lire les messages
@router.get("/admin/messages", response_model=List[ContactMessage], tags=["Admin"])
def read_all_messages(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to administrators."
        )
    return contact_messages_db