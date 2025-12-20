from pydantic import BaseModel
from typing import Optional

class CareerResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    market_trend: Optional[str] = None
    salary_range: Optional[str] = None

    class Config:
        from_attributes = True
