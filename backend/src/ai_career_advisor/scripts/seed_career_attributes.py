"""
Seed Data: Career Attributes
Populates initial career attributes for recommendation system
Run: python -m ai_career_advisor.scripts.seed_career_attributes
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from ai_career_advisor.core.database import get_db, engine
from ai_career_advisor.models.career_attributes import CareerAttributes
from ai_career_advisor.core.logger import logger
from sqlalchemy import select


# Career data for Indian students
CAREER_DATA = [
    {
        "career_name": "Software Engineer",
        "career_category": "technology",
        "short_description": "Design, develop, and maintain software applications and systems.",
        "required_skills": ["python", "java", "javascript", "problem_solving", "dsa", "git", "sql"],
        "interest_tags": ["technology", "coding", "innovation", "computers", "logic"],
        "personality_fit": ["analytical", "detail_oriented", "problem_solver", "curious"],
        "min_education": "graduate",
        "preferred_streams": ["science", "computer_science"],
        "required_degrees": ["B.Tech", "BCA", "B.Sc Computer Science", "MCA"],
        "salary_range": "6-25 LPA",
        "min_salary_lpa": 6.0,
        "max_salary_lpa": 25.0,
        "work_style": "hybrid",
        "difficulty_level": 3,
        "growth_potential": "high",
        "job_availability": "high",
        "top_cities": ["Bangalore", "Hyderabad", "Pune", "Chennai", "Delhi NCR"],
        "popularity_score": 0.95
    },
    {
        "career_name": "Data Scientist",
        "career_category": "technology",
        "short_description": "Analyze complex data to help businesses make better decisions using ML and statistics.",
        "required_skills": ["python", "machine_learning", "statistics", "sql", "data_visualization", "deep_learning"],
        "interest_tags": ["technology", "data", "mathematics", "research", "patterns"],
        "personality_fit": ["analytical", "curious", "detail_oriented", "researcher"],
        "min_education": "graduate",
        "preferred_streams": ["science", "computer_science", "statistics"],
        "required_degrees": ["B.Tech", "M.Tech", "M.Sc Statistics", "MBA Analytics"],
        "salary_range": "8-30 LPA",
        "min_salary_lpa": 8.0,
        "max_salary_lpa": 30.0,
        "work_style": "hybrid",
        "difficulty_level": 4,
        "growth_potential": "high",
        "job_availability": "high",
        "top_cities": ["Bangalore", "Mumbai", "Hyderabad", "Delhi NCR"],
        "popularity_score": 0.90
    },
    {
        "career_name": "Chartered Accountant",
        "career_category": "finance",
        "short_description": "Manage financial accounts, auditing, taxation, and business advisory services.",
        "required_skills": ["accounting", "taxation", "auditing", "excel", "financial_analysis", "communication"],
        "interest_tags": ["finance", "numbers", "business", "law", "economics"],
        "personality_fit": ["detail_oriented", "organized", "ethical", "analytical"],
        "min_education": "graduate",
        "preferred_streams": ["commerce"],
        "required_degrees": ["B.Com", "CA Foundation", "CA Intermediate", "CA Final"],
        "salary_range": "7-20 LPA",
        "min_salary_lpa": 7.0,
        "max_salary_lpa": 20.0,
        "work_style": "office",
        "difficulty_level": 5,
        "growth_potential": "high",
        "job_availability": "high",
        "top_cities": ["Mumbai", "Delhi", "Chennai", "Kolkata", "Bangalore"],
        "popularity_score": 0.88
    },
    {
        "career_name": "Doctor (MBBS)",
        "career_category": "healthcare",
        "short_description": "Diagnose and treat illnesses, provide medical care to patients.",
        "required_skills": ["biology", "chemistry", "communication", "empathy", "problem_solving", "patience"],
        "interest_tags": ["healthcare", "biology", "helping_others", "science", "medicine"],
        "personality_fit": ["empathetic", "patient", "dedicated", "calm_under_pressure"],
        "min_education": "12th",
        "preferred_streams": ["science"],
        "required_degrees": ["MBBS", "MD", "MS"],
        "salary_range": "8-25 LPA",
        "min_salary_lpa": 8.0,
        "max_salary_lpa": 25.0,
        "work_style": "office",
        "difficulty_level": 5,
        "growth_potential": "high",
        "job_availability": "high",
        "top_cities": ["All major cities"],
        "popularity_score": 0.92
    },
    {
        "career_name": "Civil Services (IAS/IPS/IFS)",
        "career_category": "government",
        "short_description": "Administrative, police, or foreign services officer serving the nation.",
        "required_skills": ["general_knowledge", "current_affairs", "writing", "communication", "ethics", "leadership"],
        "interest_tags": ["government", "public_service", "leadership", "politics", "nation_building"],
        "personality_fit": ["leader", "ethical", "dedicated", "patient", "resilient"],
        "min_education": "graduate",
        "preferred_streams": ["any"],
        "required_degrees": ["Any Graduation"],
        "salary_range": "7-18 LPA",
        "min_salary_lpa": 7.0,
        "max_salary_lpa": 18.0,
        "work_style": "office",
        "difficulty_level": 5,
        "growth_potential": "high",
        "job_availability": "low",
        "top_cities": ["Delhi", "State Capitals", "District HQs"],
        "popularity_score": 0.85
    },
    {
        "career_name": "Lawyer",
        "career_category": "legal",
        "short_description": "Represent clients in legal matters, provide legal advice and advocacy.",
        "required_skills": ["law", "communication", "research", "argumentation", "critical_thinking", "writing"],
        "interest_tags": ["law", "justice", "debate", "reading", "social_issues"],
        "personality_fit": ["articulate", "logical", "persuasive", "ethical", "detail_oriented"],
        "min_education": "graduate",
        "preferred_streams": ["arts", "commerce", "any"],
        "required_degrees": ["LLB", "BA LLB", "BBA LLB"],
        "salary_range": "5-30 LPA",
        "min_salary_lpa": 5.0,
        "max_salary_lpa": 30.0,
        "work_style": "office",
        "difficulty_level": 4,
        "growth_potential": "high",
        "job_availability": "medium",
        "top_cities": ["Delhi", "Mumbai", "Chennai", "Kolkata", "Bangalore"],
        "popularity_score": 0.78
    },
    {
        "career_name": "Product Manager",
        "career_category": "technology",
        "short_description": "Lead product development, strategy, and roadmap for tech products.",
        "required_skills": ["product_thinking", "communication", "analytics", "leadership", "user_research", "strategy"],
        "interest_tags": ["technology", "business", "strategy", "leadership", "user_experience"],
        "personality_fit": ["strategic", "communicative", "empathetic", "decisive", "organized"],
        "min_education": "graduate",
        "preferred_streams": ["any"],
        "required_degrees": ["B.Tech", "MBA", "BBA", "Any"],
        "salary_range": "12-40 LPA",
        "min_salary_lpa": 12.0,
        "max_salary_lpa": 40.0,
        "work_style": "hybrid",
        "difficulty_level": 4,
        "growth_potential": "high",
        "job_availability": "medium",
        "top_cities": ["Bangalore", "Mumbai", "Delhi NCR", "Hyderabad"],
        "popularity_score": 0.82
    },
    {
        "career_name": "Digital Marketing Specialist",
        "career_category": "marketing",
        "short_description": "Plan and execute online marketing campaigns across digital channels.",
        "required_skills": ["seo", "social_media", "content_marketing", "analytics", "advertising", "creativity"],
        "interest_tags": ["marketing", "social_media", "creativity", "technology", "business"],
        "personality_fit": ["creative", "analytical", "adaptable", "communicative", "trendy"],
        "min_education": "graduate",
        "preferred_streams": ["any"],
        "required_degrees": ["BBA", "B.Com", "Any with certification"],
        "salary_range": "4-15 LPA",
        "min_salary_lpa": 4.0,
        "max_salary_lpa": 15.0,
        "work_style": "hybrid",
        "difficulty_level": 2,
        "growth_potential": "high",
        "job_availability": "high",
        "top_cities": ["Mumbai", "Delhi NCR", "Bangalore", "Hyderabad"],
        "popularity_score": 0.75
    },
    {
        "career_name": "Mechanical Engineer",
        "career_category": "engineering",
        "short_description": "Design, develop, and maintain mechanical systems and machinery.",
        "required_skills": ["cad", "thermodynamics", "mechanics", "problem_solving", "design", "manufacturing"],
        "interest_tags": ["engineering", "machines", "automobiles", "manufacturing", "design"],
        "personality_fit": ["analytical", "practical", "problem_solver", "detail_oriented"],
        "min_education": "graduate",
        "preferred_streams": ["science"],
        "required_degrees": ["B.Tech Mechanical", "Diploma Mechanical"],
        "salary_range": "4-15 LPA",
        "min_salary_lpa": 4.0,
        "max_salary_lpa": 15.0,
        "work_style": "office",
        "difficulty_level": 3,
        "growth_potential": "medium",
        "job_availability": "medium",
        "top_cities": ["Pune", "Chennai", "Bangalore", "Delhi NCR", "Ahmedabad"],
        "popularity_score": 0.72
    },
    {
        "career_name": "Graphic Designer",
        "career_category": "creative",
        "short_description": "Create visual content for digital and print media using design software.",
        "required_skills": ["photoshop", "illustrator", "creativity", "typography", "color_theory", "ui_design"],
        "interest_tags": ["art", "design", "creativity", "visual", "branding"],
        "personality_fit": ["creative", "artistic", "detail_oriented", "trendy", "patient"],
        "min_education": "12th",
        "preferred_streams": ["any"],
        "required_degrees": ["BFA", "B.Design", "Any with certification"],
        "salary_range": "3-12 LPA",
        "min_salary_lpa": 3.0,
        "max_salary_lpa": 12.0,
        "work_style": "hybrid",
        "difficulty_level": 2,
        "growth_potential": "medium",
        "job_availability": "high",
        "top_cities": ["Mumbai", "Delhi", "Bangalore", "Pune"],
        "popularity_score": 0.70
    }
]


async def seed_career_attributes():
    """Seed the career_attributes table with initial data"""
    async for db in get_db():
        try:
            logger.info("🌱 Seeding career attributes...")
            
            for career_data in CAREER_DATA:
                # Check if already exists
                result = await db.execute(
                    select(CareerAttributes).where(
                        CareerAttributes.career_name == career_data["career_name"]
                    )
                )
                existing = result.scalars().first()
                
                if existing:
                    logger.info(f"  ✓ {career_data['career_name']} already exists, skipping")
                    continue
                
                # Create new career
                career = CareerAttributes(**career_data)
                db.add(career)
                logger.info(f"  + Added: {career_data['career_name']}")
            
            await db.commit()
            logger.success(f"✅ Seeded {len(CAREER_DATA)} careers successfully!")
            break
            
        except Exception as e:
            logger.error(f"Seeding error: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_career_attributes())
