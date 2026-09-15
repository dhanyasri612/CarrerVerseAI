from sqlalchemy import Column, Integer, String, Date, Float, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    certification_name = Column(String(255), nullable=False, index=True)
    issuing_organization = Column(String(255), nullable=False, index=True)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    credential_id = Column(String(255), nullable=True, index=True)
    credential_url = Column(String(1000), nullable=True)
    certificate_file_url = Column(String(1000), nullable=True)

    # Source: MANUAL, RESUME, FILE_UPLOAD, GOOGLE_DRIVE, PLATFORM_SYNC
    source = Column(String(50), nullable=False, default="MANUAL")

    # Status: UNVERIFIED, VERIFICATION_PENDING, VERIFIED, FAILED
    verification_status = Column(String(50), nullable=False, default="UNVERIFIED")

    extracted_skills = Column(JSON, nullable=True, default=list)
    confidence_score = Column(Float, nullable=True, default=1.0)
    raw_metadata = Column(JSON, nullable=True, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship("User", back_populates="certifications")

    @property
    def name(self):
        """Convenience alias for certification_name"""
        return self.certification_name

    @name.setter
    def name(self, value):
        self.certification_name = value
