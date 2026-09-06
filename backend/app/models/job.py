from sqlalchemy import Column, Integer, String, Text, JSON
from app.database.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    company = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    required_skills = Column(JSON, nullable=True)

    location = Column(String, nullable=True)

    salary = Column(String, nullable=True)

    experience = Column(String, nullable=True)