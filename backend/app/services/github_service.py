import base64
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import GITHUB_TOKEN
from app.models.user import User
from app.models.github_profile import GitHubProfile
from app.models.github_repository import GitHubRepository
from app.models.github_repository_document import GitHubRepositoryDocument
from app.models.github_repository_file import GitHubRepositoryFile


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
        db.flush()

    github_profile.username = username
    github_profile.profile_url = profile_data.get("html_url")
    #github_profile.repositories = repositories
    github_profile.languages = sorted(languages)
    github_profile.topics = sorted(topics)
    github_profile.total_repositories = len(repositories)
    github_profile.total_stars = total_stars
    github_profile.total_forks = total_forks

    # Remove previously stored repository records
    db.query(GitHubRepository).filter(
        GitHubRepository.github_profile_id == github_profile.id
    ).delete()

    # Store repositories as separate records
    for repo in repos_data:
        github_repository = GitHubRepository(
            github_profile_id=github_profile.id,
            github_repo_id=repo.get("id"),
            name=repo.get("name"),
            full_name=repo.get("full_name"),
            description=repo.get("description"),
            url=repo.get("html_url"),
            default_branch=repo.get("default_branch"),
            language=repo.get("language"),
            stars=repo.get("stargazers_count", 0),
            forks=repo.get("forks_count", 0),
            topics=repo.get("topics", []),
            is_fork=repo.get("fork", False),
            is_archived=repo.get("archived", False),
        )

        db.add(github_repository)

    db.commit()
    db.refresh(github_profile)

    return github_profile

def fetch_repository_readme(
    db: Session,
    repository_id: int,
    current_user: User
):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    # Get the stored repository and verify ownership
    repository = (
        db.query(GitHubRepository)
        .join(GitHubProfile)
        .filter(
            GitHubRepository.id == repository_id,
            GitHubProfile.user_id == current_user.id
        )
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="GitHub repository not found"
        )

    # Fetch README from GitHub
    response = httpx.get(
        f"{GITHUB_API_URL}/repos/{repository.full_name}/readme",
        headers=headers,
        timeout=10.0
    )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="README not found"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch repository README"
        )

    readme_data = response.json()

    # GitHub returns README content as Base64
    import base64

    content = base64.b64decode(
        readme_data["content"]
    ).decode("utf-8")

    # Remove previous README
    db.query(GitHubRepositoryDocument).filter(
        GitHubRepositoryDocument.github_repository_id == repository.id,
        GitHubRepositoryDocument.document_type == "README"
    ).delete()

    # Store README
    document = GitHubRepositoryDocument(
        github_repository_id=repository.id,
        document_type="README",
        file_name=readme_data.get("name"),
        path=readme_data.get("path"),
        content=content
    )

    db.add(document)

    db.commit()
    db.refresh(document)

    return document

def fetch_repository_files(
    db: Session,
    repository_id: int,
    current_user: User
):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
    }

    repository = (
        db.query(GitHubRepository)
        .join(GitHubProfile)
        .filter(
            GitHubRepository.id == repository_id,
            GitHubProfile.user_id == current_user.id,
        )
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="GitHub repository not found",
        )

    repository_response = httpx.get(
        f"{GITHUB_API_URL}/repos/{repository.full_name}",
        headers=headers,
        timeout=10.0,
    )

    if repository_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch repository metadata",
        )

    repository_data = repository_response.json()

    tree_sha = repository_data.get("default_branch")

    branch_response = httpx.get(
        f"{GITHUB_API_URL}/repos/{repository.full_name}/branches/{tree_sha}",
        headers=headers,
        timeout=10.0,
    )

    if branch_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch repository branch",
        )

    branch_data = branch_response.json()
    commit_tree_sha = branch_data["commit"]["commit"]["tree"]["sha"]

    tree_response = httpx.get(
        f"{GITHUB_API_URL}/repos/{repository.full_name}/git/trees/{commit_tree_sha}?recursive=1",
        headers=headers,
        timeout=20.0,
    )

    if tree_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch repository file tree",
        )

    tree_data = tree_response.json()

    db.query(GitHubRepositoryFile).filter(
        GitHubRepositoryFile.github_repository_id == repository.id
    ).delete()

    files = []

    for item in tree_data.get("tree", []):
        if item.get("type") != "blob":
            continue

        file_path = item.get("path", "")
        file_name = file_path.split("/")[-1]

        files.append(
            GitHubRepositoryFile(
                github_repository_id=repository.id,
                file_path=file_path,
                file_name=file_name,
                file_type="file",
                size=None,
                sha=item.get("sha"),
                download_url=None,
                content=None,
                selected_for_analysis=False,
            )
        )

    db.add_all(files)
    db.commit()

    return files


def fetch_repository_file_content(
    db: Session,
    file_id: int,
    current_user: User
):
    file_record = (
        db.query(GitHubRepositoryFile)
        .filter(GitHubRepositoryFile.id == file_id)
        .first()
    )

    if not file_record:
        raise HTTPException(
            status_code=404,
            detail="GitHub repository file not found"
        )

    repository = (
        db.query(GitHubRepository)
        .join(GitHubProfile)
        .filter(
            GitHubRepository.id == file_record.github_repository_id,
            GitHubProfile.user_id == current_user.id
        )
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="GitHub repository file not found"
        )

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    url = f"{GITHUB_API_URL}/repos/{repository.full_name}/contents/{file_record.file_path}"

    response = httpx.get(
        url,
        headers=headers,
        timeout=15.0
    )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="GitHub file not found"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch file content from GitHub"
        )

    file_data = response.json()

    if isinstance(file_data, list) or file_data.get("type") != "file":
        raise HTTPException(
            status_code=400,
            detail="Requested path is not a file"
        )

    raw_content = file_data.get("content")
    if raw_content is None:
        raise HTTPException(
            status_code=502,
            detail="GitHub response did not contain file content"
        )

    try:
        decoded_bytes = base64.b64decode(raw_content)
        decoded_text = decoded_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Binary or unsupported file encoding cannot be decoded as source code"
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Failed to decode base64 file content from GitHub"
        )

    file_record.content = decoded_text
    if file_data.get("size") is not None:
        file_record.size = file_data.get("size")
    if file_data.get("sha") is not None:
        file_record.sha = file_data.get("sha")
    if file_data.get("download_url") is not None:
        file_record.download_url = file_data.get("download_url")

    db.commit()
    db.refresh(file_record)

    return file_record