from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CourseDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    filename: str
    original_filename: str
    file_type: str
    mime_type: str
    file_size: int
    content_hash: str
    status: str
    error_message: Optional[str] = None
    total_pages: Optional[int] = None
    total_chunks: int = 0
    created_at: datetime
    updated_at: datetime


class CourseDocumentListResponse(BaseModel):
    documents: List[CourseDocumentResponse]
    total_count: int


class CourseDocumentUploadResponse(BaseModel):
    success: bool
    message: str
    document: CourseDocumentResponse


class CourseMaterialSearchResult(BaseModel):
    document_id: int
    filename: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    similarity_score: float
    excerpt: str
    chunk_index: int = 0
