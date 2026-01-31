from pydantic import BaseModel
from typing import List, Dict, Optional  


class CareerInsightResponse(BaseModel):
    career_id: int
    skills: List[str]
    internships: List[str]
    projects: Dict[str, List[str]]
    programs: List[str]
    top_salary: Optional[str] = None  
    class Config:
        from_attributes = True
