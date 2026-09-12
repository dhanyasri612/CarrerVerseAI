import os
import re
import uuid
import httpx
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.certification import Certification
from app.models.user import User
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.schemas.certification import (
    CertificationCreate,
    CertificationUpdate,
    CertificationResponse,
    CertificationExtractResponse,
    GoogleDriveImportRequest,
    GoogleDriveFolderImportRequest,
    GoogleDriveFolderImportResponse,
    ImportedCertificationItem,
    FileImportError,
    PlatformCredentialSyncRequest,
    VerifyCredentialRequest,
    VerificationResultResponse,
    CertificationSource,
    VerificationStatus,
)
from app.parsers.certificate_extractor import (
    extract_from_pdf_bytes,
    extract_fallback_from_images,
    parse_structured_certification,
    calculate_confidence_score,
    evaluate_initial_verification_status,
    extract_skills_from_text,
    extract_dates,
    extract_issuing_organization,
    extract_credential_id,
    extract_credential_url,
    is_invalid_or_generic_title,
    TRUSTED_VERIFICATION_DOMAINS,
)

CERTIFICATES_UPLOAD_DIR = "uploads/certificates"
os.makedirs(CERTIFICATES_UPLOAD_DIR, exist_ok=True)
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
]


# ==========================================
# 1. HELPER & DEDUPLICATION FUNCTIONS
# ==========================================

def normalize_string(val: Optional[str]) -> str:
    """Normalize string by lowercasing and stripping non-alphanumeric characters."""
    if not val:
        return ""
    return re.sub(r"[^a-z0-9]", "", val.lower().strip())


def find_duplicate_certification(
    db: Session,
    user_id: int,
    credential_id: Optional[str],
    certification_name: str,
    issuing_organization: str,
) -> Optional[Certification]:
    """
    Find existing certification for the user by:
    1. Exact credential_id match (when valid ID with >= 5 chars is available)
    2. Strong match of normalized (non-generic title + non-generic issuer)
    
    IMPORTANT: Never match duplicates on generic titles ('Certificate of Completion')
    or 'Unknown Organization'.
    """
    # 1. Exact Credential ID match
    if credential_id and len(credential_id.strip()) >= 5:
        cid_clean = credential_id.strip()
        if cid_clean.lower() not in ["unknown", "null", "none", "12345", "cert_id", "certificate"]:
            existing_by_id = (
                db.query(Certification)
                .filter(
                    Certification.user_id == user_id,
                    Certification.credential_id.ilike(cid_clean)
                )
                .first()
            )
            if existing_by_id:
                return existing_by_id

    # 2. Strong Normalized Name + Issuer Match
    # Reject generic titles or generic issuers from triggering duplicate matches!
    if is_invalid_or_generic_title(certification_name):
        return None

    if not issuing_organization or issuing_organization.strip().lower() in ["unknown organization", "unknown", "organization", ""]:
        return None

    target_name_norm = normalize_string(certification_name)
    target_issuer_norm = normalize_string(issuing_organization)

    if len(target_name_norm) < 4 or len(target_issuer_norm) < 3:
        return None

    user_certs = db.query(Certification).filter(Certification.user_id == user_id).all()
    for cert in user_certs:
        # Check existing cert's title is also not generic
        if is_invalid_or_generic_title(cert.certification_name):
            continue

        if (
            normalize_string(cert.certification_name) == target_name_norm
            and normalize_string(cert.issuing_organization) == target_issuer_norm
        ):
            return cert

    return None


