from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class GitHubRepositoryResponse(BaseModel):
    id: int
    github_profile_id: int
    github_repo_id: int
    name: str
    full_name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    default_branch: Optional[str] = None
    language: Optional[str] = None
    stars: int
    forks: int
    topics: Optional[List[str]] = None
    is_fork: bool
    is_archived: bool
    selected_for_analysis: bool

    model_config = ConfigDict(from_attributes=True)


class GitHubProfileResponse(BaseModel):
    id: int
    user_id: int
    username: str
    profile_url: Optional[str] = None
    repositories: Optional[List[GitHubRepositoryResponse]] = None
    languages: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    total_repositories: int
    total_stars: int
    total_forks: int

    model_config = ConfigDict(from_attributes=True)