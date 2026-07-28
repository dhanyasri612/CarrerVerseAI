from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate , UserLogin
from app.utils.security import hash_password , verify_password
from app.utils.jwt import create_access_token


def register_user(db: Session , user: UserCreate):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError("Email already registered")
    hashed_password = hash_password(user.password)
    db_user = User(name=user.name,email=user.email,hashed_password=hashed_password,role_id=user.role_id,phone=user.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def login_user(db: Session , user: UserLogin):
    db_user = db.query(User).filter(User.email == user.email).first()
    print(db_user)
    if not db_user:
        raise ValueError("Invalid email or password")
    if not verify_password(user.password, db_user.hashed_password):
        raise ValueError("Invalid email or password")
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}