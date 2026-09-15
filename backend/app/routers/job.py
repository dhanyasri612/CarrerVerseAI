from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.core.dependencies import get_current_user, require_recruiter_or_admin
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.services.job_service import (
    create_job,
    get_all_jobs,
    get_job_by_id,
    update_job,
    delete_job,
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job posting (Recruiter/Admin only)"
)
def create_job_endpoint(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter_or_admin)
):
    return create_job(db, job_data)


@router.get(
    "/",
    response_model=List[JobResponse],
    status_code=status.HTTP_200_OK,
    summary="List all available jobs"
)
def get_all_jobs_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_all_jobs(db)


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get job details by ID"
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_job_by_id(db, job_id)


@router.put(
    "/{job_id}",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
    summary="Update job posting (Recruiter/Admin only)"
)
def update_job_endpoint(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter_or_admin)
):
    return update_job(
        db,
        job_id,
        job_data
    )


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete job posting (Recruiter/Admin only)"
)
def delete_job_endpoint(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter_or_admin)
):
    return delete_job(
        db,
        job_id
    )