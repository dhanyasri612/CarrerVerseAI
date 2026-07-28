from sqlalchemy import Column , Integer , String , Boolean , ForeignKey
from sqlalchemy.orm import relationship 
from app.database.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(255),index=True,nullable=False)
    email = Column(String(255),index=True,nullable=False,unique=True)
    hashed_password = Column(String(255),nullable=False)
    is_active = Column(Boolean,default=True)
    role_id = Column(Integer,ForeignKey("roles.id"),nullable=False)
    role = relationship("Role",back_populates="users")
    phone = Column(String(),index=True)