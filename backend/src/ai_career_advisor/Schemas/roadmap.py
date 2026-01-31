from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime


class RoadmapGenerateRequest(BaseModel):
    degree_id: int
    branch_id: int
    career_id: int


class SaveRoadmapRequest(BaseModel):
    name: str
    type: str  
    career_goal: str
    roadmap_data: dict  


class RoadmapListResponse(BaseModel):
    id: int
    name: str
    type: str
    career_goal: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class RoadmapDetailResponse(BaseModel):
    id: int
    name: str
    type: str
    career_goal: str
    roadmap_data: dict
    created_at: datetime
    
    class Config:
        from_attributes = True
