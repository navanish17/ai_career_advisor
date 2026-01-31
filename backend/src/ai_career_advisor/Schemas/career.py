from pydantic import BaseModel
from typing import Optional

class CareerResponse(BaseModel):
    id: int
    name: str
    branch_id: int
    description: Optional[str] = None
    market_trend: Optional[str] = None
    salary_range: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True
