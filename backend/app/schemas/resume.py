from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    parsed_status: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime
    content_hash: str | None = None
    parser_version: str | None = None
    parsed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