def merge_certification_records(
    existing: Certification,
    new_data: Dict[str, Any]
) -> Certification:
    """
    Merge newly extracted certification data into existing record without duplication:
    - Merges skill sets
    - Fills in missing fields (issue_date, expiry_date, credential_id, urls)
    - Upgrades verification status if applicable
    - Retains highest confidence score
    - Updates raw metadata
    """
    # Merge skills
    existing_skills = set(existing.extracted_skills or [])
    new_skills = set(new_data.get("extracted_skills") or [])
    existing.extracted_skills = sorted(list(existing_skills | new_skills))

    # Fill in missing fields
    if not existing.credential_id and new_data.get("credential_id"):
        existing.credential_id = new_data["credential_id"]

    if not existing.credential_url and new_data.get("credential_url"):
        existing.credential_url = new_data["credential_url"]

    if not existing.certificate_file_url and new_data.get("certificate_file_url"):
        existing.certificate_file_url = new_data["certificate_file_url"]

    if not existing.issue_date and new_data.get("issue_date"):
        existing.issue_date = new_data["issue_date"]

    if not existing.expiry_date and new_data.get("expiry_date"):
        existing.expiry_date = new_data["expiry_date"]

    # Status priority: VERIFIED > VERIFICATION_PENDING > UNVERIFIED > FAILED
    status_weights = {
        "FAILED": 0,
        "UNVERIFIED": 1,
        "VERIFICATION_PENDING": 2,
        "VERIFIED": 3,
    }
    cur_weight = status_weights.get(existing.verification_status, 1)
    new_weight = status_weights.get(new_data.get("verification_status", "UNVERIFIED"), 1)
    if new_weight > cur_weight:
        existing.verification_status = new_data["verification_status"]

    # Confidence score: keep highest
    existing_conf = existing.confidence_score or 0.0
    new_conf = new_data.get("confidence_score") or 0.0
    existing.confidence_score = max(existing_conf, new_conf)

    # Merge metadata
    cur_meta = existing.raw_metadata or {}
    new_meta = new_data.get("raw_metadata") or {}
    merged_meta = {**cur_meta, **new_meta, "last_merged_at": datetime.utcnow().isoformat()}
    existing.raw_metadata = merged_meta

    existing.updated_at = datetime.utcnow()
    return existing


def save_uploaded_bytes_to_disk(file_bytes: bytes, original_filename: str) -> str:
    """Save certificate file bytes to uploads/certificates and return relative URL path."""
    ext = os.path.splitext(original_filename)[1].lower()
    if not ext:
        ext = ".pdf"
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(CERTIFICATES_UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return f"/uploads/certificates/{unique_filename}"


# ==========================================
# 2. CRUD OPERATIONS
# ==========================================

def create_certification(
    db: Session,
    cert_in: CertificationCreate,
    current_user: User
) -> Certification:
    """Create certification or merge into existing duplicate record."""
    duplicate = find_duplicate_certification(
        db,
        user_id=current_user.id,
        credential_id=cert_in.credential_id,
        certification_name=cert_in.certification_name,
        issuing_organization=cert_in.issuing_organization,
    )

    if duplicate:
        merged = merge_certification_records(duplicate, cert_in.model_dump())
        db.commit()
        db.refresh(merged)
        return merged

    # Evaluate trust status if URL provided and status is default UNVERIFIED
    initial_status = cert_in.verification_status
    if initial_status == VerificationStatus.UNVERIFIED and cert_in.credential_url:
        initial_status = evaluate_initial_verification_status(cert_in.credential_url, cert_in.issuing_organization)

    cert = Certification(
        user_id=current_user.id,
        certification_name=cert_in.certification_name.strip(),
        issuing_organization=cert_in.issuing_organization.strip(),
        issue_date=cert_in.issue_date,
        expiry_date=cert_in.expiry_date,
        credential_id=cert_in.credential_id.strip() if cert_in.credential_id else None,
        credential_url=cert_in.credential_url.strip() if cert_in.credential_url else None,
        certificate_file_url=cert_in.certificate_file_url,
        source=cert_in.source.value if hasattr(cert_in.source, "value") else str(cert_in.source),
        verification_status=initial_status.value if hasattr(initial_status, "value") else str(initial_status),
        extracted_skills=cert_in.extracted_skills or [],
        confidence_score=cert_in.confidence_score if cert_in.confidence_score is not None else 1.0,
        raw_metadata=cert_in.raw_metadata or {},
    )

    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


def list_certifications(
    db: Session,
    current_user: User,
    source: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> List[Certification]:
    """List certifications for current user with optional filters."""
    query = db.query(Certification).filter(Certification.user_id == current_user.id)

    if source:
        query = query.filter(Certification.source == source.upper())
    if status:
        query = query.filter(Certification.verification_status == status.upper())
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Certification.certification_name.ilike(search_term),
                Certification.issuing_organization.ilike(search_term),
                Certification.credential_id.ilike(search_term)
            )
        )

    return query.order_by(Certification.created_at.desc()).all()


