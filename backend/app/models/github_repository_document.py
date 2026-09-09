from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class GitHubRepositoryDocument(Base):
    __tablename__ = "github_repository_documents"

    id = Column(Integer, primary_key=True, index=True)

    github_repository_id = Column(
        Integer,
        ForeignKey("github_repositories.id"),
        nullable=False,
    )

    document_type = Column(
        String(50),
        nullable=False,
    )

    file_name = Column(
        String(255),
        nullable=True,
    )

    path = Column(
        String(500),
        nullable=True,
    )

    content = Column(
        Text,
        nullable=True,
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
        back_populates="documents",
    )