import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.user import User
from app.models.job import Job
from app.utils.skill_normalizer import normalize_skill



def contains_metrics(items):
    """
    Check whether resume content contains measurable information
    such as percentages, numbers, or quantities.
    """

    metric_pattern = r"\b\d+(\.\d+)?\s*(%|percent|users|projects|years|months|ms|seconds|hours|days)?\b"

    for item in items:
        if item and re.search(metric_pattern, item.lower()):
            return True

    return False


def analyze_resume(
    db: Session,
    resume_id: int,
    job_id: int,
    current_user: User
):
    # 1. Check resume ownership
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # 2. Get parsed resume
    parsed_resume = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.resume_id == resume.id
        )
        .first()
    )

    if not parsed_resume:
        raise HTTPException(
            status_code=404,
            detail="Parsed resume not found"
        )

    # 3. Get target job
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    strengths = []
    weaknesses = []
    suggestions = []

    # 4. Resume skills
    resume_skills = {
        normalize_skill(skill)
        for skill in (parsed_resume.skills or [])
        if skill
    }

    # 5. Job required skills
    required_skills = {
        normalize_skill(skill)
        for skill in (job.required_skills or [])
        if skill
    }

    # 6. Find matched and missing skills
    matched_skills = resume_skills.intersection(required_skills)
    missing_skills = required_skills.difference(resume_skills)

    # 7. Skill analysis
    if matched_skills:
        strengths.append(
            f"Resume matches {len(matched_skills)} required job skill(s)"
        )

    if missing_skills:
        weaknesses.append(
            "Resume is missing some skills required for the target job"
        )

        for skill in sorted(missing_skills):
            suggestions.append(
                f"Add experience or projects demonstrating {skill}"
            )
    else:
        strengths.append(
            "Resume contains all required skills for the target job"
        )

    # 8. Analyze education
    education = parsed_resume.education or []

    if education:
        strengths.append(
            "Education information is available"
        )
    else:
        weaknesses.append(
            "Education information is missing"
        )
        suggestions.append(
            "Add your educational qualifications"
        )

    # 9. Analyze experience
    experience = parsed_resume.experience or []

    if experience:
        strengths.append(
            "Resume contains experience information"
        )
    else:
        weaknesses.append(
            "Work experience information is missing"
        )
        suggestions.append(
            "Add internships, work experience, or relevant practical experience"
        )

    # 10. Analyze projects
    projects = parsed_resume.projects or []

    if projects:
        strengths.append(
            "Resume contains project information"
        )
    else:
        weaknesses.append(
            "Project information is missing"
        )
        suggestions.append(
            "Add projects relevant to the target job"
        )

    # 11. Analyze certifications
    certifications = parsed_resume.certifications or []

    if certifications:
        strengths.append(
            "Certifications are included"
        )
    else:
        suggestions.append(
            "Consider adding certifications relevant to the target job"
        )

    # 12. Analyze measurable achievements
    content_to_check = experience + projects

    if content_to_check:
        if contains_metrics(content_to_check):
            strengths.append(
                "Resume includes measurable information or achievements"
            )
        else:
            weaknesses.append(
                "Experience and project descriptions lack measurable achievements"
            )
            suggestions.append(
                "Add measurable results such as percentages, "
                "performance improvements, users served, or time saved"
            )

    return {
        "resume_id": resume_id,
        "job_id": job_id,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions
    }