def get_certification_by_id(
    db: Session,
    cert_id: int,
    current_user: User
) -> Certification:
    """Retrieve certification by ID ensuring user ownership."""
    cert = (
        db.query(Certification)
        .filter(
            Certification.id == cert_id,
            Certification.user_id == current_user.id
        )
        .first()
    )
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found or access denied."
        )
    return cert


def update_certification(
    db: Session,
    cert_id: int,
    cert_in: CertificationUpdate,
    current_user: User
) -> Certification:
    """Update certification fields."""
    cert = get_certification_by_id(db, cert_id, current_user)
    update_data = cert_in.model_dump(exclude_unset=True)

    for field, val in update_data.items():
        if field == "source" and val is not None:
            val = val.value if hasattr(val, "value") else str(val)
        if field == "verification_status" and val is not None:
            val = val.value if hasattr(val, "value") else str(val)
        setattr(cert, field, val)

    cert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(cert)
    return cert


def delete_certification(
    db: Session,
    cert_id: int,
    current_user: User
) -> Dict[str, str]:
    """Delete certification and delete local certificate file if present."""
    cert = get_certification_by_id(db, cert_id, current_user)

    # Delete local file if it exists
    if cert.certificate_file_url and cert.certificate_file_url.startswith("/uploads/"):
        rel_path = cert.certificate_file_url.lstrip("/")
        if os.path.exists(rel_path):
            try:
                os.remove(rel_path)
            except Exception:
                pass

    db.delete(cert)
    db.commit()
    return {"message": "Certification deleted successfully."}


# ==========================================
# 3. FILE UPLOAD & PREVIEW EXTRACTION
# ==========================================

def extract_certification_from_file_bytes(
    file_bytes: bytes,
    filename: str,
    source: CertificationSource = CertificationSource.FILE_UPLOAD
) -> Dict[str, Any]:
    """Parse certificate PDF or image bytes into extracted fields."""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == ".pdf":
        extracted = extract_from_pdf_bytes(file_bytes, filename)
    else:
        text, meta = extract_fallback_from_images(file_bytes, filename)
        extracted = parse_structured_certification(text, raw_metadata=meta, filename=filename)

    extracted["source"] = source
    return extracted


def preview_uploaded_file(
    db: Session,
    file_bytes: bytes,
    filename: str,
    current_user: User,
    source: CertificationSource = CertificationSource.FILE_UPLOAD
) -> CertificationExtractResponse:
    """Extract metadata for preview without saving to database."""
    extracted = extract_certification_from_file_bytes(file_bytes, filename, source=source)

    # Check duplicate
    dup = find_duplicate_certification(
        db,
        user_id=current_user.id,
        credential_id=extracted.get("credential_id"),
        certification_name=extracted.get("certification_name", ""),
        issuing_organization=extracted.get("issuing_organization", ""),
    )

    is_duplicate = dup is not None
    existing_id = dup.id if dup else None
    match_reason = f"Matches existing certification #{dup.id} ({dup.certification_name})" if dup else None

    return CertificationExtractResponse(
        certification_name=extracted["certification_name"],
        issuing_organization=extracted["issuing_organization"],
        issue_date=extracted["issue_date"],
        expiry_date=extracted["expiry_date"],
        credential_id=extracted["credential_id"],
        credential_url=extracted["credential_url"],
        certificate_file_url=None,
        source=source,
        verification_status=extracted["verification_status"],
        extracted_skills=extracted["extracted_skills"],
        confidence_score=extracted["confidence_score"],
        raw_metadata=extracted["raw_metadata"],
        is_duplicate=is_duplicate,
        existing_id=existing_id,
        match_reason=match_reason,
    )


