#To connect python application and database
from sqlalchemy import create_engine 
#Sessionmaker - class , when working with database , we need to create a session to work with database
#Declarative_base - class , to create a base class for all the models
from sqlalchemy.orm import sessionmaker , declarative_base
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(bind = engine , autoflush=False)
Base = declarative_base()