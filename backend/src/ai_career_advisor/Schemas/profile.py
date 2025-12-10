from pydantic import BaseModel, Field
from typing import Optional, List

class ProfileBase(BaseModel):
    class_level: Optional[str] = Field(None, description="class_10 / class_12")
    location: Optional[str] = None
    language: Optional[str] = None
    known_interests: Optional[List[str]] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

