from typing import List, Dict, Any, Optional, Set, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.github_profile import GitHubProfile
from app.models.github_repository import GitHubRepository
from app.models.linkedin_profile import LinkedInProfile
from app.models.leetcode_profile import LeetCodeProfile
from app.models.hackerrank_profile import HackerRankProfile
from app.models.certification import Certification

from app.schemas.candidate_intelligence import (
    SkillEvidenceItem,
    UnifiedSkill,
    SkillsByCategory,
    UserProfileSummary,
    EducationSummary,
    ExperienceSummary,
    ProjectSummary,
    CertificationsSummary,
    GitHubSummary,
    LinkedInSummary,
    LeetCodeSummary,
    HackerRankSummary,
    ResumeSummary,
    ProfileCompleteness,
    UnifiedProfileResponse,
)
from app.parsers.skill_normalizer import (
    normalize_skill,
    SKILL_CATEGORIES,
)


def _safe_get_user_profile(user: User, candidate_profile: Optional[CandidateProfile]) -> UserProfileSummary:
    """Build user profile summary."""
    summary_text = None
    if candidate_profile and candidate_profile.summary:
        summary_text = candidate_profile.summary
    elif user.bio:
        summary_text = user.bio

    return UserProfileSummary(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        college=user.college,
        degree=user.degree,
        graduation_year=user.graduation_year,
        location=user.location,
        bio=user.bio,
        summary=summary_text,
        created_at=user.created_at,
    )


def _aggregate_education(
    user: User,
    candidate_profile: Optional[CandidateProfile],
    parsed_resumes: List[ParsedResume]
) -> List[EducationSummary]:
    """Aggregate education entries from CandidateProfile, parsed resumes, and basic profile."""
    education_list: List[EducationSummary] = []
    seen_keys: Set[str] = set()

    # 1. From CandidateProfile
    if candidate_profile and candidate_profile.education:
        raw_edu = candidate_profile.education
        if isinstance(raw_edu, list):
            for item in raw_edu:
                if isinstance(item, dict):
                    inst = item.get("institution") or item.get("college") or item.get("school")
                    deg = item.get("degree")
                    key = f"{inst}_{deg}".lower()
                    if key not in seen_keys:
                        seen_keys.add(key)
                        education_list.append(
                            EducationSummary(
                                institution=inst,
                                degree=deg,
                                field_of_study=item.get("field_of_study") or item.get("major"),
                                start_date=str(item.get("start_date")) if item.get("start_date") else None,
                                end_date=str(item.get("end_date")) if item.get("end_date") else None,
                                grade=item.get("grade") or item.get("gpa") or item.get("percentage"),
                                raw_text=item.get("raw_text")
                            )
                        )
                elif isinstance(item, str) and item.strip():
                    key = item.strip().lower()
                    if key not in seen_keys:
                        seen_keys.add(key)
                        education_list.append(EducationSummary(institution=item.strip(), raw_text=item.strip()))

    # 2. From ParsedResumes
    for pr in parsed_resumes:
        if pr.education:
            if isinstance(pr.education, list):
                for item in pr.education:
                    if isinstance(item, dict):
                        inst = item.get("institution") or item.get("college") or item.get("school")
                        deg = item.get("degree")
                        key = f"{inst}_{deg}".lower()
                        if key not in seen_keys:
                            seen_keys.add(key)
                            education_list.append(
                                EducationSummary(
                                    institution=inst,
                                    degree=deg,
                                    field_of_study=item.get("field_of_study") or item.get("major"),
                                    start_date=str(item.get("start_date")) if item.get("start_date") else None,
                                    end_date=str(item.get("end_date")) if item.get("end_date") else None,
                                    grade=item.get("grade") or item.get("gpa") or item.get("percentage"),
                                    raw_text=item.get("raw_text")
                                )
                            )
                    elif isinstance(item, str) and item.strip():
                        key = item.strip().lower()
                        if key not in seen_keys:
                            seen_keys.add(key)
                            education_list.append(EducationSummary(institution=item.strip(), raw_text=item.strip()))
            elif isinstance(pr.education, str) and pr.education.strip():
                key = pr.education.strip().lower()
                if key not in seen_keys:
                    seen_keys.add(key)
                    education_list.append(EducationSummary(institution=pr.education.strip(), raw_text=pr.education.strip()))

    # 3. Fallback from User basic fields
    if not education_list and (user.college or user.degree):
        education_list.append(
            EducationSummary(
                institution=user.college,
                degree=user.degree,
                end_date=str(user.graduation_year) if user.graduation_year else None,
                raw_text=f"{user.degree or ''} from {user.college or ''}".strip()
            )
        )

    return education_list


