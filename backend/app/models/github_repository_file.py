from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class GitHubRepositoryFile(Base):
    __tablename__ = "github_repository_files"

    id = Column(Integer, primary_key=True, index=True)

    github_repository_id = Column(
        Integer,
        ForeignKey("github_repositories.id"),
        nullable=False,
    )

    file_path = Column(
        String(1000),
        nullable=False,
    )

    file_name = Column(
        String(255),
        nullable=False,
    )

    file_type = Column(
        String(50),
        nullable=False,
    )

    size = Column(
        Integer,
        nullable=True,
    )

    sha = Column(
        String(100),
        nullable=True,
    )

    download_url = Column(
        String(1000),
        nullable=True,
    )

    content = Column(
        Text,
        nullable=True,
    )

    selected_for_analysis = Column(
        Boolean,
        default=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    github_repository = relationship(
        "GitHubRepository",
        back_populates="files",
    )