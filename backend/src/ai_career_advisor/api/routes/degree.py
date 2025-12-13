from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ai_career_advisor.Schemas.degree import DegreeResponse
from ai_career_advisor.services.degree_service import DegreeService
from ai_career_advisor.core.database import get_db

router = APIRouter(prefix="/api/degree", tags=["degree"])

@router.get("/all", response_model=List[DegreeResponse])
async def get_all_degrees(db: AsyncSession = Depends(get_db)):
    degrees = await DegreeService.get_all_degrees(db)
    return degrees

@router.get("/from-stream/{stream}", response_model=List[DegreeResponse])
async def get_degrees_from_stream(stream: str, db: AsyncSession = Depends(get_db)):
    stream = stream.lower()
    degrees = await DegreeService.get_degrees_by_stream(db, stream)
    if degrees is None:
        return []
    return degrees

