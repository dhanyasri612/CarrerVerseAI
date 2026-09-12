from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.hackerrank_profile import HackerRankProfileResponse
from app.services.hackerrank_service import (
    sync_hackerrank_profile,
    get_hackerrank_profile,
)


router = APIRouter(
    prefix="/hackerrank",
    tags=["HackerRank"],
)


@router.post(
    "/sync/{username}",
    response_model=HackerRankProfileResponse,
)
def sync_profile(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sync_hackerrank_profile(
        db,
        username,
        current_user,
    )


@router.get(
    "/profile",
    response_model=HackerRankProfileResponse,
)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_hackerrank_profile(
        db,
        current_user,
    )
