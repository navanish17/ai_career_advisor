from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date


class EntranceExamSearchRequest(BaseModel):
    college_name: str = Field(..., min_length=3, max_length=300)
    degree: str = Field(..., min_length=2, max_length=100)
    branch: Optional[str] = Field(None, max_length=200)


class EntranceExamResponse(BaseModel):
    id: int
    exam_name: str
    exam_full_name: Optional[str]
    conducting_body: Optional[str]
    exam_date: Optional[str]
    registration_start_date: Optional[str]
    registration_end_date: Optional[str]
    exam_pattern: Optional[str]
    official_website: Optional[str]
    syllabus_link: Optional[str]
    academic_year: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class CreateAlertRequest(BaseModel):
    user_email: EmailStr
    college_name: str = Field(..., min_length=3, max_length=300)
    degree: str = Field(..., min_length=2, max_length=100)
    branch: Optional[str] = Field(None, max_length=200)
    alert_types: list[str] = Field(
        default=["registration_start", "registration_3days", "registration_last", "exam_1day"],
        description="Alert types to create"
    )


class AlertResponse(BaseModel):
    id: int
    user_email: str
    entrance_exam_id: int
    alert_type: str
    alert_date: str
    is_sent: bool
    college_name: Optional[str]
    degree: Optional[str]
    branch: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class AdmissionAlertSuccessResponse(BaseModel):
    success: bool = True
    message: str
    exam: EntranceExamResponse
    alert: Optional[AlertResponse] = None
