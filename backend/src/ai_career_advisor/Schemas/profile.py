from pydantic import BaseModel
from typing import Optional


class UserProfile(BaseModel):
    class_level: Optional[str] = None  # "10th" / "12th"
    location: Optional[str] = None
    language: Optional[str] = None
    known_interests: Optional[list[str]] = []

    class Config:
        from_attributes = True
