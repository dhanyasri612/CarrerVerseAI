import os
import fitz
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.session import get_db, SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.certification import Certification
from app.utils.security import hash_password
from app.utils.jwt import create_access_token

client = TestClient(app)


def setup_test_users():
    db: Session = SessionLocal()
    # Check or create role
    role = db.query(Role).filter(Role.name == "CANDIDATE").first()
    if not role:
        role = Role(name="CANDIDATE")
        db.add(role)
        db.commit()
        db.refresh(role)

    # User 1
    user1 = db.query(User).filter(User.email == "cert_test_user1@careerverse.ai").first()
    if not user1:
        user1 = User(
            name="Cert Test User 1",
            email="cert_test_user1@careerverse.ai",
            hashed_password=hash_password("TestPass123!"),
            role_id=role.id,
            is_active=True
        )
        db.add(user1)
        db.commit()
        db.refresh(user1)

    # User 2 (for authorization checks)
    user2 = db.query(User).filter(User.email == "cert_test_user2@careerverse.ai").first()
    if not user2:
        user2 = User(
            name="Cert Test User 2",
            email="cert_test_user2@careerverse.ai",
            hashed_password=hash_password("TestPass123!"),
            role_id=role.id,
            is_active=True
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)

    # Clean existing test certifications and resumes for test isolation
    db.query(Certification).filter(Certification.user_id.in_([user1.id, user2.id])).delete(synchronize_session=False)
    db.query(ParsedResume).filter(ParsedResume.resume_id.in_(
        db.query(Resume.id).filter(Resume.user_id.in_([user1.id, user2.id]))
    )).delete(synchronize_session=False)
    db.query(Resume).filter(Resume.user_id.in_([user1.id, user2.id])).delete(synchronize_session=False)
    db.commit()

    token1 = create_access_token({"sub": user1.email, "id": user1.id})
    token2 = create_access_token({"sub": user2.email, "id": user2.id})
    db.close()
    return user1, token1, user2, token2


