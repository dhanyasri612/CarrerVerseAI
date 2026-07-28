from typing import Optional
from pydantic import BaseModel , EmailStr

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    
class UserCreate(UserBase):
    password: str   
    role_id: int
    
class UserResponse(UserBase):
    id: int
    is_active: bool
    role_id: int
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
