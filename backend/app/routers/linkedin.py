from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.linkedin_profile import (
    LinkedInProfileResponse,
    LinkedInAuthUrlResponse,
)
from app.services.linkedin_service import (
    generate_linkedin_authorization_url,
    validate_and_consume_oauth_state,
    exchange_code_for_token,
    fetch_linkedin_userinfo,
    sync_linkedin_profile,
    get_linkedin_profile,
    refresh_user_linkedin_data,
)


router = APIRouter(
    prefix="/linkedin",
    tags=["LinkedIn"],
)


@router.get(
    "/login",
    response_model=LinkedInAuthUrlResponse,
)
def linkedin_login(
    current_user: User = Depends(get_current_user),
):
    auth_url = generate_linkedin_authorization_url(current_user)
    return {"authorization_url": auth_url}


@router.get(
    "/callback",
    response_model=LinkedInProfileResponse,
)
def linkedin_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    if error:
        detail_msg = error_description or f"LinkedIn authorization failed: {error}"
        raise HTTPException(
            status_code=400,
            detail=detail_msg,
        )

    if not code or not state:
        raise HTTPException(
            status_code=400,
            detail="Missing code or state parameter in authorization callback",
        )

    # 1. Cryptographically validate state and identify the initiating CareerVerse user
    user = validate_and_consume_oauth_state(state, db)

    # 2. Exchange authorization code for LinkedIn access token
    token_data = exchange_code_for_token(code)
    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in")

    if not access_token:
        raise HTTPException(
            status_code=502,
            detail="Failed to obtain access token from LinkedIn",
        )

    # 3. Fetch user profile info from official LinkedIn userinfo endpoint
    userinfo = fetch_linkedin_userinfo(access_token)

    # 4. Upsert LinkedInProfile in PostgreSQL
    profile = sync_linkedin_profile(
        db=db,
        user=user,
        linkedin_data=userinfo,
        access_token=access_token,
        expires_in=expires_in,
    )

    return profile


@router.get(
    "/profile",
    response_model=LinkedInProfileResponse,
)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_linkedin_profile(
        db,
        current_user,
    )


@router.post(
    "/sync",
    response_model=LinkedInProfileResponse,
)
def sync_connected_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return refresh_user_linkedin_data(
        db,
        current_user,
    )