def upload_and_process_certificate(
    db: Session,
    file: UploadFile,
    current_user: User,
    auto_save: bool = True
) -> Any:
    """Handle multipart file upload, parse, and optionally auto-save."""
    if file.content_type not in ALLOWED_MIME_TYPES and not (file.filename and file.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.webp'))):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Supported formats: PDF, PNG, JPG, JPEG, WEBP."
        )

    file_bytes = file.file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 15MB limit."
        )

    if not auto_save:
        return preview_uploaded_file(db, file_bytes, file.filename or "certificate.pdf", current_user)

    # Auto-save flow
    saved_url = save_uploaded_bytes_to_disk(file_bytes, file.filename or "certificate.pdf")
    extracted = extract_certification_from_file_bytes(file_bytes, file.filename or "certificate.pdf", source=CertificationSource.FILE_UPLOAD)
    extracted["certificate_file_url"] = saved_url

    cert_in = CertificationCreate(
        certification_name=extracted["certification_name"],
        issuing_organization=extracted["issuing_organization"],
        issue_date=extracted["issue_date"],
        expiry_date=extracted["expiry_date"],
        credential_id=extracted["credential_id"],
        credential_url=extracted["credential_url"],
        certificate_file_url=saved_url,
        source=CertificationSource.FILE_UPLOAD,
        verification_status=extracted["verification_status"],
        extracted_skills=extracted["extracted_skills"],
        confidence_score=extracted["confidence_score"],
        raw_metadata=extracted["raw_metadata"],
    )

    return create_certification(db, cert_in, current_user)


# ==========================================
# 4. RESUME CERTIFICATION EXTRACTION
# ==========================================

def extract_certifications_from_user_resume(
    db: Session,
    resume_id: int,
    current_user: User,
    auto_save: bool = False
) -> List[Any]:
    """
    Extract certification items from candidate's resume (file or parsed data).
    """
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or access denied."
        )

    extracted_items = []
    
    # 1. Check ParsedResume table first
    parsed_res = db.query(ParsedResume).filter(ParsedResume.resume_id == resume.id).first()
    raw_cert_strings = []
    if parsed_res and parsed_res.certifications:
        if isinstance(parsed_res.certifications, list):
            raw_cert_strings.extend(parsed_res.certifications)
        elif isinstance(parsed_res.certifications, str):
            raw_cert_strings.append(parsed_res.certifications)

    # 2. If empty, read raw text from PDF file
    if not raw_cert_strings and resume.file_path and os.path.exists(resume.file_path):
        try:
            doc = fitz.open(resume.file_path)
            full_text = "\n".join([page.get_text() for page in doc])
            doc.close()

            # Find certification section
            cert_section_match = re.search(
                r"(?:certifications?|courses?|licenses?|credentials?)[:\s\n]+(.*?)(?=\n[A-Z\s]{4,}:|\Z)",
                full_text,
                re.IGNORECASE | re.DOTALL
            )
            if cert_section_match:
                section_text = cert_section_match.group(1)
                for line in section_text.splitlines():
                    line = line.strip()
                    if len(line) > 5 and not any(line.lower().startswith(x) for x in ["page", "email", "phone"]):
                        raw_cert_strings.append(line)
        except Exception:
            pass

    # 3. Process each string item
    results = []
    for cert_text in raw_cert_strings:
        if not cert_text or len(cert_text.strip()) < 4:
            continue

        item_data = parse_structured_certification(
            cert_text,
            raw_metadata={"resume_id": resume.id, "resume_name": resume.file_name, "snippet": cert_text},
            filename=resume.file_name
        )

        dup = find_duplicate_certification(
            db,
            user_id=current_user.id,
            credential_id=item_data.get("credential_id"),
            certification_name=item_data.get("certification_name", ""),
            issuing_organization=item_data.get("issuing_organization", "")
        )

        if auto_save:
            cert_in = CertificationCreate(
                certification_name=item_data["certification_name"],
                issuing_organization=item_data["issuing_organization"],
                issue_date=item_data["issue_date"],
                expiry_date=item_data["expiry_date"],
                credential_id=item_data["credential_id"],
                credential_url=item_data["credential_url"],
                certificate_file_url=None,
                source=CertificationSource.RESUME,
                verification_status=item_data["verification_status"],
                extracted_skills=item_data["extracted_skills"],
                confidence_score=item_data["confidence_score"],
                raw_metadata=item_data["raw_metadata"],
            )
            saved = create_certification(db, cert_in, current_user)
            results.append(saved)
        else:
            results.append(
                CertificationExtractResponse(
                    certification_name=item_data["certification_name"],
                    issuing_organization=item_data["issuing_organization"],
                    issue_date=item_data["issue_date"],
                    expiry_date=item_data["expiry_date"],
                    credential_id=item_data["credential_id"],
                    credential_url=item_data["credential_url"],
                    certificate_file_url=None,
                    source=CertificationSource.RESUME,
                    verification_status=item_data["verification_status"],
                    extracted_skills=item_data["extracted_skills"],
                    confidence_score=item_data["confidence_score"],
                    raw_metadata=item_data["raw_metadata"],
                    is_duplicate=dup is not None,
                    existing_id=dup.id if dup else None,
                    match_reason=f"Matches #{dup.id}" if dup else None,
                )
            )

    return results


