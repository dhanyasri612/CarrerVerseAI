from fastapi import APIRouter , Depends
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserResponse , UserLogin , Token
from app.services.auth_service import register_user , login_user
from app.database.database import sessionLocal

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/register",response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user)

@router.post("/login",response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user)