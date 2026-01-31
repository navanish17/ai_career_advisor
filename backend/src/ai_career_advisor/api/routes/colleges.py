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


class CheckAvailabilityRequest(BaseModel):
    college_id: int
    degree: str
    branch: str


async def check_programs_in_batches(colleges, degree: str, branch: str, db: AsyncSession):
    """
    Check programs in controlled batches with caching
    Uses database cache to avoid repeated LLM calls
    """
    async def check_one(college):
        result = await CollegeProgramCheckService.check_with_cache(
            db=db,
            college_id=college.id,
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


@router.post("/check-availability")
async def check_availability(
    payload: CheckAvailabilityRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if a specific college offers the program.
    Used for background parallel checking.
    """
    # Get college name first (needed for the check)
    from ai_career_advisor.models.college import College
    from sqlalchemy import select
    
    result = await db.execute(
        select(College).where(College.id == payload.college_id)
    )
    college = result.scalars().first()
    
    if not college:
        raise HTTPException(status_code=404, detail="College not found")

    offers = await CollegeProgramCheckService.check_with_cache(
        db=db,
        college_id=college.id,
        college_name=college.name,
        degree=payload.degree,
        branch=payload.branch
    )
    
    return {
        "id": college.id,
        "offers_program": offers,
        "status": "checked"
    }


@router.post("/finder")
async def find_colleges(
    payload: CollegeFinderRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Main search: FAST RETURN.
    Returns all colleges in state immediately.
    Frontend does background availability checks.
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
            "colleges": []
        }

    print(f"📚 Found {len(colleges)} colleges in {payload.state}")
    
    # Return immediately with pending status
    # Frontend will check availability
    
    results = []
    # Track added college names to prevent duplicates
    added_names = set()
    
    for college in colleges:
        # Normalize name for de-duplication (case-insensitive, strip whitespace)
        norm_name = college.name.strip().lower()
        
        if norm_name not in added_names:
            results.append({
                "id": college.id,
                "name": college.name,
                "nirf_rank": college.nirf_rank,
                "location": f"{college.city}, {college.state}",
                "status": "pending_check",
                "offers_program": None # Unknown yet
            })
            added_names.add(norm_name)

    return {
        "message": f"Found {len(results)} colleges. Checking availability...",
        "total_colleges": len(results),
        "colleges": results
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
    # STEP 1: GET COLLEGE INFO (needed for name even if cached)
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
    # STEP 2: CHECK CACHE
    # =============================
    cached = await CollegeDetailsService.get_cached(
        db,
        college_id=payload.college_id,
        degree=payload.degree,
        branch=payload.branch
    )

    if cached:
        print(f"💾 Details found in cache for college: {college.name}")
        return {
            "id": payload.college_id,
            "name": college.name,
            "nirf_rank": college.nirf_rank,
            "location": f"{college.city}, {college.state}",
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
    # STEP 3: EXTRACT FROM GEMINI
    # =============================
    print(f"📊 Extracting details for {college.name} (on-demand request)")
    
    extracted = await CollegeStrictGeminiExtractor.extract(
        college_name=college.name,
        degree=payload.degree,
        branch=payload.branch
    )

    if "error" in extracted:
        print(f"⚠️ Extraction failed/incomplete for {college.name}: {extracted.get('error')}")
        
        # Determine message based on error type
        error_type = extracted.get("error")
        user_message = "Partial details found."
        
        if error_type == "incomplete_data_after_retries":
             user_message = "Partial details found. Some fields missing."
        elif error_type == "invalid_json_after_retries":
             user_message = "Could not parse college data. Please try again."
        elif error_type == "timeout_exceeded":
             user_message = "Request timed out. Please try again."
        else:
             user_message = "Details temporarily unavailable."

        # Attempt to retrieve any partial data if available
        partial_data = extracted.get("partial_data", {})
        
        def safe_get_val(field):
            val = partial_data.get(field)
            if isinstance(val, dict): return val.get("value")
            return str(val) if val else "Not available"

        return {
            "id": payload.college_id,
            "name": college.name,
            "nirf_rank": college.nirf_rank,
            "location": f"{college.city}, {college.state}",
            "degree": payload.degree,
            "branch": payload.branch,
            # Fill fields with partial data or "Not available"
            "fees": safe_get_val("fees"),
            "fees_source": None, 
            "avg_package": safe_get_val("avg_package"),
            "highest_package": safe_get_val("highest_package"),
            "entrance_exam": safe_get_val("entrance_exam"),
            "cutoff": safe_get_val("cutoff"),
            "source": "gemini_error_fallback",
            "message": user_message
        }

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

    if not saved:
         # This should technically be handled by the error block above if it was an error
         # But if save returned None for some other reason, we handle it here
         raise HTTPException(status_code=500, detail="Failed to save data")

    print(f"✅ Details saved to cache for {college.name}")

    response_data = {
        "id": payload.college_id,
        "name": college.name,
        "nirf_rank": college.nirf_rank,
        "location": f"{college.city}, {college.state}",
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
    
    # Commit database changes
    await db.commit()
    
    return response_data
