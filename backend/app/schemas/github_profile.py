from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class GitHubProfileResponse(BaseModel):
    id: int
    user_id: int
    username: str
    profile_url: Optional[str] = None

    repositories: Optional[List[Dict[str, Any]]] = None
    languages: Optional[List[str]] = None
    topics: Optional[List[str]] = None

    total_repositories: int
    total_stars: int
    total_forks: int

    class Config:
        from_attributes = True