from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.leetcode_profile import (
    LeetCodeProfileResponse,
    LeetCodeProblemsResponse,
)
from app.services.leetcode_service import (
    sync_leetcode_profile,
    get_leetcode_profile,
    get_leetcode_problems,
)


router = APIRouter(
    prefix="/leetcode",
    tags=["LeetCode"],
)


@router.post(
    "/sync/{username}",
    response_model=LeetCodeProfileResponse,
)
def sync_profile(
    username: str,
    force: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sync_leetcode_profile(
        db,
        username,
        current_user,
        force=force,
    )


@router.get(
    "/profile",
    response_model=LeetCodeProfileResponse,
)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_leetcode_profile(
        db,
        current_user,
    )


@router.get(
    "/problems",
    response_model=LeetCodeProblemsResponse,
)
def get_problems(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_leetcode_problems(
        db,
        current_user,
    )


@router.get(
    "/dsa-recommendations",
    summary="Generate personalized DSA practice problems and roadmap based on LeetCode & HackerRank",
)
def get_dsa_recommendations(
    target_role: str = Query("Software Developer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.dsa_service import generate_dsa_practice_and_roadmap
    return generate_dsa_practice_and_roadmap(db, current_user, target_role=target_role)


@router.post(
    "/dsa-hint",
    summary="Interactive AI Socratic hint analyzing candidate's DSA code attempt",
)
def get_dsa_hint(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.schemas.dsa_practice import DsaCodeHintRequest
    from app.services.dsa_service import generate_dsa_interactive_hint
    parsed_req = DsaCodeHintRequest(**request)
    return generate_dsa_interactive_hint(parsed_req, current_user)


@router.post(
    "/dsa/generate-rag",
    summary="Generate a brand new coding problem dynamically via RAG grounded in candidate LeetCode history",
)
def generate_rag_problem(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.dsa_service import generate_rag_dsa_problem
    topic = payload.get("topic")
    target_role = payload.get("target_role", "Software Developer")
    difficulty = payload.get("difficulty", "Medium")
    return generate_rag_dsa_problem(
        db,
        current_user,
        topic=topic,
        target_role=target_role,
        difficulty=difficulty,
    )


@router.post(
    "/dsa-evaluate",
    summary="Strictly evaluate and trace candidate DSA code against test cases with real compiler judge",
)
def evaluate_dsa_code(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.schemas.dsa_practice import DsaCodeExecutionRequest
    from app.services.dsa_service import evaluate_dsa_code_submission
    parsed_req = DsaCodeExecutionRequest(**payload)
    return evaluate_dsa_code_submission(parsed_req, current_user)



