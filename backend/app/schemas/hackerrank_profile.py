from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel


class HackerRankProfileResponse(BaseModel):
    id: int
    user_id: int
    username: str
    profile_url: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    school: Optional[str] = None

    # Problem solving & achievements
    total_solved: int = 0

    # Rich metadata
    badges: Optional[list[Any]] = None
    certificates: Optional[list[Any]] = None
    skills: Optional[list[Any]] = None
    domain_statistics: Optional[dict[str, Any]] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
