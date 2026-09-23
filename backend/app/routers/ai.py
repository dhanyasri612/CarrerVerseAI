from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.errors import (
    AIConfigurationError,
    AIInvalidResponseError,
    AIProviderAuthenticationError,
    AIProviderError,
    AIProviderTimeoutError,
)
from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.ai import AITestRequest, AITestResponse
from app.schemas.resume_ai import ResumeAIAnalysis
from app.schemas.skill_gap_ai import SkillGapAnalysis, SkillGapRequest
from app.services.skill_gap_ai_service import analyze_skill_gap_with_roadmap
from app.services.resume_ai_service import analyze_resume_intelligence


router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/test", response_model=AITestResponse, status_code=status.HTTP_200_OK)
def test_ai(request: AITestRequest, _: User = Depends(get_current_user)) -> AITestResponse:
    from app.services.ai_service import ai_service

    try:
        result, model = ai_service.test(request.message)
        return AITestResponse(success=result.success, message=result.message, model=model)
    except AIConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AIProviderAuthenticationError as exc:
        raise HTTPException(status_code=502, detail="AI provider authentication failed") from exc
    except AIProviderTimeoutError as exc:
        raise HTTPException(status_code=504, detail="AI provider request timed out") from exc
    except AIInvalidResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail="AI provider request failed") from exc


@router.post(
    "/resume/{resume_id}/analyze",
    response_model=ResumeAIAnalysis,
    status_code=status.HTTP_200_OK,
    summary="Analyze a user's resume with evidence-based AI intelligence",
)
def analyze_resume_ai_endpoint(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return analyze_resume_intelligence(db=db, current_user=current_user, resume_id=resume_id)
    except HTTPException:
        raise
    except AIConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AIProviderAuthenticationError as exc:
        raise HTTPException(status_code=502, detail="AI provider authentication failed") from exc
    except AIProviderTimeoutError as exc:
        raise HTTPException(status_code=504, detail="AI provider request timed out") from exc
    except AIInvalidResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail="AI provider request failed") from exc


@router.post(
    "/skill-gap/analyze",
    response_model=SkillGapAnalysis,
    status_code=status.HTTP_200_OK,
    summary="Analyze evidence-based skill gaps and generate a personalized roadmap",
)
def analyze_skill_gap_ai_endpoint(
    request: SkillGapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return analyze_skill_gap_with_roadmap(
            db=db,
            current_user=current_user,
            request=request,
        )
    except HTTPException:
        raise
    except AIConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AIProviderAuthenticationError as exc:
        raise HTTPException(status_code=502, detail="AI provider authentication failed") from exc
    except AIProviderTimeoutError as exc:
        raise HTTPException(status_code=504, detail="AI provider request timed out") from exc
    except AIInvalidResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail="AI provider request failed") from exc