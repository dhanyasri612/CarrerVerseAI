from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.leetcode_profile import (
    LeetCodeProfileResponse,
    LeetCodeProblemsResponse,
)
from app.services.leetcode_service import (
    sync_leetcode_profile,
    get_leetcode_profile,
    get_leetcode_problems,
)


router = APIRouter(
    prefix="/leetcode",
    tags=["LeetCode"],
)


@router.post(
    "/sync/{username}",
    response_model=LeetCodeProfileResponse,
)
def sync_profile(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sync_leetcode_profile(
        db,
        username,
        current_user,
    )


@router.get(
    "/profile",
    response_model=LeetCodeProfileResponse,
)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_leetcode_profile(
        db,
        current_user,
    )


@router.get(
    "/problems",
    response_model=LeetCodeProblemsResponse,
)
def get_problems(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_leetcode_problems(
        db,
        current_user,
    )
