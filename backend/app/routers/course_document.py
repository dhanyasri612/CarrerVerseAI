"""
Course Document Router for CareerVerse AI Teaching Room.

Provides authenticated endpoints for uploading, retrieving, listing, searching,
and deleting candidate-uploaded course learning materials.
Strictly scopes all operations to current_user.
"""

from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.course_document import (
    CourseDocumentListResponse,
    CourseDocumentResponse,
    CourseDocumentUploadResponse,
    CourseMaterialSearchResult,
)
from app.services.course_document_service import (
    delete_course_document,
    get_course_document_by_id,
    get_user_course_documents,
    search_course_materials,
    upload_and_ingest_course_document,
)

router = APIRouter(
    prefix="/course-documents",
    tags=["Course Documents"],
)


@router.post(
    "/upload",
    response_model=CourseDocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest course document (PDF, Markdown, TXT)",
)
def upload_course_document_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseDocumentUploadResponse:
    """
    Upload and parse PDF, Markdown, or TXT learning material.
    Extracts text, preserves page/section metadata, indexes in teaching_materials Chroma collection,
    and returns document status.
    """
    doc = upload_and_ingest_course_document(db, current_user, file)
    return CourseDocumentUploadResponse(
        success=True,
        message=f"Document '{doc.original_filename}' uploaded and indexed successfully.",
        document=CourseDocumentResponse.model_validate(doc),
    )


@router.get(
    "",
    response_model=CourseDocumentListResponse,
    summary="List all course documents uploaded by the authenticated user",
)
def list_course_documents_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseDocumentListResponse:
    """Returns all documents uploaded by current_user."""
    docs = get_user_course_documents(db, current_user)
    return CourseDocumentListResponse(
        documents=[CourseDocumentResponse.model_validate(d) for d in docs],
        total_count=len(docs),
    )


@router.get(
    "/search",
    response_model=List[CourseMaterialSearchResult],
    summary="Search candidate's indexed course materials",
)
def search_course_materials_endpoint(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(4, ge=1, le=20, description="Max results"),
    current_user: User = Depends(get_current_user),
) -> List[CourseMaterialSearchResult]:
    """Owner-scoped vector retrieval across teaching materials."""
    return search_course_materials(query=q, user_id=current_user.id, top_k=top_k)


@router.get(
    "/{document_id}",
    response_model=CourseDocumentResponse,
    summary="Get detail and status of a specific course document",
)
def get_course_document_detail_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseDocumentResponse:
    """Retrieves document detail ensuring ownership."""
    doc = get_course_document_by_id(db, current_user, document_id)
    return CourseDocumentResponse.model_validate(doc)


@router.delete(
    "/{document_id}",
    summary="Delete course document, disk file, and indexed vector chunks",
)
def delete_course_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletes course document and all its chunks. Returns confirmation."""
    success = delete_course_document(db, current_user, document_id)
    return {
        "success": success,
        "detail": f"Course document #{document_id} deleted successfully.",
        "id": document_id,
    }
