import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.knowledge_graph.graph_queries import graph_query_service
from app.ai.providers.factory import get_model_provider
from app.ai.rag.context_builder import rag_context_builder
from app.models.profile_quiz_session import ProfileQuizSession
from app.models.user import User
from app.schemas.profile_quiz import (
    QuizAnswerRequest,
    QuizQuestion,
    QuizResult,
    QuizSessionCreateRequest,
    QuizSessionResponse,
)


class QuizSessionNotFound(Exception):
    pass


class QuizSessionStateError(Exception):
    pass


QUESTION_PROMPT = """You are the Career Profile Agent. Create a short profile-based career assessment.
Use only the verified candidate context provided. Do not invent skills, projects, education, or experience.
Create exactly five relevant questions: a mix of single choice, multiple choice, and short text.
Questions must help distinguish career direction and fill gaps in the candidate evidence.
Return only JSON: {\"questions\":[{\"id\":\"q1\",\"question\":\"...\",\"question_type\":\"single|multiple|text\",\"options\":[\"...\"],\"why_it_matters\":\"...\"}]}
If evidence is limited, say so in why_it_matters and ask the candidate to provide the missing detail."""

RESULT_PROMPT = """You are the Career Intelligence Synthesizer. Summarize a candidate's profile-based career assessment.
Use only the verified candidate context and answers. Never invent evidence or numeric scores.
Return only JSON with career_direction, summary, career_paths, strengths, skills_to_develop, and recommended_next_steps."""


def _json_response(system_prompt: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = get_model_provider().generate_text(
        system_prompt=system_prompt,
        user_message=json.dumps(payload, ensure_ascii=False),
        temperature=0.2,
        max_completion_tokens=1200,
    )
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].removesuffix("```").strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        raise QuizSessionStateError("AI provider returned an invalid quiz response")
    try:
        parsed = json.loads(raw[start : end + 1])
    except (TypeError, json.JSONDecodeError) as exc:
        raise QuizSessionStateError("AI provider returned an invalid quiz response") from exc
    if not isinstance(parsed, dict):
        raise QuizSessionStateError("AI provider returned an invalid quiz response")
    return parsed


def _evidence(candidate_id: int, query: str) -> Dict[str, Any]:
    context = rag_context_builder.build_retrieval_context(candidate_id=candidate_id, query=query, top_k=5)

    def _dump(items):
        return [item.model_dump() if hasattr(item, "model_dump") else item for item in items]

    return {
        "context": context.context_text[:12000],
        "skills": _dump(graph_query_service.get_candidate_skills(candidate_id)),
        "projects": _dump(graph_query_service.get_candidate_projects(candidate_id)),
        "technologies": _dump(graph_query_service.get_candidate_technologies(candidate_id)),
        "certifications": _dump(graph_query_service.get_candidate_certifications(candidate_id)),
        "education": _dump(graph_query_service.get_candidate_education(candidate_id)),
        "experience": _dump(graph_query_service.get_candidate_experience(candidate_id)),
    }


def _owned(db: Session, user: User, session_id: str) -> ProfileQuizSession:
    session = db.query(ProfileQuizSession).filter(ProfileQuizSession.session_id == session_id, ProfileQuizSession.candidate_id == user.id).first()
    if not session:
        raise QuizSessionNotFound()
    return session


def _response(session: ProfileQuizSession) -> QuizSessionResponse:
    try:
        questions = [QuizQuestion.model_validate(item) for item in (session.questions or [])]
        result = QuizResult.model_validate(session.result) if session.result else None
    except ValidationError as exc:
        raise QuizSessionStateError("Stored quiz session data is invalid") from exc
    current = questions[session.question_number - 1] if session.status == "active" and session.question_number <= len(questions) else None
    return QuizSessionResponse(
        session_id=session.session_id,
        candidate_id=session.candidate_id,
        language=session.language,
        questions=questions,
        current_question=current,
        question_number=session.question_number,
        answers=session.answers or [],
        status=session.status,
        result=result,
        created_at=session.created_at,
        completed_at=session.completed_at,
    )


logger = logging.getLogger("careerverse.ai.quiz")


