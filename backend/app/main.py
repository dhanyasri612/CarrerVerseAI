from fastapi import FastAPI
from app.database.database import Base , engine
from app.models.role import Role
from app.models.user import User

from app.routers import auth

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "CarrerVerseAI API"}