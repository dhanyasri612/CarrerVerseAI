from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.schemas.job import JobCreate, JobResponse , JobUpdate
from app.services.job_service import create_job, get_all_jobs , get_job_by_id , update_job , delete_job


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.post(
    "/",
    response_model=JobResponse
)
def create_job_endpoint(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_job(db, job_data)

@router.get(
    "/",
    response_model=list[JobResponse]
)
def get_all_jobs_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_jobs(db)

@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_job_by_id(db, job_id)

@router.put(
    "/{job_id}",
    response_model=JobResponse
)
def update_job_endpoint(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_job(
        db,
        job_id,
        job_data
    )
    
@router.delete("/{job_id}")
def delete_job_endpoint(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_job(
        db,
        job_id
    )