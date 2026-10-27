from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.github_profile import GitHubProfileResponse
from app.services.github_service import (
    fetch_github_profile,
    fetch_repository_readme,
    fetch_repository_files,
    fetch_repository_file_content,
)
from app.schemas.github_repository_file import GitHubRepositoryFileResponse
from app.models.github_profile import GitHubProfile
from app.models.github_repository import GitHubRepository
from app.schemas.github_repository import GitHubRepositoryResponse


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
    force: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return fetch_github_profile(
        db,
        username,
        current_user,
        force=force,
    )

@router.get(
    "/repositories",
    response_model=list[GitHubRepositoryResponse]
)
def get_github_repositories(
    limit: int = 1000,
    offset: int = 0,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    github_profile = (
        db.query(GitHubProfile)
        .filter(
            GitHubProfile.user_id == current_user.id
        )
        .first()
    )

    if not github_profile:
        return []

    q = (
        db.query(GitHubRepository)
        .filter(
            GitHubRepository.github_profile_id == github_profile.id
        )
    )
    if search and search.strip():
        q = q.filter(GitHubRepository.name.ilike(f"%{search.strip()}%"))

    return q.order_by(GitHubRepository.name).offset(offset).limit(limit).all()

@router.patch(
    "/repositories/{repository_id}/select",
    response_model=GitHubRepositoryResponse
)
def select_github_repository(
    repository_id: int,
    selected: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    github_profile = (
        db.query(GitHubProfile)
        .filter(
            GitHubProfile.user_id == current_user.id
        )
        .first()
    )

    if not github_profile:
        raise HTTPException(
            status_code=404,
            detail="GitHub profile not found"
        )

    repository = (
        db.query(GitHubRepository)
        .filter(
            GitHubRepository.id == repository_id,
            GitHubRepository.github_profile_id == github_profile.id
        )
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="GitHub repository not found"
        )

    repository.selected_for_analysis = selected

    db.commit()
    db.refresh(repository)
    from app.ai.stores.candidate_store_sync import sync_candidate_ai_stores_safe
    sync_candidate_ai_stores_safe(db, current_user)
    return repository

@router.get(
    "/repositories/{repository_id}/readme"
)
def get_repository_readme(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return fetch_repository_readme(
        db,
        repository_id,
        current_user
    )


@router.get(
    "/repositories/{repository_id}/files",
    response_model=list[GitHubRepositoryFileResponse]
)
def get_repository_files(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return fetch_repository_files(
        db,
        repository_id,
        current_user
    )


@router.get(
    "/files/{file_id}/content",
    response_model=GitHubRepositoryFileResponse
)
def get_repository_file_content(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return fetch_repository_file_content(
        db,
        file_id,
        current_user
    )