def _aggregate_experience(
    candidate_profile: Optional[CandidateProfile],
    parsed_resumes: List[ParsedResume]
) -> List[ExperienceSummary]:
    """Aggregate work experience entries."""
    experience_list: List[ExperienceSummary] = []
    seen_keys: Set[str] = set()

    sources_to_check = []
    if candidate_profile and candidate_profile.experience:
        sources_to_check.append(candidate_profile.experience)
    for pr in parsed_resumes:
        if pr.experience:
            sources_to_check.append(pr.experience)

    for src in sources_to_check:
        if isinstance(src, list):
            for item in src:
                if isinstance(item, dict):
                    company = item.get("company") or item.get("organization") or item.get("employer")
                    role = item.get("role") or item.get("title") or item.get("position")
                    key = f"{company}_{role}".lower()
                    if key not in seen_keys:
                        seen_keys.add(key)
                        experience_list.append(
                            ExperienceSummary(
                                company=company,
                                role=role,
                                duration=item.get("duration") or item.get("dates"),
                                description=item.get("description"),
                                technologies=item.get("technologies") or [],
                                raw_text=item.get("raw_text")
                            )
                        )
                elif isinstance(item, str) and item.strip():
                    key = item.strip().lower()
                    if key not in seen_keys:
                        seen_keys.add(key)
                        experience_list.append(ExperienceSummary(company=item.strip(), raw_text=item.strip()))
        elif isinstance(src, str) and src.strip():
            key = src.strip().lower()
            if key not in seen_keys:
                seen_keys.add(key)
                experience_list.append(ExperienceSummary(company=src.strip(), raw_text=src.strip()))

    return experience_list


def _aggregate_projects(
    candidate_profile: Optional[CandidateProfile],
    parsed_resumes: List[ParsedResume],
    github_repositories: List[GitHubRepository]
) -> List[ProjectSummary]:
    """Aggregate projects from GitHub, CandidateProfile, and Resumes."""
    projects_list: List[ProjectSummary] = []
    seen_titles: Set[str] = set()

    # 1. Selected or starred GitHub repositories
    for repo in github_repositories:
        title = repo.name
        key = title.lower()
        if key not in seen_titles:
            seen_titles.add(key)
            techs = []
            if repo.language:
                techs.append(repo.language)
            if repo.topics and isinstance(repo.topics, list):
                techs.extend(repo.topics)

            projects_list.append(
                ProjectSummary(
                    title=repo.name,
                    description=repo.description or "GitHub repository project",
                    technologies=techs,
                    source="github",
                    url=repo.url,
                    stars=repo.stars or 0
                )
            )

    # 2. CandidateProfile projects
    if candidate_profile and candidate_profile.projects:
        raw_p = candidate_profile.projects
        if isinstance(raw_p, list):
            for item in raw_p:
                if isinstance(item, dict):
                    title = item.get("title") or item.get("name") or "Project"
                    key = title.lower()
                    if key not in seen_titles:
                        seen_titles.add(key)
                        projects_list.append(
                            ProjectSummary(
                                title=title,
                                description=item.get("description"),
                                technologies=item.get("technologies") or item.get("skills") or [],
                                source="candidate_profile",
                                url=item.get("url") or item.get("link")
                            )
                        )
                elif isinstance(item, str) and item.strip():
                    key = item.strip().lower()
                    if key not in seen_titles:
                        seen_titles.add(key)
                        projects_list.append(
                            ProjectSummary(
                                title=item.strip(),
                                source="candidate_profile"
                            )
                        )

    # 3. ParsedResumes projects
    for pr in parsed_resumes:
        if pr.projects:
            if isinstance(pr.projects, list):
                for item in pr.projects:
                    if isinstance(item, dict):
                        title = item.get("title") or item.get("name") or "Project"
                        key = title.lower()
                        if key not in seen_titles:
                            seen_titles.add(key)
                            projects_list.append(
                                ProjectSummary(
                                    title=title,
                                    description=item.get("description"),
                                    technologies=item.get("technologies") or item.get("skills") or [],
                                    source="resume",
                                    url=item.get("url") or item.get("link")
                                )
                            )
                    elif isinstance(item, str) and item.strip():
                        key = item.strip().lower()
                        if key not in seen_titles:
                            seen_titles.add(key)
                            projects_list.append(
                                ProjectSummary(
                                    title=item.strip(),
                                    source="resume"
                                )
                            )

    return projects_list


