from pydantic import BaseModel , EmailStr
from typing import Optional
from datetime import datetime

class ProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    role_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = None
    location: Optional[str] = None
    bio: Optional[str] = None