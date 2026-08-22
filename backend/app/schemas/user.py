from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSyncIn(BaseModel):
    uid: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    photo_url: Optional[str] = None
    phone: Optional[str] = None
    provider_id: Optional[str] = None

class UserOut(BaseModel):
    id: int
    uid: Optional[str]
    email: Optional[EmailStr]
    name: Optional[str]
    photo_url: Optional[str]
    phone: Optional[str]
    provider_id: Optional[str]

    class Config:
        from_attributes = True