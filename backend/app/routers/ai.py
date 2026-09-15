from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.errors import (
    AIConfigurationError,
    AIInvalidResponseError,
    AIProviderAuthenticationError,
    AIProviderError,
    AIProviderTimeoutError,
)
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.ai import AITestRequest, AITestResponse
from app.services.ai_service import ai_service


router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/test", response_model=AITestResponse, status_code=status.HTTP_200_OK)
def test_ai(request: AITestRequest, _: User = Depends(get_current_user)) -> AITestResponse:
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