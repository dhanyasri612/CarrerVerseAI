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
