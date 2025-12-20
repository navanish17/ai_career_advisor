from pydantic import BaseModel
from typing import List, Dict


class CareerInsightResponse(BaseModel):
    career_id: int
    skills: List[str]
    internships: List[str]
    projects: Dict[str, List[str]]
    programs: List[str]

    class Config:
        from_attributes = True


