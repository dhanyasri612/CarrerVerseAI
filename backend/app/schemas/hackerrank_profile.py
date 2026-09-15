from typing import Optional, Any, List, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict


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
    badges: Optional[List[Any]] = None
    certificates: Optional[List[Any]] = None
    skills: Optional[List[Any]] = None
    domain_statistics: Optional[Dict[str, Any]] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