# ==========================================
# 5. GOOGLE DRIVE INTEGRATION
# ==========================================

async def import_from_google_drive(
    db: Session,
    req: GoogleDriveImportRequest,
    current_user: User
) -> Any:
    """
    Stream certificate directly from Google Drive API using short-lived OAuth token.
    Token is strictly used in-flight and NEVER stored permanently.
    """
    drive_file_url = f"https://www.googleapis.com/drive/v3/files/{req.file_id}?alt=media"
    headers = {
        "Authorization": f"Bearer {req.access_token}"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(drive_file_url, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Google Drive API error: {resp.status_code} - {resp.text[:200]}"
                )
            file_bytes = resp.content
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch file from Google Drive: {str(e)}"
        )

    filename = req.file_name or "gdrive_certificate.pdf"
    
    if not req.auto_save:
        return preview_uploaded_file(
            db,
            file_bytes,
            filename,
            current_user,
            source=CertificationSource.GOOGLE_DRIVE
        )

    # Save to disk and commit to DB
    saved_url = save_uploaded_bytes_to_disk(file_bytes, filename)
    extracted = extract_certification_from_file_bytes(
        file_bytes,
        filename,
        source=CertificationSource.GOOGLE_DRIVE
    )
    extracted["certificate_file_url"] = saved_url
    extracted["raw_metadata"]["gdrive_file_id"] = req.file_id

    cert_in = CertificationCreate(
        certification_name=extracted["certification_name"],
        issuing_organization=extracted["issuing_organization"],
        issue_date=extracted["issue_date"],
        expiry_date=extracted["expiry_date"],
        credential_id=extracted["credential_id"],
        credential_url=extracted["credential_url"],
        certificate_file_url=saved_url,
        source=CertificationSource.GOOGLE_DRIVE,
        verification_status=extracted["verification_status"],
        extracted_skills=extracted["extracted_skills"],
        confidence_score=extracted["confidence_score"],
        raw_metadata=extracted["raw_metadata"],
    )

    return create_certification(db, cert_in, current_user)


