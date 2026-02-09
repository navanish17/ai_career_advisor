import asyncio
import sys
import os
import random
from sqlalchemy import select, delete

# Add backend to path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BACKEND_DIR, 'src'))

from ai_career_advisor.core.database import AsyncSessionLocal
from ai_career_advisor.models.career_attributes import CareerAttributes
from ai_career_advisor.core.logger import logger

# Sample data for CareerAttributes
CAREER_DATA = [
    # --- TECHNOLOGY ---
    {
        "career_name": "Software Engineer",
        "career_category": "Technology",
        "short_description": "Design, develop, and maintain software applications and systems.",
        "required_skills": ["Python", "Java", "JavaScript", "Problem Solving", "Data Structures", "Algorithms"],
        "interest_tags": ["Coding", "Technology", "Building things", "Logic"],
        "personality_fit": ["Analytical", "Logical", "Detail-oriented", "Creative"],
        "min_education": "Graduate",
        "preferred_streams": ["Science", "Computer Science"],
        "required_degrees": ["B.Tech", "BCA", "MCA", "B.Sc CS"],
        "salary_range": "6-12 LPA",
        "min_salary_lpa": 6.0,
        "max_salary_lpa": 25.0,
        "work_style": "Hybrid",
        "difficulty_level": 4,
        "growth_potential": "High",
        "job_availability": "High",
        "top_cities": ["Bangalore", "Hyderabad", "Pune", "Gurgaon"],
        "popularity_score": 0.95
    },
    {
        "career_name": "Data Scientist",
        "career_category": "Data Science",
        "short_description": "Analyze complex data to help organizations make better decisions.",
        "required_skills": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization"],
        "interest_tags": ["Data", "Analysis", "Math", "Predictions"],
        "personality_fit": ["Curious", "Analytical", "Logical"],
        "min_education": "Graduate",
        "preferred_streams": ["Science", "Mathematics", "Statistics"],
        "required_degrees": ["B.Tech", "M.Tech", "M.Sc Statistics"],
        "salary_range": "8-20 LPA",
        "min_salary_lpa": 8.0,
        "max_salary_lpa": 30.0,
        "work_style": "Hybrid",
        "difficulty_level": 5,
        "growth_potential": "High",
        "job_availability": "High",
        "top_cities": ["Bangalore", "Mumbai", "Delhi"],
        "popularity_score": 0.90
    },

    # --- EDUCATION & ACADEMIA ---
    {
        "career_name": "School Teacher",
        "career_category": "Education",
        "short_description": "Teach students at primary or secondary levels in schools.",
        "required_skills": ["Teaching", "Communication", "Patience", "Subject Expertise", "Classroom Management"],
        "interest_tags": ["Teaching", "Helping People", "Children", "Education", "Storytelling"],
        "personality_fit": ["Patient", "Empathetic", "Communicator", "Organized"],
        "min_education": "Graduate",
        "preferred_streams": ["Any"],
        "required_degrees": ["B.Ed", "B.A", "B.Sc"],
        "salary_range": "3-8 LPA",
        "min_salary_lpa": 3.0,
        "max_salary_lpa": 12.0,
        "work_style": "School",
        "difficulty_level": 3,
        "growth_potential": "Medium",
        "job_availability": "High",
        "top_cities": ["All India"],
        "popularity_score": 0.85
    },
    {
        "career_name": "College Professor",
        "career_category": "Education",
        "short_description": "Teach undergraduate and postgraduate students in colleges and universities.",
        "required_skills": ["Research", "Teaching", "Subject Mastery", "Mentoring", "Public Speaking"],
        "interest_tags": ["Research", "Teaching", "Higher Education", "Knowledge sharing"],
        "personality_fit": ["Intellectual", "Academic", "Patient"],
        "min_education": "Postgraduate",
        "preferred_streams": ["Any"],
        "required_degrees": ["PhD", "Master's + NET"],
        "salary_range": "6-15 LPA",
        "min_salary_lpa": 6.0,
        "max_salary_lpa": 25.0,
        "work_style": "University",
        "difficulty_level": 5,
        "growth_potential": "High",
        "job_availability": "Medium",
        "top_cities": ["All Major Cities"],
        "popularity_score": 0.80
    },

    # --- MEDIA & COMMUNICATIONS ---
    {
        "career_name": "Content Writer",
        "career_category": "Media & Communications",
        "short_description": "Write engaging content for websites, blogs, articles, and marketing materials.",
        "required_skills": ["Writing", "Research", "SEO", "Creativity", "Editing"],
        "interest_tags": ["Writing", "Storytelling", "Creativity", "Media", "Literature"],
        "personality_fit": ["Creative", "Curious", "Detail-oriented"],
        "min_education": "Graduate",
        "preferred_streams": ["Arts", "Mass Communication"],
        "required_degrees": ["B.A English", "Journalism"],
        "salary_range": "3-8 LPA",
        "min_salary_lpa": 3.0,
        "max_salary_lpa": 15.0,
        "work_style": "Remote/Hybrid",
        "difficulty_level": 3,
        "growth_potential": "High",
        "job_availability": "High",
        "top_cities": ["Bangalore", "Mumbai", "Remote"],
        "popularity_score": 0.75
    },
    {
        "career_name": "Journalist",
        "career_category": "Media & Communications",
        "short_description": "Investigate and report news stories for newspapers, magazines, TV, or online media.",
        "required_skills": ["Reporting", "Writing", "Investigation", "Communication", "Interviewing"],
        "interest_tags": ["News", "Stories", "Writing", "Public Service", "Travel"],
        "personality_fit": ["Curious", "Bold", "Communicator"],
        "min_education": "Graduate",
        "preferred_streams": ["Mass Communication", "Arts"],
        "required_degrees": ["BJMC", "MJMC"],
        "salary_range": "3-10 LPA",
        "min_salary_lpa": 3.0,
        "max_salary_lpa": 20.0,
        "work_style": "Field/Office",
        "difficulty_level": 4,
        "growth_potential": "Medium",
        "job_availability": "Medium",
        "top_cities": ["Delhi", "Mumbai", "Bangalore"],
        "popularity_score": 0.70
    },
    {
        "career_name": "Author / Novelist",
        "career_category": "Arts & Literature",
        "short_description": "Write fiction or non-fiction books, stories, and novels.",
        "required_skills": ["Creative Writing", "Storytelling", "Imagination", "Discipline", "Language Mastery"],
        "interest_tags": ["Writing", "Storytelling", "Books", "Creativity", "Art"],
        "personality_fit": ["Creative", "Introverted", "Imaginative"],
        "min_education": "Any",
        "preferred_streams": ["Arts", "Literature"],
        "required_degrees": ["Any"],
        "salary_range": "Variable",
        "min_salary_lpa": 0.0,
        "max_salary_lpa": 100.0,
        "work_style": "Remote",
        "difficulty_level": 5,
        "growth_potential": "Variable",
        "job_availability": "Low",
        "top_cities": ["Any"],
        "popularity_score": 0.60
    },

    # --- LAW & PUBLIC SERVICE ---
    {
        "career_name": "Lawyer",
        "career_category": "Legal",
        "short_description": "Advise and represent clients in legal matters.",
        "required_skills": ["Legal Analysis", "Argumentation", "Research", "Negotiation", "Public Speaking"],
        "interest_tags": ["Law", "Justice", "Debate", "Helping People", "Politics"],
        "personality_fit": ["Persuasive", "Analytical", "Ethical"],
        "min_education": "Graduate",
        "preferred_streams": ["Any"],
        "required_degrees": ["LLB", "LLM"],
        "salary_range": "5-20 LPA",
        "min_salary_lpa": 5.0,
        "max_salary_lpa": 50.0,
        "work_style": "Court/Office",
        "difficulty_level": 5,
        "growth_potential": "High",
        "job_availability": "High",
        "top_cities": ["Delhi", "Mumbai", "Bangalore"],
        "popularity_score": 0.85
    },
    {
        "career_name": "IAS Officer",
        "career_category": "Public Service",
        "short_description": "Administrative leadership in the Indian government.",
        "required_skills": ["Administration", "Policy Making", "Leadership", "Diplomacy", "General Knowledge"],
        "interest_tags": ["Society", "Government", "Leadership", "Impact"],
        "personality_fit": ["Leader", "Ethical", "Resilient"],
        "min_education": "Graduate",
        "preferred_streams": ["Any"],
        "required_degrees": ["Any Degree"],
        "salary_range": "7-15 LPA (Plus Perks)",
        "min_salary_lpa": 7.0,
        "max_salary_lpa": 20.0,
        "work_style": "Office/Field",
        "difficulty_level": 5,
        "growth_potential": "High",
        "job_availability": "Low (Competitive)",
        "top_cities": ["All India"],
        "popularity_score": 0.98
    },

    # --- MANAGEMENT & BUSINESS ---
    {
        "career_name": "Product Manager",
        "career_category": "Management",
        "short_description": "Guide the success of a product and lead the cross-functional team that is responsible for improving it.",
        "required_skills": ["Communication", "Leadership", "Strategy", "User Empathy", "Analytics"],
        "interest_tags": ["Business", "Leadership", "Technology", "Strategy"],
        "personality_fit": ["Leader", "Visionary", "Communicator"],
        "min_education": "Postgraduate",
        "preferred_streams": ["Any", "Management"],
        "required_degrees": ["MBA", "B.Tech + MBA"],
        "salary_range": "10-25 LPA",
        "min_salary_lpa": 10.0,
        "max_salary_lpa": 35.0,
        "work_style": "Office",
        "difficulty_level": 4,
        "growth_potential": "High",
        "job_availability": "Medium",
        "top_cities": ["Bangalore", "Gurgaon", "Mumbai"],
        "popularity_score": 0.85
    },
    {
        "career_name": "Human Resources (HR) Manager",
        "career_category": "Management",
        "short_description": "Plan, direct, and coordinate the administrative functions of an organization.",
        "required_skills": ["Communication", "Empathy", "Conflict Resolution", "Recruitment", "Management"],
        "interest_tags": ["People", "Management", "Business", "Psychology"],
        "personality_fit": ["People-oriented", "Organized", "Empathetic"],
        "min_education": "Postgraduate",
        "preferred_streams": ["Any"],
        "required_degrees": ["MBA (HR)", "MSW"],
        "salary_range": "5-15 LPA",
        "min_salary_lpa": 5.0,
        "max_salary_lpa": 25.0,
        "work_style": "Office",
        "difficulty_level": 3,
        "growth_potential": "High",
        "job_availability": "High",
        "top_cities": ["All Major Cities"],
        "popularity_score": 0.70
    },
    {
        "career_name": "Chartered Accountant",
        "career_category": "Finance",
        "short_description": "Manage financial records, audits, and taxation for organizations.",
        "required_skills": ["Accounting", "Taxation", "Auditing", "Finance", "Law"],
        "interest_tags": ["Money", "Numbers", "Business", "Law"],
        "personality_fit": ["Detail-oriented", "Ethical", "Analytical"],
        "min_education": "Professional",
        "preferred_streams": ["Commerce"],
        "required_degrees": ["CA"],
        "salary_range": "7-20 LPA",
        "min_salary_lpa": 7.0,
        "max_salary_lpa": 30.0,
        "work_style": "Office",
        "difficulty_level": 5,
        "growth_potential": "High",
        "job_availability": "High",
        "top_cities": ["Mumbai", "Delhi", "Chennai"],
        "popularity_score": 0.88
    },

    # --- ENGINEERING & DESIGN ---
    {
        "career_name": "Mechanical Engineer",
        "career_category": "Engineering",
        "short_description": "Design, analyze, manufacture, and maintain mechanical systems.",
        "required_skills": ["CAD", "Thermodynamics", "Materials Science", "Problem Solving", "Mathematics"],
        "interest_tags": ["Machines", "Building", "Physics", "Mechanics"],
        "personality_fit": ["Practical", "Analytical", "Hands-on"],
        "min_education": "Graduate",
        "preferred_streams": ["Science", "Engineering"],
        "required_degrees": ["B.Tech Mechanical", "BE"],
        "salary_range": "4-12 LPA",
        "min_salary_lpa": 4.0,
        "max_salary_lpa": 18.0,
        "work_style": "Office/Field",
        "difficulty_level": 4,
        "growth_potential": "Medium",
        "job_availability": "Medium",
        "top_cities": ["Pune", "Chennai", "Delhi"],
        "popularity_score": 0.70
    },
    {
        "career_name": "Civil Engineer",
        "career_category": "Engineering",
        "short_description": "Design and supervise the construction of infrastructure projects.",
        "required_skills": ["AutoCAD", "Structural Analysis", "Project Management", "Mathematics", "Site Management"],
        "interest_tags": ["Construction", "Infrastructure", "Design", "Outdoors"],
        "personality_fit": ["Practical", "Organized", "Resilient"],
        "min_education": "Graduate",
        "preferred_streams": ["Science", "Engineering"],
        "required_degrees": ["B.Tech Civil", "BE"],
        "salary_range": "4-10 LPA",
        "min_salary_lpa": 4.0,
        "max_salary_lpa": 15.0,
        "work_style": "Field",
        "difficulty_level": 4,
        "growth_potential": "Medium",
        "job_availability": "Medium",
        "top_cities": ["Delhi", "Mumbai", "Hyderabad"],
        "popularity_score": 0.65
    },
    {
        "career_name": "Active Architect",
        "career_category": "Architecture",
        "short_description": "Plan and design buildings and other structures.",
        "required_skills": ["Design", "Creativity", "Technical Drawing", "Mathematics", "Problem Solving"],
        "interest_tags": ["Design", "Building", "Art", "Math"],
        "personality_fit": ["Creative", "Practical", "Visionary"],
        "min_education": "Graduate",
        "preferred_streams": ["Science", "Arts"],
        "required_degrees": ["B.Arch"],
        "salary_range": "4-12 LPA",
        "min_salary_lpa": 4.0,
        "max_salary_lpa": 25.0,
        "work_style": "Office/Site",
        "difficulty_level": 4,
        "growth_potential": "High",
        "job_availability": "Medium",
        "top_cities": ["Mumbai", "Bangalore", "Delhi"],
        "popularity_score": 0.75
    },
    {
        "career_name": "UX/UI Designer",
        "career_category": "Design",
        "short_description": "Design user interfaces and experiences for websites and mobile apps.",
        "required_skills": ["Design Tools", "User Research", "Prototyping", "Empathy", "Creativity"],
        "interest_tags": ["Design", "Art", "Technology", "Psychology"],
        "personality_fit": ["Creative", "Empathetic", "Detail-oriented"],
        "min_education": "Graduate",
        "preferred_streams": ["Design", "Arts", "Computer Science"],
        "required_degrees": ["B.Des", "B.Sc Multimedia"],
        "salary_range": "5-15 LPA",
        "min_salary_lpa": 5.0,
        "max_salary_lpa": 20.0,
        "work_style": "Remote",
        "difficulty_level": 3,
        "growth_potential": "High",
        "job_availability": "High",
        "top_cities": ["Bangalore", "Pune", "Mumbai"],
        "popularity_score": 0.75
    },
    
    # --- HEALTHCARE ---
    {
        "career_name": "Doctor (MBBS)",
        "career_category": "Healthcare",
        "short_description": "Diagnose and treat illnesses and injuries.",
        "required_skills": ["Biology", "Diagnosis", "Patient Care", "Empathy", "Stamina"],
        "interest_tags": ["Helping People", "Biology", "Health", "Science"],
        "personality_fit": ["Empathetic", "Dedicated", "Resilient"],
        "min_education": "Postgraduate",
        "preferred_streams": ["Science (PCB)"],
        "required_degrees": ["MBBS", "MD"],
        "salary_range": "10-25 LPA",
        "min_salary_lpa": 10.0,
        "max_salary_lpa": 40.0,
        "work_style": "Hospital",
        "difficulty_level": 5,
        "growth_potential": "High",
        "job_availability": "High",
        "top_cities": ["All Major Cities"],
        "popularity_score": 0.92
    },
    {
        "career_name": "Pharmacist",
        "career_category": "Healthcare",
        "short_description": "Dispense medications and advise patients on their use.",
        "required_skills": ["Pharmacology", "Chemistry", "Attention to Detail", "Communication"],
        "interest_tags": ["Medicine", "Science", "Chemistry", "Helping People"],
        "personality_fit": ["Detail-oriented", "Responsible", "Helpful"],
        "min_education": "Graduate",
        "preferred_streams": ["Science (PCB/PCM)"],
        "required_degrees": ["B.Pharm", "D.Pharm"],
        "salary_range": "3-6 LPA",
        "min_salary_lpa": 3.0,
        "max_salary_lpa": 12.0,
        "work_style": "Pharmacy/Hospital",
        "difficulty_level": 3,
        "growth_potential": "Medium",
        "job_availability": "High",
        "top_cities": ["All India"],
        "popularity_score": 0.65
    },
    {
        "career_name": "Clinical Psychologist",
        "career_category": "Healthcare",
        "short_description": "Diagnose and treat mental, emotional, and behavioral disorders.",
        "required_skills": ["Psychology", "Empathy", "Listening", "Analysis", "Communication"],
        "interest_tags": ["Psychology", "Mental Health", "Helping People", "Mind"],
        "personality_fit": ["Empathetic", "Patient", "Insightful"],
        "min_education": "Postgraduate",
        "preferred_streams": ["Arts", "Science"],
        "required_degrees": ["M.Sc/MA Psychology"],
        "salary_range": "4-10 LPA",
        "min_salary_lpa": 4.0,
        "max_salary_lpa": 20.0,
        "work_style": "Office/Hospital",
        "difficulty_level": 4,
        "growth_potential": "High",
        "job_availability": "Medium",
        "top_cities": ["Major Cities"],
        "popularity_score": 0.70
    }
]

async def seed_career_attributes():
    async with AsyncSessionLocal() as session:
        logger.info("Starting Career Attributes seeding...")
        
        # CLEAR EXISTING DATA
        logger.info("🗑️ Clearing existing career attributes...")
        await session.execute(delete(CareerAttributes))
        await session.commit()
        logger.info("✅ Cleared existing data.")
        
        for data in CAREER_DATA:
            # Check if exists (Redundant now but safe)
            stmt = select(CareerAttributes).where(CareerAttributes.career_name == data['career_name'])
            result = await session.execute(stmt)
            existing_career = result.scalar_one_or_none()

            if existing_career:
                logger.info(f"Skipping existing: {data['career_name']}")
                continue
            
            logger.info(f"Adding: {data['career_name']}")
            career_attr = CareerAttributes(**data)
            session.add(career_attr)
        
        await session.commit()
        logger.info("✅ Career Attributes seeding completed successfully!")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(seed_career_attributes())
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
