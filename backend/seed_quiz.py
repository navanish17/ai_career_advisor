import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.ai_career_advisor.core.database import AsyncSessionLocal
from src.ai_career_advisor.models.quiz_question import QuizQuestion
from src.ai_career_advisor.core.logger import logger



# 20 Quiz Questions (import your data)

quiz_questions_data = [

    {
        "question_text": "Do you enjoy solving puzzles, logical problems, or brain teasers?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"science": 2, "technology": 2},
            "1": {"science": 1, "technology": 1},
            "2": {}
        }
    },
    {
        "question_text": "Do you like experimenting or finding out how things work?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"science": 2},
            "1": {"science": 1},
            "2": {}
        }
    },
    {
        "question_text": "Do you enjoy writing code or automating simple tasks?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"technology": 3},
            "1": {"technology": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you enjoy creating drawings, designs, or creative projects?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"arts": 3},
            "1": {"arts": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you enjoy playing sports or physical activities?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"sports": 3},
            "1": {"sports": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you feel comfortable speaking in a group or leading people?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"commerce": 2, "social": 2},
            "1": {"social": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you enjoy observing human behavior or helping others solve problems?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"social": 3},
            "1": {"social": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you enjoy working with numbers or analyzing data?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"science": 2, "commerce": 2},
            "1": {"commerce": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you like building or fixing technical things?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"technology": 3},
            "1": {"technology": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you enjoy imagining new ideas, stories, or artworks?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"arts": 3},
            "1": {"arts": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you feel excited when discussing business, marketing, or finance topics?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"commerce": 3},
            "1": {"commerce": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you enjoy competing in games or physical challenges?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"sports": 3},
            "1": {"sports": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you spend time watching scientific or tech-related videos?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"science": 2, "technology": 1},
            "1": {"science": 1},
            "2": {}
        }
    },

    {
        "question_text": "Would you prefer a job where you solve technical problems?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"technology": 3},
            "1": {"technology": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you prefer tasks involving creativity instead of routine work?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"arts": 2},
            "1": {"arts": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you like helping people understand or solve their issues?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"social": 3},
            "1": {"social": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you enjoy making strategies in games or planning things?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"commerce": 2, "technology": 1},
            "1": {"commerce": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you like learning new scientific facts?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"science": 3},
            "1": {"science": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you enjoy participating in team activities?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"sports": 2, "social": 1},
            "1": {"social": 1},
            "2": {}
        }
    },

    {
        "question_text": "Do you like planning or organizing events or group tasks?",
        "options": ["Yes", "Sometimes", "No"],
        "score_mapping": {
            "0": {"commerce": 2, "social": 1},
            "1": {"social": 1},
            "2": {}
        }
    }

]



# SEEDING FUNCTION

async def seed_quiz():
    async with AsyncSessionLocal() as db:  # type: AsyncSession
        
        logger.info("Checking existing quiz questions...")

        result = await db.execute(select(QuizQuestion))
        existing = result.scalars().all()

        if len(existing) > 0:
            logger.warning(f"Quiz already has {len(existing)} questions. Skipping seeding.")
            return

        logger.info("Seeding quiz questions...")

        for q in quiz_questions_data:
            question = QuizQuestion(
                question_text=q["question_text"],
                options=q["options"],
                score_mapping=q["score_mapping"],
            )
            db.add(question)

        await db.commit()
        logger.info("Quiz seeding completed successfully! 🎉")


if __name__ == "__main__":
    asyncio.run(seed_quiz())
    logger.info("Quiz Seeder finished running.")
