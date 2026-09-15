from fastapi import APIRouter, Depends, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Union

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.certification import (
    CertificationCreate,
    CertificationUpdate,
    CertificationResponse,
    CertificationExtractResponse,
    GoogleDriveImportRequest,
    GoogleDriveFolderImportRequest,
    GoogleDriveFolderImportResponse,
    PlatformCredentialSyncRequest,
    VerifyCredentialRequest,
    VerificationResultResponse,
)
from app.services import certification_service

router = APIRouter(
    prefix="/certifications",
    tags=["Certifications"]
)


@router.post(
    "",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create or manually add a certification (with deduplication merge)"
)
def create_certification_api(
    cert_in: CertificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return certification_service.create_certification(db, cert_in, current_user)


@router.get(
    "",
    response_model=List[CertificationResponse],
    summary="List all candidate certifications with optional filtering and search"
)
def list_certifications_api(
    source: Optional[str] = Query(None, description="Filter by source: MANUAL, RESUME, FILE_UPLOAD, GOOGLE_DRIVE, PLATFORM_SYNC"),
    verification_status: Optional[str] = Query(None, description="Filter by status: UNVERIFIED, VERIFICATION_PENDING, VERIFIED, FAILED"),
    search: Optional[str] = Query(None, description="Search query across certification name, issuer, or credential ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return certification_service.list_certifications(
        db=db,
        current_user=current_user,
        source=source,
        status=verification_status,
        search=search
    )


@router.get(
    "/{cert_id}",
    response_model=CertificationResponse,
    summary="Get single certification details by ID"
)
def get_certification_api(
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return certification_service.get_certification_by_id(db, cert_id, current_user)


@router.put(
    "/{cert_id}",
    response_model=CertificationResponse,
    summary="Update certification details"
)
def update_certification_api(
    cert_id: int,
    cert_in: CertificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return certification_service.update_certification(db, cert_id, cert_in, current_user)


@router.delete(
    "/{cert_id}",
    summary="Delete certification and associated file"
)
def delete_certification_api(
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return certification_service.delete_certification(db, cert_id, current_user)


@router.post(
    "/upload",
    summary="Upload PDF or image certificate (preview or auto-save)",
    response_model=Union[CertificationResponse, CertificationExtractResponse]
)
def upload_certificate_api(
    file: UploadFile = File(...),
    auto_save: bool = Query(True, description="Set to false to preview extracted fields before saving"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return certification_service.upload_and_process_certificate(
        db=db,
        file=file,
        current_user=current_user,
        auto_save=auto_save
    )


@router.post(
    "/preview-file",
    response_model=CertificationExtractResponse,
    summary="Upload certificate PDF or image to extract and preview fields without saving"
)
def preview_certificate_file_api(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_bytes = file.file.read()
    return certification_service.preview_uploaded_file(
        db=db,
        file_bytes=file_bytes,
        filename=file.filename or "certificate.pdf",
        current_user=current_user
    )


@router.post(
    "/extract-from-resume/{resume_id}",
    summary="Extract certifications from an uploaded resume",
    response_model=List[Union[CertificationResponse, CertificationExtractResponse]]
)
def extract_from_resume_api(
    resume_id: int,
    auto_save: bool = Query(False, description="Set to true to directly save extracted certifications to database"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return certification_service.extract_certifications_from_user_resume(
        db=db,
        resume_id=resume_id,
        current_user=current_user,
        auto_save=auto_save
    )


@router.post(
    "/google-drive/import",
    summary="Import certificate directly from Google Drive stream using ephemeral OAuth token",
    response_model=Union[CertificationResponse, CertificationExtractResponse]
)
async def import_from_google_drive_api(
    req: GoogleDriveImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await certification_service.import_from_google_drive(
        db=db,
        req=req,
        current_user=current_user
    )


@router.post(
    "/google-drive/import-folder",
    summary="Bulk import and extract all certificate files from a Google Drive folder",
    response_model=GoogleDriveFolderImportResponse
)
async def import_folder_from_google_drive_api(
    req: GoogleDriveFolderImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await certification_service.import_folder_from_google_drive(
        db=db,
        req=req,
        current_user=current_user
    )



@router.post(
    "/platform-sync",
    summary="Sync or extract certification via platform verification link / credential ID",
    response_model=Union[CertificationResponse, CertificationExtractResponse]
)
def sync_platform_credential_api(
    req: PlatformCredentialSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return certification_service.sync_platform_credential(
        db=db,
        req=req,
        current_user=current_user
    )


@router.post(
    "/{cert_id}/verify",
    response_model=VerificationResultResponse,
    summary="Execute live verification probe on certificate credential URL"
)
async def verify_certification_api(
    cert_id: int,
    req: Optional[VerifyCredentialRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await certification_service.verify_certification_credential(
        db=db,
        cert_id=cert_id,
        req=req,
        current_user=current_user
    )
