import secrets
import time
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode, quote

import httpx
from fastapi import HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core import config
from app.models.user import User
from app.models.linkedin_profile import LinkedInProfile


_active_oauth_states: dict[str, dict] = {}


def _cleanup_expired_states():
    now = time.time()
    expired_nonces = [n for n, s in _active_oauth_states.items() if s["expires_at"] < now]
    for n in expired_nonces:
        _active_oauth_states.pop(n, None)


def generate_linkedin_authorization_url(current_user: User) -> str:
    if not config.LINKEDIN_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="LinkedIn client ID is not configured on the server",
        )

    _cleanup_expired_states()

    nonce = secrets.token_urlsafe(32)
    expires_at = time.time() + 600  # 10 minutes

    _active_oauth_states[nonce] = {
        "user_id": current_user.id,
        "expires_at": expires_at,
    }

    payload = {
        "sub": current_user.email,
        "user_id": current_user.id,
        "nonce": nonce,
        "type": "linkedin_oauth_state",
        "exp": datetime.utcnow() + timedelta(minutes=10),
        "iat": datetime.utcnow(),
    }

    state_token = jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)

    params = {
        "response_type": "code",
        "client_id": config.LINKEDIN_CLIENT_ID,
        "redirect_uri": config.LINKEDIN_REDIRECT_URI,
        "state": state_token,
        "scope": "openid profile email",
    }

    return f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params, quote_via=quote)}"


def validate_and_consume_oauth_state(state: str, db: Session) -> User:
    if not state:
        raise HTTPException(
            status_code=400,
            detail="Missing OAuth state",
        )

    try:
        payload = jwt.decode(state, config.SECRET_KEY, algorithms=[config.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OAuth state",
        )

    if payload.get("type") != "linkedin_oauth_state":
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state type",
        )

    nonce = payload.get("nonce")
    user_id = payload.get("user_id")

    if not nonce or not user_id:
        raise HTTPException(
            status_code=400,
            detail="Malformed OAuth state",
        )

    _cleanup_expired_states()

    state_info = _active_oauth_states.get(nonce)
    if not state_info:
        raise HTTPException(
            status_code=400,
            detail="OAuth state has already been used or is invalid",
        )

    if time.time() > state_info["expires_at"]:
        _active_oauth_states.pop(nonce, None)
        raise HTTPException(
            status_code=400,
            detail="OAuth state has expired",
        )

    if state_info["user_id"] != user_id:
        _active_oauth_states.pop(nonce, None)
        raise HTTPException(
            status_code=400,
            detail="OAuth state user mismatch",
        )

    # Consume state immediately for single-use guarantee
    _active_oauth_states.pop(nonce, None)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User associated with OAuth session not found",
        )

    return user


def exchange_code_for_token(code: str) -> dict:
    if not config.LINKEDIN_CLIENT_ID or not config.LINKEDIN_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="LinkedIn credentials are not configured on the server",
        )

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.LINKEDIN_REDIRECT_URI,
        "client_id": config.LINKEDIN_CLIENT_ID,
        "client_secret": config.LINKEDIN_CLIENT_SECRET,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        response = httpx.post(token_url, data=data, headers=headers, timeout=15.0)
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Failed to connect to LinkedIn OAuth token endpoint",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Failed to exchange authorization code for LinkedIn access token",
        )

    return response.json()


def fetch_linkedin_userinfo(access_token: str) -> dict:
    userinfo_url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    try:
        response = httpx.get(userinfo_url, headers=headers, timeout=15.0)
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Failed to connect to LinkedIn userinfo endpoint",
        )

    if response.status_code == 401:
        raise HTTPException(
            status_code=401,
            detail="LinkedIn access token is invalid or expired",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve LinkedIn user information",
        )

    data = response.json()
    locale = data.get("locale")
    locale_str = None
    if isinstance(locale, dict):
        locale_str = f"{locale.get('language', '')}_{locale.get('country', '')}".strip("_") or None
    elif isinstance(locale, str):
        locale_str = locale

    return {
        "linkedin_id": data.get("sub"),
        "name": data.get("name"),
        "first_name": data.get("given_name"),
        "last_name": data.get("family_name"),
        "email": data.get("email"),
        "email_verified": data.get("email_verified", False),
        "profile_picture": data.get("picture"),
        "locale": locale_str,
    }


def sync_linkedin_profile(
    db: Session,
    user: User,
    linkedin_data: dict,
    access_token: Optional[str] = None,
    expires_in: Optional[int] = None,
) -> LinkedInProfile:
    profile = (
        db.query(LinkedInProfile)
        .filter(LinkedInProfile.user_id == user.id)
        .first()
    )

    if not profile:
        profile = LinkedInProfile(user_id=user.id)
        db.add(profile)

    profile.linkedin_id = linkedin_data.get("linkedin_id")
    profile.name = linkedin_data.get("name")
    profile.first_name = linkedin_data.get("first_name")
    profile.last_name = linkedin_data.get("last_name")
    profile.email = linkedin_data.get("email")
    profile.email_verified = linkedin_data.get("email_verified", False)
    profile.profile_picture = linkedin_data.get("profile_picture")
    profile.locale = linkedin_data.get("locale")

    if access_token:
        profile.access_token = access_token
    if expires_in:
        profile.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    db.commit()
    db.refresh(profile)

    return profile


def get_linkedin_profile(
    db: Session,
    current_user: User,
) -> LinkedInProfile:
    profile = (
        db.query(LinkedInProfile)
        .filter(LinkedInProfile.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="LinkedIn profile not found",
        )

    return profile


def refresh_user_linkedin_data(
    db: Session,
    current_user: User,
) -> LinkedInProfile:
    profile = (
        db.query(LinkedInProfile)
        .filter(LinkedInProfile.user_id == current_user.id)
        .first()
    )

    if not profile or not profile.access_token:
        raise HTTPException(
            status_code=404,
            detail="No connected LinkedIn account found to synchronize",
        )

    if profile.token_expires_at and profile.token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=401,
            detail="LinkedIn access token has expired. Please reauthorize your LinkedIn account.",
        )

    userinfo = fetch_linkedin_userinfo(profile.access_token)
    return sync_linkedin_profile(db, current_user, userinfo)
