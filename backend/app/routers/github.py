from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.github_profile import GitHubProfileResponse
from app.services.github_service import fetch_github_profile


router = APIRouter(
    prefix="/github",
    tags=["GitHub"]
)


@router.post(
    "/sync/{username}",
    response_model=GitHubProfileResponse
)
def sync_github_profile(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return fetch_github_profile(
        db,
        username,
        current_user
    )