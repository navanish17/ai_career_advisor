from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List

from ai_career_advisor.models.quiz_question import QuizQuestion
from ai_career_advisor.Schemas.quiz import QuizSubmitRequest, QuizResultResponse
from ai_career_advisor.core.logger import logger
from ai_career_advisor.models.profile import Profile



# Stream Mapping (FINAL)
INTEREST_TO_STREAM = {
    "technology": "science",
    "science": "science",
    "commerce": "commerce",
    "arts": "arts",
    "social": "arts",
    "sports": "arts"
}


class QuizService:

    @staticmethod
    async def get_all_questions(db: AsyncSession) -> List[QuizQuestion]:
        logger.info("Fetching all quiz questions")
        result = await db.execute(select(QuizQuestion))
        return result.scalars().all()

    @staticmethod
    async def evaluate_quiz(
    db: AsyncSession,
    payload: QuizSubmitRequest,
    user_id: int
) -> QuizResultResponse:


        logger.info("Evaluating quiz submission")

        # Fetch all questions
        result = await db.execute(select(QuizQuestion))
        questions = {q.id: q for q in result.scalars().all()}

        scores: Dict[str, int] = {}

        # Calculate interest scores
        for answer in payload.answers:
            q_id = answer["question_id"]
            selected_option = answer["selected_option"]

            if q_id not in questions:
                continue

            question = questions[q_id]
            option_key = str(selected_option)

            if option_key not in question.score_mapping:
                continue

            for interest, value in question.score_mapping[option_key].items():
                scores[interest] = scores.get(interest, 0) + value

        if not scores:
            return QuizResultResponse(stream=None)

        # Get top interest
        top_interest = max(scores, key=scores.get)

        # Map interest → stream
        stream = INTEREST_TO_STREAM.get(top_interest)

        logger.info(f"Quiz result → Interest: {top_interest}, Stream: {stream}")

        result = await db.execute(
        select(Profile).where(Profile.user_id == user_id))
        profile = result.scalar_one()

        profile.stream = stream
        await db.commit()

        logger.info(f"Stream '{stream}' saved to profile for user {user_id}")

        return QuizResultResponse(
            stream=stream
        )   