def _collect_unified_skills(
    candidate_profile: Optional[CandidateProfile],
    parsed_resumes: List[ParsedResume],
    github_profile: Optional[GitHubProfile],
    github_repositories: List[GitHubRepository],
    leetcode_profile: Optional[LeetCodeProfile],
    hackerrank_profile: Optional[HackerRankProfile],
    certifications: List[Certification]
) -> Tuple[List[UnifiedSkill], List[SkillsByCategory]]:
    """
    Collect all skills across all 8 candidate touchpoints, normalize aliases,
    deduplicate, compile multi-source evidence, calculate evidence-based confidence scores,
    and group into taxonomy categories.
    """
    # canonical_name -> {"name": canonical_name, "category": category, "evidence": List[SkillEvidenceItem], "sources": Set[str]}
    skill_store: Dict[str, Dict[str, Any]] = {}

    def add_evidence(raw_skill: str, source: str, detail: str, weight: float):
        if not raw_skill or not isinstance(raw_skill, str):
            return
        canonical_name, category = normalize_skill(raw_skill)
        if not canonical_name:
            return

        if canonical_name not in skill_store:
            skill_store[canonical_name] = {
                "name": canonical_name,
                "category": category,
                "evidence": [],
                "sources": set()
            }

        skill_store[canonical_name]["sources"].add(source)
        # Avoid duplicate exact detail strings for the same source
        existing_details = [e.detail for e in skill_store[canonical_name]["evidence"]]
        if detail not in existing_details:
            skill_store[canonical_name]["evidence"].append(
                SkillEvidenceItem(
                    source=source,
                    detail=detail,
                    weight=weight
                )
            )

    # 1. Resume Skills
    for pr in parsed_resumes:
        if pr.skills:
            skills_raw = pr.skills if isinstance(pr.skills, list) else [pr.skills]
            for s in skills_raw:
                if isinstance(s, str):
                    add_evidence(s, "resume", f"Listed in extracted technical skills from resume", 0.65)

    # 2. CandidateProfile Skills
    if candidate_profile and candidate_profile.skills:
        cp_skills = candidate_profile.skills if isinstance(candidate_profile.skills, list) else [candidate_profile.skills]
        for s in cp_skills:
            if isinstance(s, str):
                add_evidence(s, "candidate_profile", f"Self-declared in candidate profile", 0.60)

    # 3. GitHub Profile & Repositories
    if github_profile:
        # Languages
        if github_profile.languages and isinstance(github_profile.languages, dict):
            for lang, count in github_profile.languages.items():
                add_evidence(lang, "github", f"Language used across GitHub repositories ({count} occurrences)", 0.80)
        elif github_profile.languages and isinstance(github_profile.languages, list):
            for lang in github_profile.languages:
                if isinstance(lang, str):
                    add_evidence(lang, "github", f"Profile language on GitHub", 0.75)
        # Topics
        if github_profile.topics and isinstance(github_profile.topics, list):
            for t in github_profile.topics:
                if isinstance(t, str):
                    add_evidence(t, "github", f"Topic tag on GitHub profile", 0.70)

    # GitHub Repositories
    for repo in github_repositories:
        if repo.language:
            add_evidence(repo.language, "github", f"Primary language in repository '{repo.name}'", 0.85)
        if repo.topics and isinstance(repo.topics, list):
            for t in repo.topics:
                if isinstance(t, str):
                    add_evidence(t, "github", f"Repository topic in '{repo.name}'", 0.70)

    # 4. Certifications
    for cert in certifications:
        is_verified = cert.verification_status == "VERIFIED"
        status_label = "Verified" if is_verified else f"Status: {cert.verification_status}"
        weight = 0.92 if is_verified else 0.75
        
        if cert.extracted_skills and isinstance(cert.extracted_skills, list):
            for sk in cert.extracted_skills:
                if isinstance(sk, str):
                    add_evidence(
                        sk,
                        "certification",
                        f"Certificate: {cert.certification_name} ({cert.issuing_organization}) - {status_label}",
                        weight
                    )

    # 5. LeetCode Profile
    if leetcode_profile:
        # Solved Languages
        if leetcode_profile.languages and isinstance(leetcode_profile.languages, list):
            for item in leetcode_profile.languages:
                if isinstance(item, dict):
                    lang_name = item.get("languageName") or item.get("name")
                    solved = item.get("problemsSolved") or 0
                    if lang_name:
                        weight = 0.88 if solved >= 10 else 0.72
                        add_evidence(lang_name, "leetcode", f"Used to solve {solved} algorithmic problems on LeetCode", weight)
                elif isinstance(item, str):
                    add_evidence(item, "leetcode", f"Language used on LeetCode", 0.72)

        # Skill Tags / Topics
        if leetcode_profile.skills and isinstance(leetcode_profile.skills, list):
            for item in leetcode_profile.skills:
                if isinstance(item, dict):
                    tag_name = item.get("tagName") or item.get("name")
                    solved = item.get("problemsSolved") or 0
                    if tag_name:
                        add_evidence(tag_name, "leetcode", f"Solved {solved} {tag_name} problems on LeetCode", 0.80)
                elif isinstance(item, str):
                    add_evidence(item, "leetcode", f"LeetCode problem-solving topic: {item}", 0.75)

    # 6. HackerRank Profile
    if hackerrank_profile:
        # Badges
        if hackerrank_profile.badges and isinstance(hackerrank_profile.badges, list):
            for b in hackerrank_profile.badges:
                if isinstance(b, dict):
                    badge_name = b.get("badge_name") or b.get("name")
                    stars = b.get("stars") or 0
                    if badge_name:
                        add_evidence(badge_name, "hackerrank", f"{stars}-Star HackerRank Badge in {badge_name}", 0.82)
                elif isinstance(b, str):
                    add_evidence(b, "hackerrank", f"HackerRank Badge in {b}", 0.75)
        # Certificates
        if hackerrank_profile.certificates and isinstance(hackerrank_profile.certificates, list):
            for c in hackerrank_profile.certificates:
                if isinstance(c, dict):
                    c_title = c.get("title") or c.get("name")
                    if c_title:
                        add_evidence(c_title, "hackerrank", f"HackerRank Skill Certificate: {c_title}", 0.88)
                elif isinstance(c, str):
                    add_evidence(c, "hackerrank", f"HackerRank Skill Certificate: {c}", 0.85)

    # ----------------------------------------------------
    # Calculate Evidence-Based Confidence Scores
    # ----------------------------------------------------
    unified_skills_list: List[UnifiedSkill] = []

    for name, data in skill_store.items():
        evidence_list: List[SkillEvidenceItem] = data["evidence"]
        source_set: Set[str] = data["sources"]
        distinct_sources_count = len(source_set)

        if not evidence_list:
            continue

        # Highest individual evidence reliability weight
        max_evidence_weight = max(e.weight for e in evidence_list)

        # Calculate multi-source confidence boost:
        # - Single source: baseline = max_evidence_weight (e.g. HackerRank cert = 0.88, verified cert = 0.92, resume = 0.65)
        # - Two independent sources: +0.06 cross-source verification boost
        # - Three or more sources: +0.08 to +0.14 boost (cross-verified proficiency across multiple independent platforms)
        if distinct_sources_count == 1:
            confidence = max_evidence_weight
        elif distinct_sources_count == 2:
            confidence = min(max_evidence_weight + 0.06, 0.95)
        else:
            confidence = min(max_evidence_weight + 0.08 + min((distinct_sources_count - 2) * 0.02, 0.06), 0.98)

        # Cap confidence between 0.10 and 0.98
        final_confidence = min(max(round(confidence, 2), 0.10), 0.98)

        unified_skills_list.append(
            UnifiedSkill(
                name=name,
                category=data["category"],
                confidence_score=final_confidence,
                sources=sorted(list(source_set)),
                supporting_sources_count=distinct_sources_count,
                evidence=evidence_list
            )
        )

    # Sort skills by confidence score (descending)
    unified_skills_list.sort(key=lambda s: s.confidence_score, reverse=True)

    # Group by category
    skills_by_category_dict: Dict[str, List[UnifiedSkill]] = {cat: [] for cat in SKILL_CATEGORIES}
    for sk in unified_skills_list:
        if sk.category in skills_by_category_dict:
            skills_by_category_dict[sk.category].append(sk)
        else:
            if "Tools & Technologies" in skills_by_category_dict:
                skills_by_category_dict["Tools & Technologies"].append(sk)

    skills_by_category_list: List[SkillsByCategory] = [
        SkillsByCategory(category=cat, skills=skills_by_category_dict[cat])
        for cat in SKILL_CATEGORIES
        if skills_by_category_dict[cat]
    ]

    return unified_skills_list, skills_by_category_list


