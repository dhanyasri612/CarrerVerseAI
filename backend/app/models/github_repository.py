from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    JSON,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base
from app.models.github_repository_document import GitHubRepositoryDocument
from app.models.github_repository_file import GitHubRepositoryFile

class GitHubRepository(Base):
    __tablename__ = "github_repositories"

    id = Column(Integer, primary_key=True, index=True)

    github_profile_id = Column(
        Integer,
        ForeignKey("github_profiles.id"),
        nullable=False,
    )

    github_repo_id = Column(Integer, nullable=False)

    name = Column(String(255), nullable=False)

    full_name = Column(String(500), nullable=True)

    description = Column(String, nullable=True)

    url = Column(String(500), nullable=True)

    default_branch = Column(String(255), nullable=True)

    language = Column(String(100), nullable=True)

    stars = Column(Integer, default=0)

    forks = Column(Integer, default=0)

    topics = Column(JSON, nullable=True)

    is_fork = Column(Boolean, default=False)

    is_archived = Column(Boolean, default=False)

    selected_for_analysis = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    github_profile = relationship(
        "GitHubProfile",
        back_populates="repositories",
    )

    documents = relationship(
    "GitHubRepositoryDocument",
    back_populates="github_repository",
    cascade="all, delete-orphan",
    )

    files = relationship(
    "GitHubRepositoryFile",
    back_populates="github_repository",
    cascade="all, delete-orphan",
    )