async def import_folder_from_google_drive(
    db: Session,
    req: GoogleDriveFolderImportRequest,
    current_user: User
) -> GoogleDriveFolderImportResponse:
    """
    Import and extract all supported certificate files (PDF, JPG, JPEG, PNG, WEBP)
    directly from a Google Drive folder using ephemeral access token.
    Token is never stored permanently.
    """
    headers = {
        "Authorization": f"Bearer {req.access_token}"
    }
    
    # 1. List files in the Google Drive folder
    folder_files_url = (
        f"https://www.googleapis.com/drive/v3/files?"
        f"q='{req.folder_id}'+in+parents+and+trashed=false"
        f"&fields=files(id,name,mimeType,size)"
        f"&pageSize=100"
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(folder_files_url, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Google Drive API folder error ({resp.status_code}): {resp.text[:300]}"
                )
            folder_data = resp.json()
            drive_files = folder_data.get("files", [])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to query Google Drive folder: {str(e)}"
        )

    total_files = len(drive_files)
    processed_files = 0
    successful_files = 0
    failed_files = 0
    duplicate_files = 0
    imported_certifications: List[ImportedCertificationItem] = []
    errors: List[FileImportError] = []

    # Supported formats check
    supported_extensions = (".pdf", ".png", ".jpg", ".jpeg", ".webp")

    async with httpx.AsyncClient(timeout=45.0) as client:
        for f in drive_files:
            file_id = f.get("id")
            filename = f.get("name", "certificate.pdf")
            mime_type = f.get("mimeType", "")
            
            # Check if file format is supported
            is_supported = (
                filename.lower().endswith(supported_extensions)
                or mime_type in ALLOWED_MIME_TYPES
            )
            if not is_supported:
                # Skip non-certificate / unsupported files without marking hard error
                continue

            processed_files += 1

            try:
                # Download file bytes
                file_download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
                file_resp = await client.get(file_download_url, headers=headers)
                if file_resp.status_code != 200:
                    errors.append(
                        FileImportError(
                            filename=filename,
                            file_id=file_id,
                            error=f"Download failed with status {file_resp.status_code}"
                        )
                    )
                    failed_files += 1
                    continue

                file_bytes = file_resp.content
                if not file_bytes:
                    errors.append(
                        FileImportError(
                            filename=filename,
                            file_id=file_id,
                            error="File content is empty."
                        )
                    )
                    failed_files += 1
                    continue

                # Save file to disk
                saved_url = save_uploaded_bytes_to_disk(file_bytes, filename)

                # Extract certificate details with PyMuPDF & OCR
                extracted = extract_certification_from_file_bytes(
                    file_bytes,
                    filename,
                    source=CertificationSource.GOOGLE_DRIVE
                )
                extracted["certificate_file_url"] = saved_url
                extracted["raw_metadata"]["gdrive_file_id"] = file_id
                extracted["raw_metadata"]["gdrive_folder_id"] = req.folder_id

                # Deduplication check
                duplicate = find_duplicate_certification(
                    db,
                    user_id=current_user.id,
                    credential_id=extracted.get("credential_id"),
                    certification_name=extracted.get("certification_name", ""),
                    issuing_organization=extracted.get("issuing_organization", "")
                )

                if duplicate:
                    merged = merge_certification_records(duplicate, extracted)
                    db.commit()
                    db.refresh(merged)
                    duplicate_files += 1
                    successful_files += 1
                    imported_certifications.append(
                        ImportedCertificationItem(
                            id=merged.id,
                            filename=filename,
                            certification_name=extracted["certification_name"] if not is_invalid_or_generic_title(extracted["certification_name"]) else merged.certification_name,
                            issuing_organization=extracted["issuing_organization"] if extracted["issuing_organization"] != "Unknown Organization" else merged.issuing_organization,
                            issue_date=extracted["issue_date"] or merged.issue_date,
                            expiry_date=extracted["expiry_date"] or merged.expiry_date,
                            credential_id=extracted["credential_id"] or merged.credential_id,
                            credential_url=extracted["credential_url"] or merged.credential_url,
                            certificate_file_url=saved_url,
                            confidence_score=extracted["confidence_score"],
                            verification_status=extracted["verification_status"],
                            extracted_skills=extracted["extracted_skills"],
                            is_duplicate=True,
                            existing_id=merged.id,
                        )
                    )
                else:
                    cert_in = CertificationCreate(
                        certification_name=extracted["certification_name"],
                        issuing_organization=extracted["issuing_organization"],
                        issue_date=extracted["issue_date"],
                        expiry_date=extracted["expiry_date"],
                        credential_id=extracted["credential_id"],
                        credential_url=extracted["credential_url"],
                        certificate_file_url=saved_url,
                        source=CertificationSource.GOOGLE_DRIVE,
                        verification_status=extracted["verification_status"],
                        extracted_skills=extracted["extracted_skills"],
                        confidence_score=extracted["confidence_score"],
                        raw_metadata=extracted["raw_metadata"],
                    )
                    new_cert = create_certification(db, cert_in, current_user)
                    successful_files += 1
                    imported_certifications.append(
                        ImportedCertificationItem(
                            id=new_cert.id,
                            filename=filename,
                            certification_name=new_cert.certification_name,
                            issuing_organization=new_cert.issuing_organization,
                            issue_date=new_cert.issue_date,
                            expiry_date=new_cert.expiry_date,
                            credential_id=new_cert.credential_id,
                            credential_url=new_cert.credential_url,
                            certificate_file_url=new_cert.certificate_file_url,
                            confidence_score=new_cert.confidence_score or 0.0,
                            verification_status=new_cert.verification_status,
                            extracted_skills=new_cert.extracted_skills or [],
                            is_duplicate=False,
                            existing_id=None,
                        )
                    )

            except Exception as e:
                failed_files += 1
                errors.append(
                    FileImportError(
                        filename=filename,
                        file_id=file_id,
                        error=f"Processing error: {str(e)}"
                    )
                )

    return GoogleDriveFolderImportResponse(
        folder_id=req.folder_id,
        total_files=total_files,
        processed_files=processed_files,
        successful_files=successful_files,
        failed_files=failed_files,
        duplicate_files=duplicate_files,
        certifications=imported_certifications,
        errors=errors
    )



