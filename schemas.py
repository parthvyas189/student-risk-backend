from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# --- Student Schemas ---
class StudentBase(BaseModel):
    name: str
    roll_number: str
    contact_email: Optional[str] = None
    teacher_id: int 

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    class Config:
        from_attributes = True

# --- Weekly Metrics Schemas ---
class WeeklyMetricInput(BaseModel):
    student_id: int
    week_start_date: date
    attendance_score: int
    homework_submission_rate: int
    behavior_flag: bool = False
    test_score_average: float

class WeeklyMetricResponse(WeeklyMetricInput):
    id: int
    class Config:
        from_attributes = True

# --- Risk Analysis Schemas ---

# 1. Immediate Response (After POST)
class RiskAnalysisResponse(BaseModel):
    metric_id: int
    student_id: int
    risk_score: float
    risk_level: str
    risk_reasons: List[str]

# 2. Historical Response (For GET /dashboard)
class RiskHistoryItem(BaseModel):
    id: int
    analysis_date: date
    risk_score: float
    risk_level: str
    risk_reasons: str # Sending as JSON string for simplicity

    class Config:
        from_attributes = True