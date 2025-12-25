from pydantic import BaseModel, Field
from typing import Optional, List

class ProfileBase(BaseModel):
    class_level: Optional[str] = Field(None, description="class_10 / class_12")
    location: Optional[str] = None
    stream: Optional[str] = None
    language: Optional[str] = None
    known_interests: Optional[List[str]] = None

class StreamUpdateRequest(BaseModel):
    stream: str = Field(..., description="science / commerce / arts")

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ClassLevelUpdateRequest(BaseModel):
    class_level: str = Field(..., description="10th or 12th")

class ProfileResponse(ProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
    