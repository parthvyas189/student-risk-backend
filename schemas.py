from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# --- Student Schemas ---
class StudentBase(BaseModel):
    name: str
    roll_number: str
    contact_email: Optional[str] = None
    teacher_id: int # We manually assign this for now

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    class Config:
        from_attributes = True

# --- Weekly Metrics Schemas ---
class MetricCreate(BaseModel):
    student_id: int
    week_start_date: date
    attendance_score: int
    homework_submission_rate: int
    behavior_flag: bool = False
    test_score_average: float