def _calculate_profile_completeness(
    user: User,
    candidate_profile: Optional[CandidateProfile],
    education_list: List[EducationSummary],
    experience_list: List[ExperienceSummary],
    projects_list: List[ProjectSummary],
    resumes: List[Resume],
    unified_skills: List[UnifiedSkill],
    github_profile: Optional[GitHubProfile],
    linkedin_profile: Optional[LinkedInProfile],
    leetcode_profile: Optional[LeetCodeProfile],
    hackerrank_profile: Optional[HackerRankProfile],
    certifications: List[Certification]
) -> ProfileCompleteness:
    """
    Calculate profile completeness score (0-100), identify missing sections,
    and generate actionable recommendations and data quality warnings.
    """
    section_scores: Dict[str, int] = {}
    missing_sections: List[str] = []
    recommendations: List[str] = []
    warnings: List[str] = []

    # 1. Basic Profile (10 pts)
    bp_score = 0
    if user.name and user.email:
        bp_score += 4
    if user.phone:
        bp_score += 2
    else:
        warnings.append("No contact phone number provided in basic profile.")
    if user.location:
        bp_score += 2
    if user.bio or (candidate_profile and candidate_profile.summary):
        bp_score += 2
    else:
        warnings.append("No professional bio or career summary provided.")
    section_scores["basic_profile"] = bp_score
    if bp_score < 7:
        missing_sections.append("Basic Profile Information")
        recommendations.append("Complete your basic profile with contact information, location, and bio.")

    # 2. Education (10 pts)
    if education_list:
        section_scores["education"] = 10
    else:
        section_scores["education"] = 0
        missing_sections.append("Education")
        recommendations.append("Add your educational background (college, degree, graduation year).")

    # 3. Work Experience (10 pts)
    if experience_list:
        section_scores["experience"] = 10
    else:
        section_scores["experience"] = 0
        missing_sections.append("Work Experience")
        recommendations.append("Add work experience, internships, or freelance roles to demonstrate practical experience.")

    # 4. Projects (10 pts)
    if projects_list:
        section_scores["projects"] = 10
    else:
        section_scores["projects"] = 0
        missing_sections.append("Projects")
        recommendations.append("Add projects or sync your GitHub repositories to showcase hands-on work.")

    # 5. Resume (10 pts)
    if resumes:
        has_parsed = any(r.parsed_status for r in resumes)
        section_scores["resume"] = 10 if has_parsed else 6
    else:
        section_scores["resume"] = 0
        missing_sections.append("Resume")
        recommendations.append("Upload a PDF resume to enable automated skill and career intelligence extraction.")

    # 6. Skills (10 pts)
    skills_count = len(unified_skills)
    if skills_count >= 5:
        section_scores["skills"] = 10
    else:
        section_scores["skills"] = min(skills_count * 2, 10)
        if skills_count == 0:
            missing_sections.append("Skills")
            recommendations.append("Add technical and professional skills across your profile, resume, or projects.")
        else:
            warnings.append(f"Only {skills_count} skills detected. Adding more certifications, repos, or resume details will enrich skill intelligence.")

    # 7. GitHub Integration (10 pts)
    if github_profile:
        repo_count = github_profile.total_repositories or 0
        section_scores["github"] = 10 if repo_count > 0 else 6
        if repo_count == 0:
            warnings.append("GitHub connected, but 0 public repositories were discovered.")
    else:
        section_scores["github"] = 0
        missing_sections.append("GitHub Profile")
        recommendations.append("Connect your GitHub account via /github/sync/{username} to verify code repositories and languages.")

    # 8. LinkedIn Integration (5 pts)
    if linkedin_profile:
        section_scores["linkedin"] = 5
    else:
        section_scores["linkedin"] = 0
        missing_sections.append("LinkedIn Profile")
        recommendations.append("Connect your LinkedIn profile via OAuth to verify your professional identity.")

    # 9. Coding Platforms - LeetCode / HackerRank (10 pts)
    cp_score = 0
    if leetcode_profile:
        cp_score += 5 if (leetcode_profile.total_solved or 0) > 0 else 3
    if hackerrank_profile:
        cp_score += 5 if (hackerrank_profile.total_solved or 0) > 0 else 3
    section_scores["coding_platforms"] = min(cp_score, 10)
    if cp_score == 0:
        missing_sections.append("Coding Profiles (LeetCode / HackerRank)")
        recommendations.append("Sync your LeetCode or HackerRank profile to showcase algorithmic problem-solving skills.")

    # 10. Certifications (10 pts)
    if certifications:
        verified_count = sum(1 for c in certifications if c.verification_status == "VERIFIED")
        unverified_count = len(certifications) - verified_count
        section_scores["certifications"] = 10 if verified_count > 0 else 6
        if unverified_count > 0 and verified_count == 0:
            warnings.append(f"{unverified_count} certification(s) are unverified. Trigger live credential verification to boost skill confidence.")
    else:
        section_scores["certifications"] = 0
        missing_sections.append("Certifications")
        recommendations.append("Upload certificates or import credentials from Google Drive/Coursera/AWS/NPTEL.")

    # 11. Candidate Profile Summary (5 pts)
    if candidate_profile and candidate_profile.summary:
        section_scores["candidate_profile"] = 5
    else:
        section_scores["candidate_profile"] = 0

    total_score = sum(section_scores.values())
    total_score = min(max(total_score, 0), 100)

    return ProfileCompleteness(
        score=total_score,
        section_scores=section_scores,
        missing_sections=missing_sections,
        actionable_recommendations=recommendations,
        data_quality_warnings=warnings
    )


