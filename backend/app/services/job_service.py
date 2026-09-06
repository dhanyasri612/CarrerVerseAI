from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import JobCreate , JobUpdate


def create_job(
    db: Session,
    job_data: JobCreate
):
    job = Job(
        title=job_data.title,
        company=job_data.company,
        description=job_data.description,
        required_skills=job_data.required_skills,
        location=job_data.location,
        salary=job_data.salary,
        experience=job_data.experience
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job

def get_all_jobs(db: Session):
    return db.query(Job).all()

def get_job_by_id(
    db: Session,
    job_id: int
):
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job

def update_job(
    db: Session,
    job_id: int,
    job_data: JobUpdate
):
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    update_data = job_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    return job

def delete_job(
    db: Session,
    job_id: int
):
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    db.delete(job)
    db.commit()

    return {
        "message": "Job deleted successfully"
    }