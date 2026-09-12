from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class LinkedInProfileResponse(BaseModel):
    id: int
    user_id: int
    linkedin_id: Optional[str] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = False
    profile_picture: Optional[str] = None
    locale: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LinkedInAuthUrlResponse(BaseModel):
    authorization_url: str
