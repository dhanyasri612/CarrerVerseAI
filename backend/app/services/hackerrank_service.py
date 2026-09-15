import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.hackerrank_profile import HackerRankProfile


HACKERRANK_BASE_URL = "https://www.hackerrank.com"


def fetch_hackerrank_data(username: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    # 1. Fetch Profile
    try:
        profile_res = httpx.get(
            f"{HACKERRANK_BASE_URL}/rest/hackers/{username}",
            headers=headers,
            timeout=15.0,
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Failed to connect to HackerRank API",
        )

    if profile_res.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="HackerRank user not found",
        )

    if profile_res.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch profile from HackerRank API",
        )

    try:
        profile_json = profile_res.json()
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Invalid response received from HackerRank API",
        )

    model = profile_json.get("model")
    if not model or model.get("deleted", False):
        raise HTTPException(
            status_code=404,
            detail="HackerRank user not found",
        )

    # 2. Fetch Badges
    badges = []
    try:
        badges_res = httpx.get(
            f"{HACKERRANK_BASE_URL}/rest/hackers/{username}/badges",
            headers=headers,
            timeout=10.0,
        )
        if badges_res.status_code == 200:
            badges = badges_res.json().get("models") or []
    except Exception:
        badges = []

    # 3. Fetch Certificates
    certificates = []
    try:
        certs_res = httpx.get(
            f"{HACKERRANK_BASE_URL}/community/v1/test_results/hacker_certificate?username={username}",
            headers=headers,
            timeout=10.0,
        )
        if certs_res.status_code == 200:
            certs_data = certs_res.json().get("data") or []
            for item in certs_data:
                attr = item.get("attributes") or {}
                cert_info = attr.get("certificate") or {}
                certificates.append({
                    "certificate_name": cert_info.get("label") or attr.get("certificate_name"),
                    "level": cert_info.get("level"),
                    "status": attr.get("status"),
                    "certificate_image": attr.get("certificate_image"),
                    "alloted_at": attr.get("alloted_at"),
                })
    except Exception:
        certificates = []

    # 4. Process Problem Statistics & Skills
    total_solved = sum(b.get("solved", 0) for b in badges if isinstance(b.get("solved"), int))
    domain_statistics = {}
    skills = []

    for b in badges:
        badge_name = b.get("badge_name")
        if not badge_name:
            continue
        stars = b.get("stars", 0)
        points = b.get("current_points", 0.0)
        solved = b.get("solved", 0)
        rank = b.get("hacker_rank")

        domain_statistics[badge_name] = {
            "stars": stars,
            "points": points,
            "solved": solved,
            "rank": rank,
            "category_name": b.get("category_name"),
        }

        if stars > 0 or solved > 0:
            skills.append({
                "name": badge_name,
                "stars": stars,
                "points": points,
                "solved": solved,
            })

    return {
        "username": model.get("username", username),
        "profile_url": f"{HACKERRANK_BASE_URL}/profile/{model.get('username', username)}",
        "display_name": model.get("name"),
        "bio": model.get("short_bio"),
        "avatar_url": model.get("avatar"),
        "country": model.get("country"),
        "school": model.get("school"),
        "total_solved": total_solved,
        "badges": badges,
        "certificates": certificates,
        "skills": skills,
        "domain_statistics": domain_statistics,
    }


def sync_hackerrank_profile(
    db: Session,
    username: str,
    current_user: User,
) -> HackerRankProfile:
    parsed_data = fetch_hackerrank_data(username)

    hackerrank_profile = (
        db.query(HackerRankProfile)
        .filter(HackerRankProfile.user_id == current_user.id)
        .first()
    )

    if not hackerrank_profile:
        hackerrank_profile = HackerRankProfile(
            user_id=current_user.id,
            username=parsed_data["username"],
        )
        db.add(hackerrank_profile)

    hackerrank_profile.username = parsed_data["username"]
    hackerrank_profile.profile_url = parsed_data["profile_url"]
    hackerrank_profile.display_name = parsed_data["display_name"]
    hackerrank_profile.bio = parsed_data["bio"]
    hackerrank_profile.avatar_url = parsed_data["avatar_url"]
    hackerrank_profile.country = parsed_data["country"]
    hackerrank_profile.school = parsed_data["school"]
    hackerrank_profile.total_solved = parsed_data["total_solved"]
    hackerrank_profile.badges = parsed_data["badges"]
    hackerrank_profile.certificates = parsed_data["certificates"]
    hackerrank_profile.skills = parsed_data["skills"]
    hackerrank_profile.domain_statistics = parsed_data["domain_statistics"]

    db.commit()
    db.refresh(hackerrank_profile)

    return hackerrank_profile


def get_hackerrank_profile(
    db: Session,
    current_user: User,
) -> HackerRankProfile:
    hackerrank_profile = (
        db.query(HackerRankProfile)
        .filter(HackerRankProfile.user_id == current_user.id)
        .first()
    )

    if not hackerrank_profile:
        raise HTTPException(
            status_code=404,
            detail="HackerRank profile not found",
        )

    return hackerrank_profile
