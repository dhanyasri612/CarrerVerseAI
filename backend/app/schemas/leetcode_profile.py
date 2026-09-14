from typing import Optional, Any, List, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LeetCodeProfileResponse(BaseModel):
    id: int
    user_id: int
    username: str
    profile_url: Optional[str] = None
    real_name: Optional[str] = None
    about: Optional[str] = None
    avatar_url: Optional[str] = None
    ranking: Optional[int] = None
    reputation: Optional[int] = None

    # Problem statistics
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    acceptance_rate: Optional[float] = None
    total_submissions: Optional[int] = 0

    # Contest statistics
    contest_rating: Optional[float] = None
    contest_ranking: Optional[int] = None
    contest_attended: Optional[int] = 0
    contest_top_percentage: Optional[float] = None
    contest_badge: Optional[str] = None

    # Rich metadata
    badges: Optional[List[Any]] = None
    languages: Optional[List[Any]] = None
    skills: Optional[Dict[str, Any]] = None
    recent_submissions: Optional[List[Any]] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LeetCodeProblemsResponse(BaseModel):
    username: str
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    acceptance_rate: Optional[float] = None
    total_submissions: Optional[int] = 0
    languages: Optional[List[Any]] = None
    skills: Optional[Dict[str, Any]] = None
    recent_submissions: Optional[List[Any]] = None

    model_config = ConfigDict(from_attributes=True)
