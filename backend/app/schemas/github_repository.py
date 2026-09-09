from typing import List, Optional
from pydantic import BaseModel


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

    class Config:
        from_attributes = True