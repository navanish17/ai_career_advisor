from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from ai_career_advisor.Schemas.roadmap import RoadmapGenerateRequest, SaveRoadmapRequest
from ai_career_advisor.services.roadmap_service import RoadmapService
from ai_career_advisor.core.database import get_db
from ai_career_advisor.core.security import get_current_user
from ai_career_advisor.models import Roadmap
from ai_career_advisor.core.logger import logger

router = APIRouter(tags=["Roadmap"])


@router.post("/generate")
async def generate_roadmap(
    payload: RoadmapGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        roadmap_id = await RoadmapService.create_guided_roadmap(
            db=db,
            user_id=current_user.id,
            degree_id=payload.degree_id,
            branch_id=payload.branch_id,
            career_id=payload.career_id
        )
        return {
            "message": "Roadmap generated successfully",
            "roadmap_id": roadmap_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/user")
async def list_user_roadmaps(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all saved roadmaps for current user"""
    result = await db.execute(
        select(Roadmap).where(
            Roadmap.user_id == current_user.id,
            Roadmap.name.isnot(None)  # Only saved roadmaps
        ).order_by(Roadmap.created_at.desc())
    )
    roadmaps = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "name": r.name,
            "type": r.roadmap_type,
            "career_goal": r.career_goal,
            "roadmap_data": r.roadmap_data,
            "created_at": r.created_at.isoformat()
        }
        for r in roadmaps
    ]

@router.get("/{roadmap_id}")
async def get_roadmap(
    roadmap_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        return await RoadmapService.get_roadmap(
            db=db,
            user_id=current_user.id,
            roadmap_id=roadmap_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@router.get("/saved/{roadmap_id}")
async def get_saved_roadmap(
    roadmap_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific saved roadmap by ID"""
    result = await db.execute(
        select(Roadmap).where(
            Roadmap.id == roadmap_id,
            Roadmap.user_id == current_user.id
        )
    )
    roadmap = result.scalars().first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    return {
        "id": roadmap.id,
        "name": roadmap.name,
        "type": roadmap.roadmap_type,
        "career_goal": roadmap.career_goal,
        "roadmap_data": roadmap.roadmap_data,
        "created_at": roadmap.created_at.isoformat()
    }


@router.post("/save")
async def save_roadmap_endpoint(
    payload: SaveRoadmapRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Save a generated roadmap (forward or backward)"""
    try:
        logger.info(f"📝 Saving roadmap - Type: {payload.type}, Name: {payload.name}")
        logger.info(f"📝 Received roadmap_data: {payload.roadmap_data}")
        
        # Convert roadmap_data to dict if needed
        roadmap_data = payload.roadmap_data
        if hasattr(roadmap_data, 'dict'):
            roadmap_data = roadmap_data.dict()
        elif hasattr(roadmap_data, 'model_dump'):
            roadmap_data = roadmap_data.model_dump()
        
        logger.info(f"📝 Converted roadmap_data: {roadmap_data}")
        
        # Extract class_level from roadmap_data if it exists (for forward roadmaps)
        class_level = None
        if isinstance(roadmap_data, dict):
            class_level = roadmap_data.get("class_level")
        
        logger.info(f"📝 Extracted class_level: {class_level}")
        
        roadmap = Roadmap(
            user_id=current_user.id,
            name=payload.name,
            roadmap_type=payload.type,
            career_goal=payload.career_goal,
            class_level=class_level,
            roadmap_data=roadmap_data
        )
        
        logger.info(f"📝 About to save roadmap to DB: {roadmap.__dict__}")
        
        db.add(roadmap)
        await db.commit()
        await db.refresh(roadmap)
        
        logger.success(f"✅ Roadmap saved successfully - ID: {roadmap.id}")
        logger.info(f"✅ Saved roadmap_data: {roadmap.roadmap_data}")
        
        return {
            "message": "Roadmap saved successfully",
            "roadmap_id": roadmap.id
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Error saving roadmap: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save roadmap: {str(e)}")


@router.delete("/roadmap/{roadmap_id}")
async def delete_roadmap_endpoint(
    roadmap_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a saved roadmap"""
    result = await db.execute(
        select(Roadmap).where(
            Roadmap.id == roadmap_id,
            Roadmap.user_id == current_user.id
        )
    )
    roadmap = result.scalars().first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    await db.delete(roadmap)
    await db.commit()
    
    return {"message": "Roadmap deleted successfully"}


@router.post("/{roadmap_id}/share")
async def share_roadmap(
    roadmap_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate a public share link for a roadmap"""
    import uuid
    
    # Get roadmap ensuring ownership
    result = await db.execute(
        select(Roadmap).where(
            Roadmap.id == roadmap_id,
            Roadmap.user_id == current_user.id
        )
    )
    roadmap = result.scalars().first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    # Generate token if not exists
    if not roadmap.share_token:
        roadmap.share_token = str(uuid.uuid4())
        await db.commit()
    
    return {
        "share_token": roadmap.share_token,
        "message": "Public link generated"
    }


@router.get("/public/{share_token}")
async def view_shared_roadmap(
    share_token: str,
    db: AsyncSession = Depends(get_db)
):
    """View a shared roadmap (Public access)"""
    result = await db.execute(
        select(Roadmap).where(Roadmap.share_token == share_token)
    )
    roadmap = result.scalars().first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Shared roadmap not found")
    
    return {
        "id": roadmap.id,
        "name": roadmap.name,
        "type": roadmap.roadmap_type,
        "career_goal": roadmap.career_goal,
        # Roadmap data is safe to share (no PII)
        "roadmap_data": roadmap.roadmap_data, 
        "created_at": roadmap.created_at.isoformat(),
        "is_public": True
    }


@router.delete("/{roadmap_id}/share")
async def unshare_roadmap(
    roadmap_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Revoke public access to a roadmap"""
    result = await db.execute(
        select(Roadmap).where(
            Roadmap.id == roadmap_id,
            Roadmap.user_id == current_user.id
        )
    )
    roadmap = result.scalars().first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    roadmap.share_token = None
    await db.commit()
    
    return {"message": "Roadmap is no longer public"}

