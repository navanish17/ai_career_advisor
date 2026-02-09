import asyncio
import sys
import os
from sqlalchemy import select

# Add backend to path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BACKEND_DIR, 'src'))

from ai_career_advisor.core.database import AsyncSessionLocal
from ai_career_advisor.models.branch import Branch
from ai_career_advisor.models.career import Career
from ai_career_advisor.core.logger import logger

CAREERS = {
    # ========== SCIENCE - BE / BTech ==========
    "Computer / Software": [
        "Software Engineer",
        "Full Stack Developer",
        "DevOps Engineer",
        "Cloud Architect",
        "AI/ML Engineer",
    ],
    "Mechanical / Manufacturing": [
        "Mechanical Engineer",
        "Production Engineer",
        "Design Engineer",
        "Quality Control Engineer",
        "Maintenance Engineer",
    ],
    "Civil / Infrastructure": [
        "Civil Engineer",
        "Structural Engineer",
        "Site Engineer",
        "Project Manager",
        "Quantity Surveyor",
    ],
    "Electrical / Electronics": [
        "Electrical Engineer",
        "Electronics Engineer",
        "Power Systems Engineer",
        "Embedded Systems Engineer",
        "Control Systems Engineer",
    ],
    "Chemical / Process": [
        "Chemical Engineer",
        "Process Engineer",
        "Production Chemist",
        "Quality Assurance Engineer",
        "Safety Officer",
    ],
    
    # ========== SCIENCE - BSc ==========
    "Physics": [
        "Research Scientist",
        "Lab Technician",
        "Data Analyst",
        "Scientific Officer",
        "Physics Teacher",
    ],
    "Chemistry": [
        "Analytical Chemist",
        "Quality Control Analyst",
        "Research Chemist",
        "Lab Analyst",
        "Chemical Technician",
    ],
    "Mathematics": [
        "Data Analyst",
        "Statistician",
        "Operations Research Analyst",
        "Quantitative Analyst",
        "Math Teacher",
    ],
    "Biology": [
        "Research Assistant",
        "Lab Technician",
        "Microbiologist",
        "Environmental Scientist",
        "Biomedical Researcher",
    ],
    
    # ========== SCIENCE - BCA ==========
    "Software Development": [
        "Software Developer",
        "Web Developer",
        "Mobile App Developer",
        "Backend Developer",
        "Frontend Developer",
    ],
    "Data & Analytics": [
        "Data Analyst",
        "Business Intelligence Analyst",
        "Data Scientist",
        "MIS Executive",
        "Reporting Analyst",
    ],
    "Cybersecurity": [
        "Cybersecurity Analyst",
        "Security Operations Analyst",
        "Penetration Tester",
        "Information Security Officer",
        "Network Security Engineer",
    ],
    
    # ========== SCIENCE - MBBS ==========
    "Clinical Medicine": [
        "General Physician",
        "Medical Officer",
        "Resident Doctor",
        "Clinical Associate",
        "Family Medicine Doctor",
    ],
    "Surgery": [
        "Surgeon",
        "Surgical Resident",
        "Assistant Surgeon",
        "Trauma Surgeon",
        "Laparoscopic Surgeon",
    ],
    "Diagnostics & Public Health": [
        "Public Health Officer",
        "Epidemiologist",
        "Clinical Research Coordinator",
        "Medical Data Analyst",
        "Community Health Officer",
    ],
    
    # ========== SCIENCE - BDS ==========
    "Dental Practice": [
        "Dentist",
        "Dental Surgeon",
        "Orthodontist",
        "Endodontist",
        "Dental Consultant",
    ],
    "Oral Surgery": [
        "Oral Surgeon",
        "Maxillofacial Surgeon",
        "Implantologist",
        "Oral Pathologist",
        "Oral Medicine Specialist",
    ],
    "Dental Research": [
        "Dental Researcher",
        "Clinical Research Associate",
        "Dental Product Developer",
        "Academic Researcher",
        "Forensic Odontologist",
    ],
    
    # ========== SCIENCE - BAMS ==========
    "Ayurveda Practice": [
        "Ayurvedic Physician",
        "Ayurveda Consultant",
        "Wellness Practitioner",
        "Ayurvedic Therapist",
        "Panchakarma Specialist",
    ],
    "Panchakarma & Therapy": [
        "Panchakarma Therapist",
        "Ayurvedic Spa Manager",
        "Wellness Therapist",
        "Detox Specialist",
        "Ayurvedic Masseur",
    ],
    "Research & Pharmacology": [
        "Ayurvedic Researcher",
        "Drug Formulation Scientist",
        "Quality Control Analyst",
        "Herbal Product Developer",
        "Pharmacology Researcher",
    ],
    
    # ========== SCIENCE - BHMS ==========
    "Homeopathic Practice": [
        "Homeopathic Physician",
        "Homeopathy Consultant",
        "Clinical Homeopath",
        "Wellness Practitioner",
        "Holistic Health Advisor",
    ],
    "Clinical Research": [
        "Clinical Research Associate",
        "Medical Researcher",
        "Drug Trial Coordinator",
        "Research Analyst",
        "Evidence-Based Medicine Specialist",
    ],
    "Preventive Healthcare": [
        "Preventive Medicine Specialist",
        "Health Educator",
        "Wellness Coach",
        "Community Health Worker",
        "Public Health Consultant",
    ],
    
    # ========== SCIENCE - BSc Nursing ==========
    "Clinical Nursing": [
        "Staff Nurse",
        "Clinical Nurse",
        "ICU Nurse",
        "Emergency Nurse",
        "Surgical Nurse",
    ],
    "Community Health": [
        "Community Health Nurse",
        "Public Health Nurse",
        "School Health Nurse",
        "Occupational Health Nurse",
        "Home Care Nurse",
    ],
    "Nursing Administration": [
        "Nurse Manager",
        "Nursing Supervisor",
        "Nurse Administrator",
        "Quality Assurance Nurse",
        "Clinical Coordinator",
    ],
    
    # ========== SCIENCE - BPT ==========
    "Orthopedic Physiotherapy": [
        "Orthopedic Physiotherapist",
        "Sports Physiotherapist",
        "Musculoskeletal Therapist",
        "Rehabilitation Specialist",
        "Manual Therapist",
    ],
    "Sports Physiotherapy": [
        "Sports Physiotherapist",
        "Athletic Trainer",
        "Sports Injury Specialist",
        "Performance Enhancement Specialist",
        "Fitness Therapist",
    ],
    "Neuro Rehabilitation": [
        "Neuro Physiotherapist",
        "Stroke Rehabilitation Specialist",
        "Pediatric Physiotherapist",
        "Geriatric Therapist",
        "Cardiopulmonary Physiotherapist",
    ],
    
    # ========== SCIENCE - BPharm ==========
    "Pharmaceutical Sciences": [
        "Pharmacist",
        "Clinical Pharmacist",
        "Hospital Pharmacist",
        "Community Pharmacist",
        "Retail Pharmacist",
    ],
    "Clinical Pharmacy": [
        "Clinical Pharmacist",
        "Drug Safety Associate",
        "Pharmacovigilance Officer",
        "Clinical Trial Coordinator",
        "Medical Affairs Executive",
    ],
    "Drug Research & Manufacturing": [
        "Formulation Scientist",
        "Quality Control Analyst",
        "Production Pharmacist",
        "R&D Scientist",
        "Regulatory Affairs Officer",
    ],
    
    # ========== SCIENCE - BArch ==========
    "Architectural Design": [
        "Architect",
        "Design Architect",
        "Project Architect",
        "Landscape Architect",
        "Interior Architect",
    ],
    "Urban Planning": [
        "Urban Planner",
        "City Planner",
        "Town Planner",
        "Transportation Planner",
        "Environmental Planner",
    ],
    "Construction Technology": [
        "Construction Manager",
        "Site Architect",
        "Building Consultant",
        "Construction Project Manager",
        "Structural Coordinator",
    ],
    
    # ========== COMMERCE - BCom ==========
    "Accounting": [
        "Accountant",
        "Tax Consultant",
        "Accounts Executive",
        "Junior Auditor",
        "Accounts Manager",
    ],
    "Finance": [
        "Financial Analyst",
        "Finance Executive",
        "Investment Analyst",
        "Credit Analyst",
        "Treasury Executive",
    ],
    "Banking & Insurance": [
        "Bank Officer",
        "Insurance Advisor",
        "Relationship Manager",
        "Loan Officer",
        "Claims Officer",
    ],
    
    # ========== COMMERCE - BBA ==========
    "Management": [
        "Management Trainee",
        "Business Analyst",
        "Operations Manager",
        "Project Coordinator",
        "Administrative Manager",
    ],
    "Marketing": [
        "Marketing Executive",
        "Brand Manager",
        "Digital Marketing Specialist",
        "Sales Manager",
        "Market Research Analyst",
    ],
    "Human Resources": [
        "HR Executive",
        "Talent Acquisition Specialist",
        "HR Business Partner",
        "Training Coordinator",
        "Recruitment Manager",
    ],
    
    # ========== COMMERCE - BMS ==========
    "Business Management": [
        "Business Manager",
        "Operations Executive",
        "Strategy Consultant",
        "Management Consultant",
        "Business Development Manager",
    ],
    "Operations": [
        "Operations Manager",
        "Supply Chain Analyst",
        "Logistics Coordinator",
        "Process Improvement Specialist",
        "Quality Manager",
    ],
    "Strategy": [
        "Strategy Analyst",
        "Business Strategy Manager",
        "Corporate Planning Executive",
        "Growth Manager",
        "Strategic Consultant",
    ],
    
    # ========== COMMERCE - BAF ==========
    "Financial Analysis": [
        "Financial Analyst",
        "Investment Analyst",
        "Equity Research Analyst",
        "Budget Analyst",
        "Credit Risk Analyst",
    ],
    "Auditing": [
        "Internal Auditor",
        "External Auditor",
        "Compliance Officer",
        "Risk Auditor",
        "Forensic Auditor",
    ],
    
    # ========== COMMERCE - BFM ==========
    "Financial Markets": [
        "Stock Broker",
        "Equity Trader",
        "Derivatives Trader",
        "Market Analyst",
        "Portfolio Manager",
    ],
    "Investment": [
        "Investment Banker",
        "Investment Advisor",
        "Asset Manager",
        "Fund Manager",
        "Venture Capital Analyst",
    ],
    "Risk Management": [
        "Risk Manager",
        "Risk Analyst",
        "Compliance Manager",
        "Operational Risk Analyst",
        "Market Risk Analyst",
    ],
    
    # ========== COMMERCE - BBI ==========
    "Banking Operations": [
        "Banking Operations Manager",
        "Branch Manager",
        "Credit Officer",
        "Loan Processing Officer",
        "Banking Service Executive",
    ],
    "Insurance Management": [
        "Insurance Underwriter",
        "Claims Manager",
        "Insurance Sales Manager",
        "Actuarial Analyst",
        "Insurance Broker",
    ],
    "Financial Services": [
        "Financial Advisor",
        "Wealth Manager",
        "Financial Planner",
        "Client Relationship Manager",
        "Investment Consultant",
    ],
    
    # ========== ARTS - BA ==========
    "Humanities": [
        "Content Writer",
        "Research Assistant",
        "Policy Analyst",
        "Academic Coordinator",
        "Heritage Manager",
    ],
    "Social Sciences": [
        "Social Researcher",
        "NGO Program Manager",
        "Development Officer",
        "Survey Analyst",
        "Community Organizer",
    ],
    "Languages": [
        "Translator",
        "Content Writer",
        "Language Teacher",
        "Editorial Assistant",
        "Localization Specialist",
    ],
    
    # ========== ARTS - BFA ==========
    "Fine Arts": [
        "Visual Artist",
        "Illustrator",
        "Art Teacher",
        "Gallery Curator",
        "Art Director",
    ],
    "Visual Design": [
        "Graphic Designer",
        "UI/UX Designer",
        "Visual Designer",
        "Brand Designer",
        "Motion Graphics Designer",
    ],
    "Performing Arts": [
        "Theater Artist",
        "Choreographer",
        "Performing Artist",
        "Dance Teacher",
        "Cultural Program Coordinator",
    ],
    
    # ========== ARTS - BSW ==========
    "Social Work Practice": [
        "Social Worker",
        "Case Manager",
        "Community Outreach Worker",
        "Family Counselor",
        "Child Welfare Officer",
    ],
    "Community Development": [
        "Community Development Officer",
        "Rural Development Worker",
        "Program Coordinator",
        "Grassroots Organizer",
        "Development Facilitator",
    ],
    "Welfare Administration": [
        "Welfare Officer",
        "Social Services Administrator",
        "NGO Manager",
        "Policy Coordinator",
        "Grant Manager",
    ],
    
    # ========== ARTS - LLB ==========
    "Legal Practice": [
        "Advocate",
        "Legal Consultant",
        "Litigation Lawyer",
        "Legal Advisor",
        "Court Lawyer",
    ],
    "Corporate Law": [
        "Corporate Lawyer",
        "Legal Counsel",
        "Compliance Officer",
        "Contract Specialist",
        "Mergers & Acquisitions Lawyer",
    ],
    "Criminal & Civil Law": [
        "Criminal Lawyer",
        "Civil Lawyer",
        "Public Prosecutor",
        "Defense Attorney",
        "Judicial Clerk",
    ],
    
    # ========== ARTS - BDes ==========
    "Product Design": [
        "Product Designer",
        "Industrial Designer",
        "UX Designer",
        "Design Engineer",
        "Prototyping Specialist",
    ],
    "UX & Communication Design": [
        "UX Designer",
        "UI Designer",
        "Interaction Designer",
        "Communication Designer",
        "User Researcher",
    ],
    "Fashion & Interior Design": [
        "Fashion Designer",
        "Interior Designer",
        "Textile Designer",
        "Styling Consultant",
        "Space Planner",
    ],
    
    # ========== ARTS - BJMC / BJ / BMM ==========
    "Journalism": [
        "Journalist",
        "Reporter",
        "News Anchor",
        "Content Editor",
        "Investigative Journalist",
    ],
    "Media Production": [
        "Video Producer",
        "Film Editor",
        "Content Producer",
        "Cinematographer",
        "Media Production Manager",
    ],
    "Advertising & Communication": [
        "Advertising Executive",
        "Copywriter",
        "Brand Strategist",
        "Public Relations Officer",
        "Social Media Manager",
    ],
    
    # ========== ARTS - BHM / BSc Hospitality ==========
    "Hotel Operations": [
        "Hotel Manager",
        "Front Office Manager",
        "Housekeeping Manager",
        "Guest Relations Manager",
        "Operations Supervisor",
    ],
    "Tourism & Travel": [
        "Travel Consultant",
        "Tour Manager",
        "Destination Manager",
        "Travel Planner",
        "Tourism Development Officer",
    ],
    "Hospitality Management": [
        "Restaurant Manager",
        "Event Manager",
        "Catering Manager",
        "F&B Manager",
        "Hospitality Consultant",
    ],
}


