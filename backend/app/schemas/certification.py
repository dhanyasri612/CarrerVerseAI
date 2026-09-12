from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class CertificationSource(str, Enum):
    MANUAL = "MANUAL"
    RESUME = "RESUME"
    FILE_UPLOAD = "FILE_UPLOAD"
    GOOGLE_DRIVE = "GOOGLE_DRIVE"
    PLATFORM_SYNC = "PLATFORM_SYNC"


class VerificationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class CertificationBase(BaseModel):
    certification_name: str = Field(..., description="Name of the certification or course")
    issuing_organization: str = Field(..., description="Organization or platform issuing the credential")
    issue_date: Optional[date] = Field(None, description="Date when the credential was issued")
    expiry_date: Optional[date] = Field(None, description="Date when the credential expires")
    credential_id: Optional[str] = Field(None, description="Unique credential or badge ID")
    credential_url: Optional[str] = Field(None, description="Public verification URL")
    certificate_file_url: Optional[str] = Field(None, description="Path or URL to stored certificate file")
    source: CertificationSource = Field(default=CertificationSource.MANUAL, description="Ingestion source")
    verification_status: VerificationStatus = Field(default=VerificationStatus.UNVERIFIED, description="Trust evaluation status")
    extracted_skills: List[str] = Field(default_factory=list, description="Skills mapped from certification")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    raw_metadata: Dict[str, Any] = Field(default_factory=dict, description="Raw extraction or platform metadata")


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(BaseModel):
    certification_name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    certificate_file_url: Optional[str] = None
    source: Optional[CertificationSource] = None
    verification_status: Optional[VerificationStatus] = None
    extracted_skills: Optional[List[str]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    raw_metadata: Optional[Dict[str, Any]] = None


class CertificationResponse(CertificationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CertificationExtractResponse(BaseModel):
    certification_name: str
    issuing_organization: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    certificate_file_url: Optional[str] = None
    source: CertificationSource
    verification_status: VerificationStatus
    extracted_skills: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)
    is_duplicate: bool = False
    existing_id: Optional[int] = None
    match_reason: Optional[str] = None


class GoogleDriveImportRequest(BaseModel):
    file_id: str = Field(..., description="Google Drive file ID")
    access_token: str = Field(..., description="Short-lived ephemeral OAuth access token")
    file_name: Optional[str] = Field("certificate.pdf", description="Original file name in Google Drive")
    auto_save: bool = Field(False, description="Whether to automatically save or return preview")


class PlatformCredentialSyncRequest(BaseModel):
    platform: str = Field(..., description="Platform name: Coursera, Udemy, NPTEL, edX, AWS, Microsoft, Google Cloud, Cisco, LinkedIn Learning, Credly")
    credential_url: Optional[str] = Field(None, description="Public verification URL")
    credential_id: Optional[str] = Field(None, description="Credential or badge ID")
    certification_name: Optional[str] = Field(None, description="Optional manual override name")
    auto_save: bool = Field(False, description="Whether to automatically save or return preview")


class VerifyCredentialRequest(BaseModel):
    credential_url: Optional[str] = Field(None, description="Optional URL to verify")
    credential_id: Optional[str] = Field(None, description="Optional ID to verify")


class VerificationResultResponse(BaseModel):
    certification_id: int
    verification_status: VerificationStatus
    message: str
    verification_details: Dict[str, Any] = Field(default_factory=dict)


class GoogleDriveFolderImportRequest(BaseModel):
    folder_id: str = Field(..., description="Google Drive Folder ID containing certificate files")
    access_token: str = Field(..., description="Short-lived ephemeral OAuth access token")


class ImportedCertificationItem(BaseModel):
    id: Optional[int] = None
    filename: str
    certification_name: str
    issuing_organization: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    certificate_file_url: Optional[str] = None
    confidence_score: float
    verification_status: str
    extracted_skills: List[str] = Field(default_factory=list)
    is_duplicate: bool = False
    existing_id: Optional[int] = None


class FileImportError(BaseModel):
    filename: str
    file_id: Optional[str] = None
    error: str


class GoogleDriveFolderImportResponse(BaseModel):
    folder_id: str
    total_files: int
    processed_files: int
    successful_files: int
    failed_files: int
    duplicate_files: int
    certifications: List[ImportedCertificationItem]
    errors: List[FileImportError]

