import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import GITHUB_TOKEN
from app.models.user import User
from app.models.github_profile import GitHubProfile


GITHUB_API_URL = "https://api.github.com"


def fetch_github_profile(
    db: Session,
    username: str,
    current_user: User
):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    # Fetch GitHub user profile
    profile_response = httpx.get(
        f"{GITHUB_API_URL}/users/{username}",
        headers=headers,
        timeout=10.0
    )

    if profile_response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="GitHub user not found"
        )

    if profile_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch GitHub profile"
        )

    profile_data = profile_response.json()

    # Fetch public repositories
    repos_response = httpx.get(
        f"{GITHUB_API_URL}/users/{username}/repos",
        headers=headers,
        params={
            "per_page": 100,
            "sort": "updated"
        },
        timeout=10.0
    )

    if repos_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch GitHub repositories"
        )

    repos_data = repos_response.json()

    repositories = []
    languages = set()
    topics = set()

    total_stars = 0
    total_forks = 0

    for repo in repos_data:
        repository = {
            "name": repo.get("name"),
            "description": repo.get("description"),
            "url": repo.get("html_url"),
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "topics": repo.get("topics", [])
        }

        repositories.append(repository)

        if repo.get("language"):
            languages.add(repo["language"])

        for topic in repo.get("topics", []):
            topics.add(topic)

        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)

    # Check whether GitHub profile already exists
    github_profile = (
        db.query(GitHubProfile)
        .filter(
            GitHubProfile.user_id == current_user.id
        )
        .first()
    )

    if not github_profile:
        github_profile = GitHubProfile(
            user_id=current_user.id,
            username=username
        )
        db.add(github_profile)

    github_profile.username = username
    github_profile.profile_url = profile_data.get("html_url")
    github_profile.repositories = repositories
    github_profile.languages = sorted(languages)
    github_profile.topics = sorted(topics)
    github_profile.total_repositories = len(repositories)
    github_profile.total_stars = total_stars
    github_profile.total_forks = total_forks

    db.commit()
    db.refresh(github_profile)

    return github_profile