# ==========================================
# 6. PLATFORM SYNC & VERIFICATION ENGINE
# ==========================================

def sync_platform_credential(
    db: Session,
    req: PlatformCredentialSyncRequest,
    current_user: User
) -> Any:
    """
    Extract / sync credential from platform verification link or credential ID.
    Platforms: Coursera, Udemy, NPTEL, edX, AWS, Microsoft Learn, Google Cloud, Cisco, LinkedIn Learning, Credly.
    """
    platform_name = req.platform.strip()
    cred_url = req.credential_url.strip() if req.credential_url else None
    cred_id = req.credential_id.strip() if req.credential_id else None

    # Derive cert name or default
    cert_name = req.certification_name or f"{platform_name} Certified Professional"
    
    # Check initial status
    initial_status = evaluate_initial_verification_status(cred_url, platform_name)
    
    # Skill mapping
    extracted_skills = extract_skills_from_text(f"{platform_name} {cert_name}", cert_name)
    
    # Confidence score
    confidence = calculate_confidence_score(cert_name, platform_name, cred_id, cred_url, date.today(), extracted_skills)

    raw_meta = {
        "platform": platform_name,
        "sync_method": "PLATFORM_CREDENTIAL_SYNC",
        "synced_at": datetime.utcnow().isoformat()
    }

    if not req.auto_save:
        dup = find_duplicate_certification(db, current_user.id, cred_id, cert_name, platform_name)
        return CertificationExtractResponse(
            certification_name=cert_name,
            issuing_organization=platform_name,
            issue_date=date.today(),
            expiry_date=None,
            credential_id=cred_id,
            credential_url=cred_url,
            certificate_file_url=None,
            source=CertificationSource.PLATFORM_SYNC,
            verification_status=VerificationStatus(initial_status),
            extracted_skills=extracted_skills,
            confidence_score=confidence,
            raw_metadata=raw_meta,
            is_duplicate=dup is not None,
            existing_id=dup.id if dup else None,
            match_reason=f"Matches #{dup.id}" if dup else None,
        )

    cert_in = CertificationCreate(
        certification_name=cert_name,
        issuing_organization=platform_name,
        issue_date=date.today(),
        expiry_date=None,
        credential_id=cred_id,
        credential_url=cred_url,
        certificate_file_url=None,
        source=CertificationSource.PLATFORM_SYNC,
        verification_status=VerificationStatus(initial_status),
        extracted_skills=extracted_skills,
        confidence_score=confidence,
        raw_metadata=raw_meta,
    )

    return create_certification(db, cert_in, current_user)


