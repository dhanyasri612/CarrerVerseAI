from fastapi import FastAPI
from app.database.database import Base , engine
from app.models.role import Role
from app.models.user import User
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.models.github_profile import GitHubProfile

from app.routers import profile , resume , parser , job , skill_gap , recommendation , resume_improvement , career_roadmap , candidate_profile , github
from app.routers import auth

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(resume.router)
app.include_router(parser.router)
app.include_router(job.router)
app.include_router(skill_gap.router)
app.include_router(recommendation.router)
app.include_router(resume_improvement.router)
app.include_router(career_roadmap.router)
app.include_router(candidate_profile.router)
app.include_router(github.router)



@app.get("/")
def read_root():
    return {"message": "CarrerVerseAI API"}