def test_certification_pipeline():
    user1, token1, user2, token2 = setup_test_users()
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    print("\n--- 1. Testing Manual Certification Creation ---")
    payload1 = {
        "certification_name": "AWS Certified Solutions Architect - Associate",
        "issuing_organization": "Amazon Web Services",
        "issue_date": "2024-05-10",
        "expiry_date": "2027-05-10",
        "credential_id": "AWS-SAA-100293",
        "credential_url": "https://www.credly.com/badges/sample-aws-badge",
        "source": "MANUAL",
        "verification_status": "UNVERIFIED",
        "extracted_skills": ["AWS", "Cloud Architecture"],
        "confidence_score": 1.0,
        "raw_metadata": {"notes": "Passed on first attempt"}
    }
    res = client.post("/certifications", json=payload1, headers=headers1)
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
    cert1 = res.json()
    cert1_id = cert1["id"]
    # Verify trust rule: Credly URL sets status to VERIFICATION_PENDING (not VERIFIED)
    assert cert1["verification_status"] == "VERIFICATION_PENDING", f"Expected VERIFICATION_PENDING, got {cert1['verification_status']}"
    assert cert1["certification_name"] == payload1["certification_name"]
    print(f"Created manual certification #{cert1_id} with status {cert1['verification_status']}")

    print("\n--- 2. Testing Deduplication and Skill Merging ---")
    duplicate_payload = {
        "certification_name": "AWS Certified Solutions Architect - Associate",
        "issuing_organization": "Amazon Web Services",
        "credential_id": "AWS-SAA-100293",
        "credential_url": "https://www.credly.com/badges/sample-aws-badge-updated",
        "extracted_skills": ["Docker", "Kubernetes", "AWS"], # Merging extra skills
        "source": "MANUAL"
    }
    res_dup = client.post("/certifications", json=duplicate_payload, headers=headers1)
    assert res_dup.status_code == 201
    merged_cert = res_dup.json()
    assert merged_cert["id"] == cert1_id, "Duplicate record should merge into existing ID, not create a new one!"
    assert "Docker" in merged_cert["extracted_skills"] and "AWS" in merged_cert["extracted_skills"]
    print(f"Deduplication successfully merged skills for #{cert1_id}: {merged_cert['extracted_skills']}")

    print("\n--- 3. Testing Listing & Filtering ---")
    list_res = client.get("/certifications?source=MANUAL", headers=headers1)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1
    print(f"Found {len(list_res.json())} certifications for user 1")

    print("\n--- 4. Testing PDF Upload & PyMuPDF Extraction ---")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), """
Coursera
DeepLearning.AI
This is to certify that
Cert Test User 1
has successfully completed
Deep Learning Specialization
Authorized by DeepLearning.AI and offered through Coursera
Issued on September 15, 2024
Coursera Verify: DL-SPEC-2024-99
https://coursera.org/verify/DL-SPEC-2024-99
""")
    pdf_bytes = doc.write()
    doc.close()

    files = {"file": ("deep_learning_cert.pdf", pdf_bytes, "application/pdf")}
    upload_res = client.post("/certifications/upload?auto_save=true", files=files, headers=headers1)
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    uploaded_cert = upload_res.json()
    assert "Deep Learning" in uploaded_cert["certification_name"]
    assert uploaded_cert["issuing_organization"] == "Coursera"
    assert uploaded_cert["verification_status"] == "VERIFICATION_PENDING"
    assert uploaded_cert["source"] == "FILE_UPLOAD"
    assert uploaded_cert["certificate_file_url"] is not None
    print(f"Uploaded & parsed PDF certification #{uploaded_cert['id']}: {uploaded_cert['certification_name']}")

    print("\n--- 5. Testing Preview Without Saving ---")
    preview_files = {"file": ("deep_learning_cert.pdf", pdf_bytes, "application/pdf")}
    preview_res = client.post("/certifications/preview-file", files=preview_files, headers=headers1)
    assert preview_res.status_code == 200
    preview_data = preview_res.json()
    assert preview_data["is_duplicate"] == True
    print(f"Preview detected existing duplicate #{preview_data['existing_id']}")

    print("\n--- 6. Testing Platform Sync ---")
    sync_payload = {
        "platform": "Udemy",
        "credential_url": "https://www.udemy.com/certificate/UC-abcdef12-3456-7890/",
        "credential_id": "UC-abcdef12-3456-7890",
        "certification_name": "The Complete Web Development Bootcamp",
        "auto_save": True
    }
    sync_res = client.post("/certifications/platform-sync", json=sync_payload, headers=headers1)
    assert sync_res.status_code == 200
    synced_cert = sync_res.json()
    assert synced_cert["issuing_organization"] == "Udemy"
    assert synced_cert["source"] == "PLATFORM_SYNC"
    assert synced_cert["verification_status"] == "VERIFICATION_PENDING"
    print(f"Platform synced certification #{synced_cert['id']}: {synced_cert['certification_name']}")

    print("\n--- 7. Testing User Ownership & Security ---")
    # User 2 tries to read User 1's cert
    unauth_get = client.get(f"/certifications/{cert1_id}", headers=headers2)
    assert unauth_get.status_code == 404, "User 2 should not be able to view User 1's certification"
    
    # User 2 tries to delete User 1's cert
    unauth_del = client.delete(f"/certifications/{cert1_id}", headers=headers2)
    assert unauth_del.status_code == 404, "User 2 should not be able to delete User 1's certification"
    print("User ownership security checks passed successfully!")

    print("\n--- 8. Testing Resume Certification Extraction ---")
    db: Session = SessionLocal()
    # Create test resume
    resume = Resume(
        user_id=user1.id,
        file_name="test_resume.pdf",
        file_path="uploads/resumes/test_resume.pdf",
        file_type="application/pdf",
        file_size=1024,
        parsed_status=True
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    resume_id = resume.id
    parsed_res = ParsedResume(
        resume_id=resume.id,
        name="Cert Test User 1",
        certifications=[
            "AWS Certified Developer - Associate (Credential ID: AWS-DEV-9921, Issued: June 2024)",
            "Google Cloud Certified Professional Cloud Architect"
        ]
    )
    db.add(parsed_res)
    db.commit()
    db.close()

    resume_extract_res = client.post(f"/certifications/extract-from-resume/{resume_id}?auto_save=true", headers=headers1)
    assert resume_extract_res.status_code == 200, f"Resume extract failed: {resume_extract_res.text}"
    extracted_from_resume = resume_extract_res.json()
    assert len(extracted_from_resume) == 2
    print(f"Extracted and saved {len(extracted_from_resume)} certifications from resume!")

    print("\n--- 9. Testing Active Verification Probe ---")
    # Test verify on cert with fake URL
    probe_res = client.post(f"/certifications/{uploaded_cert['id']}/verify", headers=headers1)
    assert probe_res.status_code == 200
    probe_data = probe_res.json()
    assert probe_data["certification_id"] == uploaded_cert["id"]
    print(f"Probe executed with status: {probe_data['verification_status']}, message: {probe_data['message']}")

    print("\n--- 10. Testing Google Drive Folder Bulk Import ---")
    import unittest.mock as mock

    # Prepare sample certificate payloads
    # 1. Text PDF
    doc1 = fitz.open()
    p1 = doc1.new_page()
    p1.insert_text((50, 50), "AWS Certified Cloud Practitioner\nIssued by: Amazon Web Services (AWS)\nIssue Date: 2024-02-15\nCredential ID: AWS-CCP-1002")
    pdf1_bytes = doc1.write()
    doc1.close()

    # 2. Scanned image PDF
    doc2_txt = fitz.open()
    p2_txt = doc2_txt.new_page(width=600, height=400)
    p2_txt.insert_text((50, 100), "Certificate of Completion\nPython Programming Specialization\nIssued by: Stanford Online\nDate: 2024-01-19\nCredential ID: ST-99281", fontsize=16)
    pix2 = p2_txt.get_pixmap(dpi=150)
    doc2_txt.close()
    scanned_pdf2 = fitz.open()
    scanned_page2 = scanned_pdf2.new_page(width=pix2.width, height=pix2.height)
    scanned_page2.insert_image(scanned_page2.rect, stream=pix2.tobytes("png"))
    pdf2_bytes = scanned_pdf2.write()
    scanned_pdf2.close()

    # 3. Pure PNG image
    img3_bytes = pix2.tobytes("png")

    folder_files_list = {
        "files": [
            {"id": "file_1_id", "name": "aws_cloud.pdf", "mimeType": "application/pdf"},
            {"id": "file_2_id", "name": "23AM018_scanned.pdf", "mimeType": "application/pdf"},
            {"id": "file_3_id", "name": "python_badge.png", "mimeType": "image/png"},
            {"id": "file_4_dup", "name": "aws_cloud_dup.pdf", "mimeType": "application/pdf"},
            {"id": "file_5_err", "name": "damaged_file.pdf", "mimeType": "application/pdf"},
        ]
    }

    async def mock_async_get(self, url, *args, **kwargs):
        class MockResponse:
            def __init__(self, status_code, content=b"", json_data=None):
                self.status_code = status_code
                self.content = content
                self._json = json_data or {}
                self.text = content.decode("utf-8", errors="ignore") if content else ""

            def json(self):
                return self._json

        if "q=" in url:
            # Folder listing
            return MockResponse(200, json_data=folder_files_list)
        elif "file_1_id" in url or "file_4_dup" in url:
            return MockResponse(200, content=pdf1_bytes)
        elif "file_2_id" in url:
            return MockResponse(200, content=pdf2_bytes)
        elif "file_3_id" in url:
            return MockResponse(200, content=img3_bytes)
        elif "file_5_err" in url:
            return MockResponse(500, content=b"Corrupted Google Drive file stream")
        return MockResponse(404, content=b"Not found")

    with mock.patch("httpx.AsyncClient.get", new=mock_async_get):
        gdrive_folder_payload = {
            "folder_id": "1AbCdEfGhIjKlMnOpQrStUvWxYz",
            "access_token": "mock_ephemeral_token_12345"
        }
        folder_res = client.post("/certifications/google-drive/import-folder", json=gdrive_folder_payload, headers=headers1)
        assert folder_res.status_code == 200, f"Folder import failed: {folder_res.text}"
        folder_data = folder_res.json()
        print("Folder import response:", folder_data)
        assert folder_data["total_files"] == 5
        assert folder_data["processed_files"] == 5
        assert folder_data["successful_files"] == 4
        assert folder_data["failed_files"] == 1
        assert folder_data["duplicate_files"] == 2
        assert len(folder_data["errors"]) == 1
        assert folder_data["errors"][0]["filename"] == "damaged_file.pdf"
        print("Google Drive folder bulk import tests passed with full OCR & duplicate handling!")

    print("\n--- 11. Testing Update & Delete ---")
    update_res = client.put(f"/certifications/{uploaded_cert['id']}", json={"confidence_score": 0.95}, headers=headers1)
    assert update_res.status_code == 200
    assert update_res.json()["confidence_score"] == 0.95

    del_res = client.delete(f"/certifications/{uploaded_cert['id']}", headers=headers1)
    assert del_res.status_code == 200
    print(f"Successfully updated and deleted certification #{uploaded_cert['id']}")

    print("\n==========================================")
    print("ALL CERTIFICATION PIPELINE TESTS PASSED!")
    print("==========================================")


if __name__ == "__main__":
    test_certification_pipeline()
