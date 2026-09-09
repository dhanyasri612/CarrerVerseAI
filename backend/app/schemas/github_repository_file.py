from typing import Optional

from pydantic import BaseModel


class GitHubRepositoryFileResponse(BaseModel):
    id: int
    github_repository_id: int
    file_path: str
    file_name: str
    file_type: str
    size: Optional[int] = None
    sha: Optional[str] = None
    download_url: Optional[str] = None
    content: Optional[str] = None
    selected_for_analysis: bool

    class Config:
        from_attributes = True