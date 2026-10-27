"""
Prompt builder for Personalized Interview Preparation Agent.
Constructs strict, fact-grounded system and user prompts to generate personalized interview questions.
"""

from typing import Any, Dict, List, Optional
from app.ai.language.prompt_builder import language_prompt_builder
from app.schemas.rag import RAGPrompt, RAGRetrievedContext
from app.schemas.skill_gap import SkillGapItem


class InterviewPromptBuilder:
    """
    Constructs prompts enforcing factual grounding and structured JSON generation
    for personalized candidate interview preparation across supported languages (Tamil, Hindi, English, etc.).
    """

    SYSTEM_PROMPT = """You are CareerVerse AI's Senior Technical Interview Coach and Assessment Agent.
Your objective is to generate personalized, grounded interview preparation questions for a candidate based strictly on their verified profile evidence, target role, and identified skill gaps.

CRITICAL INSTRUCTIONS & STRICT BOUNDARIES:
1. STRICT EVIDENCE GROUNDING:
   - Rely ONLY on the candidate profile facts (skills, projects, technologies, experience, certifications) and target role requirements provided below.
   - NEVER invent or hallucinate candidate projects, previous employers, achievements, or skills.
   - If a project name appears in a question or rationale, it MUST exist in the provided candidate projects list.
   - If a skill or technology is cited as candidate evidence, it MUST exist in the candidate's verified evidence.

2. SUPPORTING PROJECT & SKILL-GAP DIFFERENTIATION:
   - When asking project-based questions, refer to the candidate's real projects (e.g., Ecomm_Backend, CareerVerseAI, InboxPilot_Backend). Do NOT invent implementation details that are not in the context. Ask about architecture, challenges, design decisions, and verified tech stack.
   - When asking about identified SKILL GAPS (missing or unverified requirements for a target role):
     * Set question_type to "skill_gap".
     * In the rationale, explicitly state that this question addresses an identified skill gap/growth area for the target role, NOT that the candidate currently claims mastery over it.
   - When a user asks about a project or skill that DOES NOT exist in their profile:
     * Do NOT claim the candidate possesses or built it.
     * Note in the rationale/summary that there is no verified candidate evidence for that item, and present it as a conceptual/learning question without attributing it to their profile.

3. QUESTION TYPES:
   Each question must have one of the following question_type values:
   - "project_based": Deep dive into candidate's real project architecture, design trade-offs, and implementation.
   - "technical": Core technical knowledge, algorithms, language features, and systems fundamentals.
   - "skill_based": Practical application of candidate's verified skills.
   - "role_based": Scenario and best-practice questions tailored to the target role's expectations.
   - "skill_gap": Questions designed to help the candidate prepare for areas where they currently have gaps.
   - "behavioral": Collaboration, problem-solving, code review, and engineering trade-offs.

4. DIFFICULTY LEVELS:
   - "easy", "medium", or "hard"

5. AVOID PROMISES, FAKE STATS & PROBABILITIES:
   - Never claim a question is guaranteed to be asked by a specific employer.
   - Do not invent salary information, hiring probabilities, or company-specific hiring criteria.
   - Use phrasing like "recommended preparation question", "grounded in your project evidence", or "targeted for role readiness".

6. OUTPUT FORMAT:
   Return ONLY a valid JSON object without markdown formatting, enclosed in a ```json code block:
   {
     "preparation_summary": "A concise, grounded strategic overview of how the candidate should prepare based on their real strengths and target role/topics.",
     "questions": [
       {
         "question": "Clear, direct interview question text",
         "question_type": "project_based | technical | skill_based | role_based | skill_gap | behavioral",
         "difficulty": "easy | medium | hard",
         "topic": "Domain topic name (e.g., FastAPI Architecture, Concurrency, SQL Optimization)",
         "rationale": "Grounded explanation explaining why this question is recommended based on verified candidate profile data or target role gap.",
         "supporting_skills": ["Python", "FastAPI"],
         "supporting_projects": ["Ecomm_Backend"],
         "supporting_technologies": ["Python", "PostgreSQL"],
         "evidence_sources": ["project", "skill"]
       }
     ]
   }
"""

    def build_prompt(
        self,
        query: str,
        interview_mode: str,
        target_role: Optional[str],
        context: RAGRetrievedContext,
        candidate_graph_evidence: Dict[str, Any],
        skill_gap_items: Optional[List[SkillGapItem]] = None,
        num_questions: int = 5,
        language: str = "en",
    ) -> RAGPrompt:
        """
        Builds user message with verified multi-modal context and structured instructions in the target language.
        """
        sections: List[str] = []

        # 1. Candidate Overview
        cand_name = "Candidate"
        if context.graph_context and context.graph_context.candidate and context.graph_context.candidate.name:
            cand_name = context.graph_context.candidate.name
        cand_id = context.candidate_id
        sections.append(f"### CANDIDATE: {cand_name} (ID: {cand_id})")
        if target_role:
            sections.append(f"### TARGET INTERVIEW ROLE: {target_role}")
        sections.append(f"### DETECTED INTERVIEW MODE: {interview_mode.upper()}")
        sections.append(f"### USER INQUIRY: \"{query}\"")

        # 2. Verified Candidate Skills & Technologies
        verified_skills = candidate_graph_evidence.get("skills", [])
        if verified_skills:
            skill_names = [s.name if hasattr(s, "name") else (s.get("name") if isinstance(s, dict) else str(s)) for s in verified_skills]
            sections.append(f"### VERIFIED CANDIDATE SKILLS ({len(skill_names)}):\n" + ", ".join(skill_names[:30]))

        verified_techs = candidate_graph_evidence.get("technologies", [])
        if verified_techs:
            tech_names = [t.name if hasattr(t, "name") else (t.get("name") if isinstance(t, dict) else str(t)) for t in verified_techs]
            sections.append(f"### VERIFIED TECHNOLOGIES USED:\n" + ", ".join(tech_names))

        # 3. Verified Candidate Projects
        verified_projects = candidate_graph_evidence.get("projects", [])
        if verified_projects:
            proj_lines = []
            for p in verified_projects[:10]:
                name = getattr(p, "title", None) or getattr(p, "name", None) or (p.get("title") if isinstance(p, dict) else (p.get("name") if isinstance(p, dict) else str(p)))
                desc = getattr(p, "description", "") or (p.get("description", "") if isinstance(p, dict) else "")
                techs = getattr(p, "technologies", []) or (p.get("technologies", []) if isinstance(p, dict) else [])
                proj_lines.append(f"- Project: {name} | Tech: {', '.join(techs) if techs else 'N/A'} | Desc: {str(desc)[:120]}")
            sections.append("### VERIFIED CANDIDATE PROJECTS:\n" + "\n".join(proj_lines))

        # 4. Verified Experience & Education
        verified_exp = candidate_graph_evidence.get("experience", [])
        if verified_exp:
            exp_lines = []
            for e in verified_exp[:5]:
                title = getattr(e, "title", "") or (e.get("title", "") if isinstance(e, dict) else "")
                company = getattr(e, "company", "") or (e.get("company", "") if isinstance(e, dict) else "")
                exp_lines.append(f"- {title} at {company}" if title or company else f"- {e}")
            sections.append("### VERIFIED EXPERIENCE:\n" + "\n".join(exp_lines))

        # 5. Skill Gap Analysis (if available)
        if skill_gap_items:
            gap_lines = []
            for g in skill_gap_items:
                if g.status in ("missing", "partially_demonstrated", "insufficient_evidence"):
                    gap_lines.append(f"- Skill Gap: {g.skill} (Status: {g.status}, Gap Level: {g.gap_level}, Req: {g.target_requirement})")
            if gap_lines:
                sections.append("### IDENTIFIED SKILL GAPS FOR TARGET ROLE:\n" + "\n".join(gap_lines))

        # 6. Semantic Context Chunks / Structured Context Text
        if context.context_text:
            sections.append("### RELEVANT RETRIEVED TEXT EVIDENCE:\n" + context.context_text[:1500])

        # 7. Generation Directives based on mode
        mode_directives = {
            "project": f"Generate {num_questions} interview questions focused specifically on the candidate's verified projects, their architecture, trade-offs, and applied technologies.",
            "skill": f"Generate {num_questions} technical interview questions evaluating the candidate's verified technical skills and depth.",
            "skill_gap": f"Generate {num_questions} targeted interview questions focusing on identified skill gaps for the target role, clearly labeling them as skill_gap type.",
            "target_role": f"Generate {num_questions} balanced interview questions for a {target_role or 'software engineering'} interview, combining role-based requirements, candidate strengths, real projects, and skill-gap readiness.",
            "general": f"Generate {num_questions} personalized interview questions covering candidate's real projects, technical skills, and core engineering principles.",
        }

        directive = mode_directives.get(interview_mode, mode_directives["general"])
        lang_instruction = language_prompt_builder.build_language_instruction(language)

        sections.append(
            f"### TASK INSTRUCTION:\n{directive}\n{lang_instruction}\n"
            "Ensure all JSON fields are complete, supporting arrays contain only real verified evidence, and no projects/skills are invented."
        )

        user_message = "\n\n".join(sections)

        system_prompt = language_prompt_builder.with_system_language_policy(
            self.SYSTEM_PROMPT, language
        )

        return RAGPrompt(
            system_prompt=system_prompt,
            user_message=user_message,
            query=query,
        )


# Global singleton instance
interview_prompt_builder = InterviewPromptBuilder()

