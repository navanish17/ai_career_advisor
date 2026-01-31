import asyncio
from ai_career_advisor.core.database import AsyncSessionLocal
from ai_career_advisor.models.degree import Degree
from ai_career_advisor.services.degree_llm import generate_degree_description

DEGREES = [
    # SCIENCE STREAM
    ("BE / BTech", "science", "12th Science (PCM)", 4),
    ("BSc", "science", "12th Science", 3),
    ("BCA", "science", "12th (Any stream, Maths preferred)", 3),
    ("MBBS", "science", "12th Science (PCB + NEET)", 5.5),
    ("BDS", "science", "12th Science (PCB + NEET)", 5),
    ("BAMS", "science", "12th Science (PCB + NEET)", 5.5),
    ("BHMS", "science", "12th Science (PCB)", 5.5),
    ("BSc Nursing", "science", "12th Science (PCB)", 4),
    ("BPT", "science", "12th Science (PCB)", 4.5),
    ("BPharm", "science", "12th Science (PCB/PCM)", 4),
    ("BArch", "science", "12th Science (PCM + NATA)", 5),
    
    # COMMERCE STREAM
    ("BCom", "commerce", "12th Commerce", 3),
    ("BBA", "commerce", "12th Any Stream", 3),
    ("BMS", "commerce", "12th Any Stream", 3),
    ("BAF", "commerce", "12th Commerce", 3),
    ("BFM", "commerce", "12th Commerce", 3),
    ("BBI", "commerce", "12th Commerce", 3),
    
    # ARTS STREAM
    ("BA", "arts", "12th Any Stream", 3),
    ("BFA", "arts", "12th Any Stream", 4),
    ("BSW", "arts", "12th Any Stream", 3),
    ("LLB", "arts", "Graduation Required", 3),
    ("BDes", "arts", "12th Any Stream", 4),
    ("BJMC / BJ / BMM", "arts", "12th Any Stream", 3),
    ("BHM / BSc Hospitality", "arts", "12th Any Stream", 3),
]

async def seed_degrees_with_llm():
    """Seed degrees with AI-generated descriptions"""
    
    async with AsyncSessionLocal() as session:
        added = 0
        errors = 0
        
        print(" Starting degree seeding with LLM descriptions...\n")
        
        for name, stream, eligibility, duration in DEGREES:
            print(f" Processing: {name}...")
            
            try:
                
                desc = generate_degree_description(name)
                
                
                degree = Degree(
                    name=name,
                    stream=stream,
                    eligibility=eligibility,
                    duration_years=duration,
                    short_description=desc,  
                    is_active=True
                )
                
                session.add(degree)
                await session.commit()
                
                print(f"    Added")
                added += 1
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                errors += 1
                await session.rollback()
        
        print("\n" + "="*60)
        print(f" SUMMARY:")
        print(f"    Successfully added: {added}")
        print(f"    Errors: {errors}")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(seed_degrees_with_llm())
