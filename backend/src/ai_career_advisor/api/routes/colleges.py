from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import asyncio

from ai_career_advisor.core.database import get_db
from ai_career_advisor.services.college_service import CollegeService
from ai_career_advisor.services.college_details_service import CollegeDetailsService
from ai_career_advisor.services.college_details_extractor import CollegeStrictGeminiExtractor
from ai_career_advisor.services.college_program_check import CollegeProgramCheckService

router = APIRouter(prefix="/colleges", tags=["Colleges"])

# ✅ Free tier safe settings
PROGRAM_CHECK_BATCH_SIZE = 5  # Batch size for parallel checks
BATCH_DELAY = 4  # Delay between batches (seconds)


class CollegeFinderRequest(BaseModel):
    state: str
    degree: str
    branch: str


class CollegeDetailRequest(BaseModel):
    college_id: int
    degree: str
    branch: str


async def check_programs_in_batches(colleges, degree: str, branch: str):
    """
    Check programs in controlled batches with delays
    Free tier safe: 15 RPM = ~4s per call
    """
    async def check_one(college):
        result = await CollegeProgramCheckService.check(
            college_name=college.name,
            degree=degree,
            branch=branch
        )
        return (college, result)
    
    all_results = []
    total = len(colleges)
    
    for i in range(0, total, PROGRAM_CHECK_BATCH_SIZE):
        batch = colleges[i:i + PROGRAM_CHECK_BATCH_SIZE]
        batch_num = (i // PROGRAM_CHECK_BATCH_SIZE) + 1
        total_batches = (total + PROGRAM_CHECK_BATCH_SIZE - 1) // PROGRAM_CHECK_BATCH_SIZE
        
        print(f"🔍 Processing batch {batch_num}/{total_batches} ({len(batch)} colleges)")
        
        # Process batch in parallel
        batch_results = await asyncio.gather(*[check_one(c) for c in batch])
        all_results.extend(batch_results)
        
        # Delay between batches (NOT after last batch)
        if i + PROGRAM_CHECK_BATCH_SIZE < total:
            print(f"⏳ Waiting {BATCH_DELAY}s before next batch (rate limit safety)")
            await asyncio.sleep(BATCH_DELAY)
    
    return all_results


@router.post("/finder")
async def find_colleges(
    payload: CollegeFinderRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Main search: Returns all offering colleges + FULL details for TOP 1 only
    """
    
    # =============================
    # STEP 1: GET COLLEGES FROM DB
    # =============================
    colleges = await CollegeService.get_top_colleges_by_state(
        db,
        state=payload.state
    )

    if not colleges:
        return {
            "message": f"No colleges found in {payload.state}",
            "offering_colleges": [],
            "not_offering_colleges": []
        }

    print(f"📚 Found {len(colleges)} colleges in {payload.state}")

    # =============================
    # STEP 2: CHECK PROGRAM AVAILABILITY (ALL)
    # =============================
    print(f"🔍 Checking which colleges offer {payload.degree} in {payload.branch}")
    
    program_results = await check_programs_in_batches(
        colleges,
        payload.degree,
        payload.branch
    )

    # Separate offering vs not offering
    offering = [(college, True) for college, offers in program_results if offers]
    not_offering = [(college, False) for college, offers in program_results if not offers]

    print(f"✅ {len(offering)} colleges offer the program")
    print(f"❌ {len(not_offering)} colleges do NOT offer the program")

    # =============================
    # STEP 3: EXTRACT DETAILS FOR TOP 1 ONLY
    # =============================
    offering_results = []

    if offering:
        top_college = offering[0][0]  # Best NIRF rank (already sorted)
        
        # Check cache first
        cached = await CollegeDetailsService.get_cached(
            db,
            college_id=top_college.id,
            degree=payload.degree,
            branch=payload.branch
        )

        if cached:
            print(f"💾 Top college details found in cache: {top_college.name}")
            offering_results.append({
                "id": top_college.id,
                "name": top_college.name,
                "nirf_rank": top_college.nirf_rank,
                "offers_program": True,
                "fees": cached.fees_value,
                "fees_source": cached.fees_source,
                "avg_package": cached.avg_package_value,
                "avg_package_source": cached.avg_package_source,
                "highest_package": cached.highest_package_value,
                "highest_package_source": cached.highest_package_source,
                "entrance_exam": cached.entrance_exam_value,
                "entrance_exam_source": cached.entrance_exam_source,
                "cutoff": cached.cutoff_value,
                "cutoff_source": cached.cutoff_source,
                "status": "full_details_available",
                "source": "cache"
            })
        else:
            print(f"📊 Extracting details for TOP college: {top_college.name}")
            
            extracted = await CollegeStrictGeminiExtractor.extract(
                college_name=top_college.name,
                degree=payload.degree,
                branch=payload.branch
            )

            if "error" in extracted:
                print(f"⚠️ Error extracting details: {extracted.get('error')}")
                offering_results.append({
                    "id": top_college.id,
                    "name": top_college.name,
                    "nirf_rank": top_college.nirf_rank,
                    "offers_program": True,
                    "status": "details_extraction_failed",
                    "error": extracted.get("error")
                })
            else:
                # Save to cache
                saved = await CollegeDetailsService.save_from_extraction(
                    db,
                    college_id=top_college.id,
                    degree=payload.degree,
                    branch=payload.branch,
                    extracted=extracted
                )

                offering_results.append({
                    "id": top_college.id,
                    "name": top_college.name,
                    "nirf_rank": top_college.nirf_rank,
                    "offers_program": True,
                    "fees": saved.fees_value,
                    "fees_source": saved.fees_source,
                    "avg_package": saved.avg_package_value,
                    "avg_package_source": saved.avg_package_source,
                    "highest_package": saved.highest_package_value,
                    "highest_package_source": saved.highest_package_source,
                    "entrance_exam": saved.entrance_exam_value,
                    "entrance_exam_source": saved.entrance_exam_source,
                    "cutoff": saved.cutoff_value,
                    "cutoff_source": saved.cutoff_source,
                    "status": "full_details_available",
                    "source": "gemini_fresh"
                })

                print(f"✅ Details saved to cache for {top_college.name}")

        # =============================
        # REMAINING COLLEGES (No details yet)
        # =============================
        for college, _ in offering[1:]:  # Skip first (already processed)
            offering_results.append({
                "id": college.id,
                "name": college.name,
                "nirf_rank": college.nirf_rank,
                "offers_program": True,
                "status": "details_available_on_request",
                "message": "Click 'Get Details' to fetch information"
            })

    # =============================
    # NOT OFFERING COLLEGES
    # =============================
    not_offering_results = [
        {
            "id": college.id,
            "name": college.name,
            "nirf_rank": college.nirf_rank,
            "offers_program": False,
            "reason": f"Does not offer {payload.degree} in {payload.branch}"
        }
        for college, _ in not_offering
    ]

    return {
        "total_colleges_checked": len(colleges),
        "offering_count": len(offering),
        "not_offering_count": len(not_offering),
        "offering_colleges": offering_results,
        "not_offering_colleges": not_offering_results[:10],  # Limit to 10
        "message": f"✅ Found {len(offering)} colleges offering {payload.degree} in {payload.branch}. Full details provided for top college."
    }


@router.post("/details")
async def get_college_details(
    payload: CollegeDetailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    On-demand details: Get full info for a specific college
    (Used when user clicks 'Get Details' on remaining colleges)
    """
    
    # =============================
    # STEP 1: CHECK CACHE
    # =============================
    cached = await CollegeDetailsService.get_cached(
        db,
        college_id=payload.college_id,
        degree=payload.degree,
        branch=payload.branch
    )

    if cached:
        print(f"💾 Details found in cache for college_id={payload.college_id}")
        return {
            "college_id": payload.college_id,
            "degree": payload.degree,
            "branch": payload.branch,
            "fees": cached.fees_value,
            "fees_source": cached.fees_source,
            "fees_extracted_text": cached.fees_extracted_text,
            "avg_package": cached.avg_package_value,
            "avg_package_source": cached.avg_package_source,
            "avg_package_extracted_text": cached.avg_package_extracted_text,
            "highest_package": cached.highest_package_value,
            "highest_package_source": cached.highest_package_source,
            "highest_package_extracted_text": cached.highest_package_extracted_text,
            "entrance_exam": cached.entrance_exam_value,
            "entrance_exam_source": cached.entrance_exam_source,
            "entrance_exam_extracted_text": cached.entrance_exam_extracted_text,
            "cutoff": cached.cutoff_value,
            "cutoff_source": cached.cutoff_source,
            "cutoff_extracted_text": cached.cutoff_extracted_text,
            "source": "cache"
        }

    # =============================
    # STEP 2: GET COLLEGE INFO
    # =============================
    from ai_career_advisor.models.college import College
    from sqlalchemy import select
    
    result = await db.execute(
        select(College).where(College.id == payload.college_id)
    )
    college = result.scalars().first()

    if not college:
        raise HTTPException(status_code=404, detail="College not found")

    # =============================
    # STEP 3: EXTRACT FROM GEMINI
    # =============================
    print(f"📊 Extracting details for {college.name} (on-demand request)")
    
    extracted = await CollegeStrictGeminiExtractor.extract(
        college_name=college.name,
        degree=payload.degree,
        branch=payload.branch
    )

    if "error" in extracted:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract details: {extracted.get('error')}"
        )

    # =============================
    # STEP 4: SAVE TO CACHE
    # =============================
    saved = await CollegeDetailsService.save_from_extraction(
        db,
        college_id=payload.college_id,
        degree=payload.degree,
        branch=payload.branch,
        extracted=extracted
    )

    print(f"✅ Details saved to cache for {college.name}")

    return {
        "college_id": payload.college_id,
        "college_name": college.name,
        "degree": payload.degree,
        "branch": payload.branch,
        "fees": saved.fees_value,
        "fees_source": saved.fees_source,
        "fees_extracted_text": saved.fees_extracted_text,
        "avg_package": saved.avg_package_value,
        "avg_package_source": saved.avg_package_source,
        "avg_package_extracted_text": saved.avg_package_extracted_text,
        "highest_package": saved.highest_package_value,
        "highest_package_source": saved.highest_package_source,
        "highest_package_extracted_text": saved.highest_package_extracted_text,
        "entrance_exam": saved.entrance_exam_value,
        "entrance_exam_source": saved.entrance_exam_source,
        "entrance_exam_extracted_text": saved.entrance_exam_extracted_text,
        "cutoff": saved.cutoff_value,
        "cutoff_source": saved.cutoff_source,
        "cutoff_extracted_text": saved.cutoff_extracted_text,
        "source": "gemini_fresh"
    }
