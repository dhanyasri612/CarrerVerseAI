# To connect the Python application and database
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import DATABASE_URL

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
sessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


def ensure_resume_cache_columns() -> None:
    """Add resume cache metadata to databases created before the cache existed.

    The project currently relies on ``create_all`` rather than a migration
    runner. Keep this migration deliberately narrow and additive so existing
    resume records remain untouched while new deployments and upgraded
    databases get the cache columns required by the parser service.
    """
    inspector = inspect(engine)
    if "resumes" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("resumes")}
    missing_columns = {
        "content_hash": "VARCHAR(64)",
        "parser_version": "VARCHAR(64)",
        "parsed_at": "TIMESTAMP",
    }

    with engine.begin() as connection:
        for column_name, column_type in missing_columns.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(f"ALTER TABLE resumes ADD COLUMN {column_name} {column_type}")
                )


def ensure_course_document_table() -> None:
    """Ensure the course_documents table exists safely without touching existing database tables."""
    from app.models.course_document import CourseDocument
    inspector = inspect(engine)
    if "course_documents" not in inspector.get_table_names():
        CourseDocument.__table__.create(bind=engine, checkfirst=True)


def ensure_proctoring_table() -> None:
    """Ensure the proctoring_events table exists safely without touching existing database tables."""
    from app.models.proctoring_event import ProctoringEvent
    inspector = inspect(engine)
    if "proctoring_events" not in inspector.get_table_names():
        ProctoringEvent.__table__.create(bind=engine, checkfirst=True)


def ensure_roadmap_tables() -> None:
    """Ensure the career roadmap tables and columns exist safely without touching existing database tables."""
    from app.models.career_roadmap import (
        CareerRoadmap,
        RoadmapVersion,
        RoadmapMilestone,
        RoadmapTrendSignal,
        RoadmapChangeLog,
    )
    inspector = inspect(engine)
    existing = set(inspector.get_table_names())
    for model in [CareerRoadmap, RoadmapVersion, RoadmapMilestone, RoadmapTrendSignal, RoadmapChangeLog]:
        if model.__tablename__ not in existing:
            model.__table__.create(bind=engine, checkfirst=True)

    if "career_roadmaps" in existing:
        existing_cols = {c["name"] for c in inspector.get_columns("career_roadmaps")}
        missing_columns = {
            "experience_level": "VARCHAR(50) DEFAULT 'intermediate'",
            "readiness_score": "INTEGER DEFAULT 0",
            "current_version": "INTEGER DEFAULT 1",
            "total_milestones": "INTEGER DEFAULT 0",
            "completed_milestones": "INTEGER DEFAULT 0",
            "last_reviewed_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
        }
        with engine.begin() as conn:
            for col_name, col_type in missing_columns.items():
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE career_roadmaps ADD COLUMN {col_name} {col_type}"))
            # Make sure legacy non-null columns do not fail constraints
            legacy_non_nulls = [
                "experience_level",
                "version",
                "roadmap_data",
                "completed_node_ids",
                "customizations",
                "change_log",
                "version_history",
                "research_sources",
                "last_verified_at",
            ]
            for col in legacy_non_nulls:
                if col in existing_cols:
                    try:
                        conn.execute(text(f"ALTER TABLE career_roadmaps ALTER COLUMN {col} DROP NOT NULL"))
                    except Exception:
                        pass
            # Set defaults for created_at and updated_at
            try:
                conn.execute(text("ALTER TABLE career_roadmaps ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP"))
                conn.execute(text("ALTER TABLE career_roadmaps ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP"))
            except Exception:
                pass


