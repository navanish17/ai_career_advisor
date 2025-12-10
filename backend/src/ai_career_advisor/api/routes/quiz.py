from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.core.database import get_db
from ai_career_advisor.core.security import get_current_user
from ai_career_advisor.services.quiz_service import QuizService
from ai_career_advisor.Schemas.quiz import (
    QuizQuestionResponse,
    QuizSubmitRequest,
    QuizResultResponse,
)

router = APIRouter()

# GET: Fetch all quiz questions

@router.get("/questions", response_model=list[QuizQuestionResponse])
async def get_quiz_questions(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    questions = await QuizService.get_all_questions(db)
    return questions



# POST: Submit quiz answers

@router.post("/submit", response_model=QuizResultResponse)
async def submit_quiz(
    payload: QuizSubmitRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await QuizService.evaluate_quiz(db, payload)
    return result