# ==========================================
# MAIN UNIFIED CANDIDATE PROFILE SERVICE
# ==========================================

def build_unified_candidate_profile(
    db: Session,
    current_user: User
) -> UnifiedProfileResponse:
    """
    Aggregate all 8 candidate touchpoints into a unified intelligence response.
    Guarantees user isolation and fault tolerance (no single missing integration fails the request).
    """
    user_id = current_user.id

    # 1. Fetch all models for current_user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = current_user

    candidate_profile = (
        db.query(CandidateProfile)
        .filter(CandidateProfile.user_id == user_id)
        .first()
    )

    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
        .all()
    )

    parsed_resumes = (
        db.query(ParsedResume)
        .join(Resume, ParsedResume.resume_id == Resume.id)
        .filter(Resume.user_id == user_id)
        .all()
    )

    github_profile = (
        db.query(GitHubProfile)
        .filter(GitHubProfile.user_id == user_id)
        .first()
    )

    github_repositories = []
    if github_profile:
        github_repositories = (
            db.query(GitHubRepository)
            .filter(GitHubRepository.github_profile_id == github_profile.id)
            .all()
        )

    linkedin_profile = (
        db.query(LinkedInProfile)
        .filter(LinkedInProfile.user_id == user_id)
        .first()
    )

    leetcode_profile = (
        db.query(LeetCodeProfile)
        .filter(LeetCodeProfile.user_id == user_id)
        .first()
    )

    hackerrank_profile = (
        db.query(HackerRankProfile)
        .filter(HackerRankProfile.user_id == user_id)
        .first()
    )

    certifications = (
        db.query(Certification)
        .filter(Certification.user_id == user_id)
        .order_by(Certification.created_at.desc())
        .all()
    )

    # 2. Build Component Summaries
    user_profile_summary = _safe_get_user_profile(user, candidate_profile)
    education_summary = _aggregate_education(user, candidate_profile, parsed_resumes)
    experience_summary = _aggregate_experience(candidate_profile, parsed_resumes)
    projects_summary = _aggregate_projects(candidate_profile, parsed_resumes, github_repositories)

    # Resume Summary
    has_parsed_data = len(parsed_resumes) > 0 or (any(r.parsed_status for r in resumes) if resumes else False)
    resume_summary = ResumeSummary(
        uploaded=len(resumes) > 0,
        count=len(resumes),
        latest_filename=resumes[0].file_name if resumes else None,
        parsed_status=has_parsed_data
    )

    # GitHub Summary (aggregate repo languages if profile languages dict is empty)
    gh_languages: Dict[str, Any] = {}
    if github_profile and isinstance(github_profile.languages, dict) and github_profile.languages:
        gh_languages = dict(github_profile.languages)
    elif github_repositories:
        for repo in github_repositories:
            if repo.language:
                gh_languages[repo.language] = gh_languages.get(repo.language, 0) + 1

    github_summary = GitHubSummary(
        connected=github_profile is not None,
        username=github_profile.username if github_profile else None,
        profile_url=github_profile.profile_url if github_profile else None,
        total_repositories=github_profile.total_repositories if github_profile else len(github_repositories),
        total_stars=github_profile.total_stars if github_profile else sum(r.stars or 0 for r in github_repositories),
        total_forks=github_profile.total_forks if github_profile else sum(r.forks or 0 for r in github_repositories),
        languages=gh_languages,
        top_topics=github_profile.topics if github_profile and isinstance(github_profile.topics, list) else [],
        analyzed_repositories_count=len([r for r in github_repositories if r.selected_for_analysis])
    )

    # LinkedIn Summary (Never expose tokens!)
    linkedin_summary = LinkedInSummary(
        connected=linkedin_profile is not None,
        name=linkedin_profile.name if linkedin_profile else None,
        email=linkedin_profile.email if linkedin_profile else None,
        email_verified=linkedin_profile.email_verified if linkedin_profile else None,
        profile_picture=linkedin_profile.profile_picture if linkedin_profile else None,
        locale=linkedin_profile.locale if linkedin_profile else None
    )

    # LeetCode Summary
    leetcode_summary = LeetCodeSummary(
        connected=leetcode_profile is not None,
        username=leetcode_profile.username if leetcode_profile else None,
        profile_url=leetcode_profile.profile_url if leetcode_profile else None,
        ranking=leetcode_profile.ranking if leetcode_profile else None,
        reputation=leetcode_profile.reputation if leetcode_profile else None,
        total_solved=leetcode_profile.total_solved if leetcode_profile else 0,
        easy_solved=leetcode_profile.easy_solved if leetcode_profile else 0,
        medium_solved=leetcode_profile.medium_solved if leetcode_profile else 0,
        hard_solved=leetcode_profile.hard_solved if leetcode_profile else 0,
        acceptance_rate=leetcode_profile.acceptance_rate if leetcode_profile else None,
        contest_rating=leetcode_profile.contest_rating if leetcode_profile else None,
        badges_count=len(leetcode_profile.badges) if leetcode_profile and isinstance(leetcode_profile.badges, list) else 0,
        languages=leetcode_profile.languages if leetcode_profile and isinstance(leetcode_profile.languages, list) else []
    )

    # HackerRank Summary
    hackerrank_summary = HackerRankSummary(
        connected=hackerrank_profile is not None,
        username=hackerrank_profile.username if hackerrank_profile else None,
        profile_url=hackerrank_profile.profile_url if hackerrank_profile else None,
        display_name=hackerrank_profile.display_name if hackerrank_profile else None,
        country=hackerrank_profile.country if hackerrank_profile else None,
        school=hackerrank_profile.school if hackerrank_profile else None,
        total_solved=hackerrank_profile.total_solved if hackerrank_profile else 0,
        badges_count=len(hackerrank_profile.badges) if hackerrank_profile and isinstance(hackerrank_profile.badges, list) else 0,
        certificates_count=len(hackerrank_profile.certificates) if hackerrank_profile and isinstance(hackerrank_profile.certificates, list) else 0,
        badges=hackerrank_profile.badges if hackerrank_profile and isinstance(hackerrank_profile.badges, list) else []
    )

    # Certifications Summary
    verified_certs = [c for c in certifications if c.verification_status == "VERIFIED"]
    pending_certs = [c for c in certifications if c.verification_status == "VERIFICATION_PENDING"]
    certifications_summary = CertificationsSummary(
        total_certifications=len(certifications),
        verified_count=len(verified_certs),
        pending_count=len(pending_certs),
        items=[
            {
                "id": c.id,
                "certification_name": c.certification_name,
                "issuing_organization": c.issuing_organization,
                "issue_date": str(c.issue_date) if c.issue_date else None,
                "expiry_date": str(c.expiry_date) if c.expiry_date else None,
                "credential_id": c.credential_id,
                "credential_url": c.credential_url,
                "certificate_file_url": c.certificate_file_url,
                "source": c.source,
                "verification_status": c.verification_status,
                "extracted_skills": c.extracted_skills or [],
                "confidence_score": c.confidence_score
            }
            for c in certifications
        ]
    )

    # 3. Collect Unified Skills & Evidence
    unified_skills, skills_by_category = _collect_unified_skills(
        candidate_profile=candidate_profile,
        parsed_resumes=parsed_resumes,
        github_profile=github_profile,
        github_repositories=github_repositories,
        leetcode_profile=leetcode_profile,
        hackerrank_profile=hackerrank_profile,
        certifications=certifications
    )

    # 4. Compute Profile Completeness & Quality Warnings
    completeness = _calculate_profile_completeness(
        user=user,
        candidate_profile=candidate_profile,
        education_list=education_summary,
        experience_list=experience_summary,
        projects_list=projects_summary,
        resumes=resumes,
        unified_skills=unified_skills,
        github_profile=github_profile,
        linkedin_profile=linkedin_profile,
        leetcode_profile=leetcode_profile,
        hackerrank_profile=hackerrank_profile,
        certifications=certifications
    )

    return UnifiedProfileResponse(
        user_profile=user_profile_summary,
        education=education_summary,
        experience=experience_summary,
        projects=projects_summary,
        resume_summary=resume_summary,
        github_summary=github_summary,
        linkedin_summary=linkedin_summary,
        leetcode_summary=leetcode_summary,
        hackerrank_summary=hackerrank_summary,
        certifications_summary=certifications_summary,
        unified_skills=unified_skills,
        skills_by_category=skills_by_category,
        completeness=completeness
    )
