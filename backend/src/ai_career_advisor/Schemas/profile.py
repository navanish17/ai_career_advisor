from pydantic import BaseModel
from typing import Optional


class UserProfile(BaseModel):
    class_level: str  # "10th" / "12th"
    location: str  # mandatory 
    language: Optional[str] = None
    known_interests: Optional[list[str]] = []

    class Config:
        from_attributes = True