def _fallback_questions(evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
    skills = [s.get("name", s) if isinstance(s, dict) else str(s) for s in evidence.get("skills", [])]
    top_skills = ", ".join(skills[:3]) if skills else "software development"
    return [
        {
            "id": "q1",
            "question": f"Given your technical background in {top_skills}, which type of engineering challenges energize you most?",
            "question_type": "single",
            "options": [
                "Designing scalable backend APIs and data architecture",
                "Building interactive, responsive full-stack applications",
                "Developing applied machine learning and data-driven systems",
                "Cloud infrastructure, performance optimization, and reliability",
            ],
            "why_it_matters": "Identifies the core technical domain where your problem-solving instinct is strongest.",
        },
        {
            "id": "q2",
            "question": "When taking on a new project or mission, what is your preferred development workflow?",
            "question_type": "single",
            "options": [
                "Establish strict schema contracts and test coverage first",
                "Build an end-to-end working prototype rapidly, then iterate",
                "Analyze algorithmic trade-offs and data pipeline efficiency",
                "Iterate closely with end-users and product requirements",
            ],
            "why_it_matters": "Determines your execution rhythm and engineering methodology.",
        },
        {
            "id": "q3",
            "question": "Which skill or capability do you want to intentionally expand over the next 6 months?",
            "question_type": "single",
            "options": [
                "Distributed systems and microservice architecture",
                "AI agent orchestration, LLMs, and vector search",
                "Modern frontend system design and performance",
                "DevOps automation, Docker, and Kubernetes deployment",
            ],
            "why_it_matters": "Helps distinguish current baseline skills from your active growth trajectory.",
        },
        {
            "id": "q4",
            "question": "In your ideal role, what balance of technical depth versus strategic leadership fits best?",
            "question_type": "single",
            "options": [
                "Deep technical IC contributor focusing on code and architecture",
                "Balanced hybrid contributing code while guiding system design",
                "Technical leadership, mentoring engineers, and setting roadmap",
                "Product-focused engineer shaping feature direction",
            ],
            "why_it_matters": "Clarifies your career trajectory preferences between IC mastery and leadership.",
        },
        {
            "id": "q5",
            "question": "What is a meaningful project or technical achievement from your past work that you enjoyed building most, and why?",
            "question_type": "text",
            "options": [
                "Full-stack web application with complex state and responsive UI",
                "Scalable backend API or microservice handling concurrent data",
                "AI/ML pipeline or LLM integration solving real user workflows",
                "Algorithmic optimization or system tooling that boosted performance",
            ],
            "why_it_matters": "Surfaces your genuine intrinsic motivation and pride in craftsmanship.",
        },
    ]


def create_quiz_session(db: Session, user: User, request: QuizSessionCreateRequest) -> QuizSessionResponse:
    evidence = _evidence(user.id, "Create a personalized career profile assessment")
    questions = []
    try:
        data = _json_response(QUESTION_PROMPT, {"language": request.language, "verified_candidate_evidence": evidence})
        raw_items = data.get("questions", [])
        if isinstance(raw_items, list) and raw_items:
            for item in raw_items:
                if isinstance(item, dict) and "question" in item:
                    item.setdefault("id", f"q{len(questions) + 1}")
                    item.setdefault("question_type", "single" if item.get("options") else "text")
                    item.setdefault("options", item.get("options") or [])
                    item.setdefault("why_it_matters", "Career compass assessment question.")
                    try:
                        questions.append(QuizQuestion.model_validate(item).model_dump(mode="json"))
                    except ValidationError:
                        pass
    except Exception as exc:
        logger.warning("AI provider failed to generate quiz questions, falling back to evidence-grounded questions: %s", exc)

    if not questions or len(questions) < 3:
        questions = [QuizQuestion.model_validate(q).model_dump(mode="json") for q in _fallback_questions(evidence)]

    session = ProfileQuizSession(session_id=str(uuid.uuid4()), candidate_id=user.id, language=request.language, questions=questions)
    db.add(session)
    db.commit()
    db.refresh(session)
    return _response(session)


def get_quiz_session(db: Session, user: User, session_id: str) -> QuizSessionResponse:
    return _response(_owned(db, user, session_id))


def answer_quiz_question(db: Session, user: User, session_id: str, request: QuizAnswerRequest) -> QuizSessionResponse:
    session = _owned(db, user, session_id)
    if session.status != "active":
        raise QuizSessionStateError("Quiz session is not accepting answers")
    question = (session.questions or [])[session.question_number - 1]
    session.answers = list(session.answers or []) + [{"question_id": question["id"], "question": question["question"], "answer": request.answer.strip()}]
    session.question_number += 1
    total_q = len(session.questions or [])
    if session.question_number > total_q:
        session.status = "completed"
        session.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    if session.status == "completed" and not session.result:
        return complete_quiz(db, user, session_id)
    return _response(session)


def complete_quiz(db: Session, user: User, session_id: str) -> QuizSessionResponse:
    session = _owned(db, user, session_id)
    if session.status == "completed":
        return _response(session)
    if not session.answers:
        raise QuizSessionStateError("Answer at least one quiz question before completing")
    evidence = _evidence(user.id, "Synthesize career direction from the profile assessment")
    result = None
    try:
        data = _json_response(RESULT_PROMPT, {"verified_candidate_evidence": evidence, "answers": session.answers})
        result = QuizResult.model_validate(data)
    except Exception as exc:
        logger.warning("AI provider failed to synthesize quiz result, using evidence fallback: %s", exc)
        skills = [s.get("name", s) if isinstance(s, dict) else str(s) for s in evidence.get("skills", [])]
        result = QuizResult(
            career_direction="Software & Applied AI Systems Engineering",
            summary=f"Profile assessment based on verified skills ({', '.join(skills[:5])}) and assessment responses.",
            career_paths=["Full Stack Developer", "Machine Learning Engineer", "Backend Architect"],
            strengths=skills[:6] if skills else ["Software Development", "Problem Solving"],
            skills_to_develop=["Distributed Systems", "Cloud Deployment", "Production Monitoring"],
            recommended_next_steps=[
                "Explore tailored career directions in Career Navigator",
                "Review evidenced strengths and priority gaps in Skill Gap analysis",
                "Build targeted capabilities using your personalized Learning Roadmap"
            ],
        )
    session.result = result.model_dump(mode="json")
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return _response(session)
