from pydantic import BaseModel
from typing import Optional


class DegreeBase(BaseModel):
    name: str
    stream: str
    short_description: Optional[str] = None
    duration_years: Optional[int] = None
    eligibility: Optional[str] = None
    is_active: bool = True


class DegreeCreate(DegreeBase):
    """Used if we want to create degrees manually or via seeder."""
    pass


class DegreeResponse(DegreeBase):
    id: int

    class Config:
        orm_mode = True
