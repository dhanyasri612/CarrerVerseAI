from fastapi import APIRouter , Depends
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserResponse , UserLogin , Token
from app.services.auth_service import register_user , login_user
from app.database.database import sessionLocal
from app.core.dependencies import get_current_user
from app.models.user import User
from app.database.session import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

        
@router.post("/register",response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user)

@router.post("/login",response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user)

@router.get("/me",response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user