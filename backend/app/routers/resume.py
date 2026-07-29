from fastapi import APIRouter , Depends , UploadFile , File
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeResponse
from app.services.resume_service import get_resumes , upload_resume , delete_resume , get_resume


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

@router.post(
    "/upload",
    response_model=ResumeResponse
)
def upload_resume_api(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return upload_resume(
        db,
        current_user,
        file
    )
    
@router.get(
    "",
    response_model = List[ResumeResponse]
)
def get_all_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_resumes(db,current_user)


@router.get(
    "/{resume_id}",
    response_model = ResumeResponse
)
def get_resume_by_id(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_resume(db,current_user,resume_id)

@router.delete(
    "/{resume_id}"
)
def delete_resume_by_id(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_resume(db,current_user,resume_id)
    