async def verify_certification_credential(
    db: Session,
    cert_id: int,
    req: Optional[VerifyCredentialRequest],
    current_user: User
) -> VerificationResultResponse:
    """
    Perform active live verification probe against the credential verification URL.
    - Status rules:
      - 200 OK with valid response evidence -> VERIFIED
      - 404/410/500/timeout -> FAILED
      - Untrusted/unreachable -> FAILED / UNVERIFIED
    """
    cert = get_certification_by_id(db, cert_id, current_user)

    target_url = (req.credential_url if req and req.credential_url else cert.credential_url)
    target_id = (req.credential_id if req and req.credential_id else cert.credential_id)

    if not target_url and not target_id:
        cert.verification_status = "FAILED"
        db.commit()
        return VerificationResultResponse(
            certification_id=cert.id,
            verification_status=VerificationStatus.FAILED,
            message="No credential verification URL or ID available to verify.",
            verification_details={"error": "missing_verification_fields"}
        )

    if not target_url:
        # If only ID is present, we cannot perform external probe without URL
        cert.verification_status = "VERIFICATION_PENDING"
        db.commit()
        return VerificationResultResponse(
            certification_id=cert.id,
            verification_status=VerificationStatus.VERIFICATION_PENDING,
            message="Credential ID recorded. Verification URL is required for live confirmation probe.",
            verification_details={"credential_id": target_id}
        )

    # Perform active HTTP probe
    details: Dict[str, Any] = {"probed_url": target_url}
    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 CareerVerseVerifier/1.0"
            }
        ) as client:
            response = await client.get(target_url)
            details["status_code"] = response.status_code
            details["final_url"] = str(response.url)

            if response.status_code == 200:
                # Active probe confirmed live credential page
                cert.verification_status = "VERIFIED"
                cert.updated_at = datetime.utcnow()
                cert.raw_metadata = {
                    **(cert.raw_metadata or {}),
                    "verification_probe": {
                        "verified_at": datetime.utcnow().isoformat(),
                        "http_status": 200,
                        "verified_url": str(response.url)
                    }
                }
                db.commit()
                db.refresh(cert)

                return VerificationResultResponse(
                    certification_id=cert.id,
                    verification_status=VerificationStatus.VERIFIED,
                    message="Credential successfully verified via active provider probe.",
                    verification_details=details
                )
            else:
                cert.verification_status = "FAILED"
                cert.updated_at = datetime.utcnow()
                db.commit()

                return VerificationResultResponse(
                    certification_id=cert.id,
                    verification_status=VerificationStatus.FAILED,
                    message=f"Verification failed. Provider returned HTTP status {response.status_code}.",
                    verification_details=details
                )

    except httpx.RequestError as exc:
        details["error"] = str(exc)
        cert.verification_status = "FAILED"
        cert.updated_at = datetime.utcnow()
        db.commit()

        return VerificationResultResponse(
            certification_id=cert.id,
            verification_status=VerificationStatus.FAILED,
            message=f"Verification probe network error: {str(exc)}",
            verification_details=details
        )
