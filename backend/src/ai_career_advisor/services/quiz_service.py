from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List

from ai_career_advisor.models.quiz_question import QuizQuestion
from ai_career_advisor.Schemas.quiz import QuizSubmitRequest, QuizResultResponse
from ai_career_advisor.core.logger import logger


class QuizService:

    @staticmethod
    async def get_all_questions(db:AsyncSession) -> List[QuizQuestion]:
        """it will fetch all the question from the database"""
        logger.info("Fetching all the question from the database")
        result  = await db.execute(select(QuizQuestion))
        return result.scalars().all()
    
    @staticmethod
    async def evaluate_quiz(
        db: AsyncSession,
        payload: QuizSubmitRequest)-> QuizResultResponse:

        logger.info("Evaluating quiz submission...")

        result = await db.execute(select(QuizQuestion))
        questions = {q.id: q for q in result.scalars().all()}

        scores: Dict[str, int] = {}

        for answer in payload.answers:
            q_id = answer["question_id"]
            selected_option = answer["selected_option"]

            if q_id not in questions:
                logger.warning(f"Invalid question_id: {q_id}")
                continue

            question = questions[q_id]

            option_str = str(selected_option)

            if option_str not in question.score_mapping:
                logger.warning(f"Invalid option index: {selected_option} for question {q_id}")
                continue

            option_scores = question.score_mapping[option_str]

            # accumulate score
            for interest, val in option_scores.items():
                scores[interest] = scores.get(interest, 0) + val

        # sort top interests
        sorted_interests = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_interests = [i[0] for i in sorted_interests[:3]]  # top 3

        logger.info(f"Quiz evaluated. Top interests: {top_interests}")

        # Return response (recommendation = None for now)
        return QuizResultResponse(
            top_interests=top_interests,
            scores=scores,
            recommendation=None
        )

