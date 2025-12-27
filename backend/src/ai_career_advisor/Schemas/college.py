from pydantic import BaseModel
from typing import Optional, List


class CollegeResponse(BaseModel):
    id: int
    name: str
    city: str
    state: str
    nirf_rank: Optional[int]
    website: Optional[str]

    class Config:
        from_attributes = True


class CollegeListResponse(BaseModel):
    count: int
    colleges: List[CollegeResponse]