async def seed_careers():
    async with AsyncSessionLocal() as session:
        added_count = 0
        skipped_count = 0
        missing_branches = []

        logger.info("🚀 Starting career seeding process...")
        
        for branch_name, career_list in CAREERS.items():
            # Find branch by name
            result = await session.execute(
                select(Branch).where(Branch.name == branch_name)
            )
            branch = result.scalars().first()

            if not branch:
                logger.warning(f"⚠️  Branch not found: {branch_name}")
                missing_branches.append(branch_name)
                continue

            logger.info(f"📚 Processing: {branch_name} (ID: {branch.id})")

            for career_name in career_list:
                # Check if career already exists
                exists = await session.execute(
                    select(Career).where(
                        Career.name == career_name,
                        Career.branch_id == branch.id,
                    )
                )
                if exists.scalar_one_or_none():
                    skipped_count += 1
                    continue

                # Add new career
                career = Career(
                    name=career_name,
                    branch_id=branch.id,
                    is_active=True,
                )
                session.add(career)
                added_count += 1

        await session.commit()
        
        # Print summary
        print("\n" + "="*70)
        logger.success(f"✅ Successfully added: {added_count} careers")
        logger.info(f"⏭️  Skipped (already exist): {skipped_count} careers")
        
        if missing_branches:
            logger.warning(f"⚠️  Missing branches ({len(missing_branches)}):")
            for mb in missing_branches:
                print(f"   - {mb}")
        else:
            logger.success("✅ All branches found!")
            
        print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(seed_careers())
