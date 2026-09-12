from fastapi import FastAPI
from app.database.database import Base , engine
from app.models.role import Role
from app.models.user import User
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.models.github_profile import GitHubProfile
from app.models.github_repository import GitHubRepository
from app.models.github_repository_document import GitHubRepositoryDocument
from app.models.github_repository_file import GitHubRepositoryFile
from app.models.leetcode_profile import LeetCodeProfile
from app.models.hackerrank_profile import HackerRankProfile
from app.models.linkedin_profile import LinkedInProfile
from app.models.certification import Certification

from app.routers import profile , resume , parser , job , skill_gap , recommendation , resume_improvement , career_roadmap , candidate_profile , github , leetcode , hackerrank , linkedin , certification
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
app.include_router(leetcode.router)
app.include_router(hackerrank.router)
app.include_router(linkedin.router)
app.include_router(certification.router)



@app.get("/")
def read_root():
    return {"message": "CarrerVerseAI API"}