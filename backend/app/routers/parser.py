from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.parsed_resume import ParsedResume
from app.services.parser_service import (
    parse_resume_by_id,
    get_parsed_resume_by_id,
    delete_parsed_resume,
    reparse_resume,
)

router = APIRouter(
    prefix="/parser",
    tags=["Resume Parser"]
)


@router.post(
    "/resume/{resume_id}",
    response_model=ParsedResume,
    status_code=status.HTTP_200_OK,
    summary="Parse an uploaded resume"
)
@router.post(
    "/parse/{resume_id}",
    response_model=ParsedResume,
    status_code=status.HTTP_200_OK,
    summary="Parse an uploaded resume (alias)"
)
def parse_uploaded_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return parse_resume_by_id(db, resume_id, current_user)


@router.get(
    "/resume/{resume_id}",
    response_model=ParsedResume,
    status_code=status.HTTP_200_OK,
    summary="Get parsed resume details by resume ID"
)
def get_parsed_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_parsed_resume_by_id(db, resume_id, current_user)


@router.delete(
    "/resume/{resume_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete parsed resume by resume ID"
)
def delete_parsed_resume_endpoint(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_parsed_resume(
        db,
        resume_id,
        current_user
    )


@router.post(
    "/resume/{resume_id}/reparse",
    response_model=ParsedResume,
    status_code=status.HTTP_200_OK,
    summary="Reparse an existing resume"
)
@router.post(
    "/reparse/{resume_id}",
    response_model=ParsedResume,
    status_code=status.HTTP_200_OK,
    summary="Reparse an existing resume (alias)"
)
def reparse_resume_endpoint(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return reparse_resume(
        db,
        resume_id,
        current_user
    )