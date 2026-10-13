from typing import Any, Dict, List
from app.schemas.candidate_intelligence import UnifiedProfileResponse
from app.schemas.embedding import CandidateTextDocument


class CandidateTextBuilder:
    """
    Transforms multi-source UnifiedProfileResponse into semantically rich,
    dense textual representations optimized for Sentence Transformers (all-MiniLM-L6-v2).
    """

    @staticmethod
    def build_document(profile: UnifiedProfileResponse) -> CandidateTextDocument:
        user_profile = profile.user_profile
        user_id = user_profile.id

        # 1. Headline & Professional Summary
        summary_parts: List[str] = []
        if user_profile.name:
            summary_parts.append(f"Candidate: {user_profile.name}")
        if user_profile.degree and user_profile.college:
            summary_parts.append(f"Education: {user_profile.degree} from {user_profile.college}")
        elif user_profile.degree:
            summary_parts.append(f"Education: {user_profile.degree}")
        if user_profile.summary:
            summary_parts.append(f"Profile Summary: {user_profile.summary.strip()}")
        elif user_profile.bio:
            summary_parts.append(f"Bio: {user_profile.bio.strip()}")
        summary_text = ". ".join(summary_parts) if summary_parts else "Candidate Profile Overview."

        # 2. Verified Skills Narrative (with categories, confidence scores, and source evidence)
        skills_lines: List[str] = []
        if profile.unified_skills:
            for skill in profile.unified_skills:
                sources_str = ", ".join(skill.sources) if skill.sources else "verified"
                conf_pct = int(skill.confidence_score * 100)
                skills_lines.append(f"{skill.name} ({skill.category}, {conf_pct}% confidence via {sources_str})")
        skills_text = "Demonstrated Technical Skills: " + "; ".join(skills_lines) if skills_lines else "No verified technical skills recorded."

        # 3. Work Experience Narrative
        exp_lines: List[str] = []
        if profile.experience:
            for exp in profile.experience:
                company = exp.company or "Company"
                role = exp.role or "Software Engineer"
                duration = f" ({exp.duration})" if exp.duration else ""
                techs = f" Technologies: {', '.join(exp.technologies)}." if exp.technologies else ""
                desc = f" Description: {exp.description.strip()}." if exp.description else ""
                exp_lines.append(f"Role: {role} at {company}{duration}.{techs}{desc}")
        experience_text = "Work Experience: " + " ".join(exp_lines) if exp_lines else "No formal work experience recorded."

        # 4. Technical Projects Portfolio
        proj_lines: List[str] = []
        if profile.projects:
            for proj in profile.projects:
                techs = f" Built with {', '.join(proj.technologies)}." if proj.technologies else ""
                desc = f" {proj.description.strip()}" if proj.description else ""
                proj_lines.append(f"Project '{proj.title}':{techs}{desc}")
        projects_text = "Technical Projects: " + " ".join(proj_lines) if proj_lines else "No technical projects recorded."

        # 5. Credentials & Competitive Programming Milestones
        cred_lines: List[str] = []
        # Certifications
        if profile.certifications_summary and profile.certifications_summary.items:
            cert_names = [
                c.get("title") or c.get("name")
                for c in profile.certifications_summary.items
                if isinstance(c, dict) and (c.get("title") or c.get("name"))
            ]
            if cert_names:
                cred_lines.append(f"Certifications: {', '.join(cert_names)}.")

        # LeetCode Profile
        if profile.leetcode_summary and profile.leetcode_summary.connected:
            lc = profile.leetcode_summary
            lc_info = f"LeetCode: {lc.total_solved} problems solved ({lc.easy_solved} easy, {lc.medium_solved} medium, {lc.hard_solved} hard)"
            if lc.ranking:
                lc_info += f", global rank {lc.ranking}"
            if lc.contest_rating:
                lc_info += f", contest rating {lc.contest_rating:.0f}"
            cred_lines.append(lc_info + ".")

        # HackerRank Profile
        if profile.hackerrank_summary and profile.hackerrank_summary.connected:
            hr = profile.hackerrank_summary
            badges = [
                b.get("badge_name") for b in hr.badges
                if isinstance(b, dict) and b.get("badge_name")
            ]
            hr_info = f"HackerRank: {hr.total_solved} problems solved"
            if badges:
                hr_info += f", badges earned in {', '.join(badges)}"
            cred_lines.append(hr_info + ".")

        # GitHub Stats
        if profile.github_summary and profile.github_summary.connected:
            gh = profile.github_summary
            languages = list(gh.languages.keys()) if isinstance(gh.languages, dict) else []
            gh_info = f"GitHub: {gh.total_repositories} repositories, {gh.total_stars} stars"
            if languages:
                gh_info += f", active languages: {', '.join(languages[:5])}"
            cred_lines.append(gh_info + ".")

        credentials_text = "Technical Credentials & Problem Solving: " + " ".join(cred_lines) if cred_lines else "No external credentials recorded."

        # 6. Combined Global Synthesis
        full_text_sections = [
            summary_text,
            skills_text,
            experience_text,
            projects_text,
            credentials_text,
        ]
        full_text = "\n\n".join(section for section in full_text_sections if section.strip())

        # 7. Metadata for filtering and ChromaDB ingestion
        metadata: Dict[str, Any] = {
            "user_id": user_id,
            "name": user_profile.name,
            "email": user_profile.email,
            "degree": user_profile.degree,
            "college": user_profile.college,
            "total_skills": len(profile.unified_skills),
            "top_skills": [s.name for s in profile.unified_skills[:10]],
            "has_resume": profile.resume_summary.uploaded if profile.resume_summary else False,
            "github_connected": profile.github_summary.connected if profile.github_summary else False,
            "leetcode_connected": profile.leetcode_summary.connected if profile.leetcode_summary else False,
            "hackerrank_connected": profile.hackerrank_summary.connected if profile.hackerrank_summary else False,
            "completeness_score": profile.completeness.score if profile.completeness else 0,
        }

        return CandidateTextDocument(
            user_id=user_id,
            full_text=full_text,
            skills_text=skills_text,
            experience_text=experience_text,
            projects_text=projects_text,
            credentials_text=credentials_text,
            metadata=metadata,
        )
