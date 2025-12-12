from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List 
from database import get_db, engine
import models, schemas, model_client
import json

# Sync models
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Risk API")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Student Risk Backend is Online"}

# --- Student Endpoints ---
@app.post("/students/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(
        name=student.name,
        roll_number=student.roll_number,
        contact_email=student.contact_email,
        teacher_id=student.teacher_id 
    )
    try:
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating student: {str(e)}")

@app.get("/students/", response_model=List[schemas.StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    """Fetch all students to display in a dropdown"""
    return db.query(models.Student).all()

# --- Risk & Metrics Endpoints ---

# 1. SUBMIT Data (POST) - Returns immediate analysis
@app.post("/metrics/", response_model=schemas.RiskAnalysisResponse)
async def submit_weekly_data(data: schemas.WeeklyMetricInput, db: Session = Depends(get_db)):
    
    # Check if entry already exists for this student and week
    existing_metric = db.query(models.WeeklyMetrics).filter(
        models.WeeklyMetrics.student_id == data.student_id,
        models.WeeklyMetrics.week_start_date == data.week_start_date
    ).first()

    if existing_metric:
        # Update existing record
        existing_metric.attendance_score = data.attendance_score
        existing_metric.homework_submission_rate = data.homework_submission_rate
        existing_metric.behavior_flag = data.behavior_flag
        existing_metric.test_score_average = data.test_score_average
        db_metric = existing_metric
    else:
        # Create new record
        db_metric = models.WeeklyMetrics(
            student_id=data.student_id,
            week_start_date=data.week_start_date,
            attendance_score=data.attendance_score,
            homework_submission_rate=data.homework_submission_rate,
            behavior_flag=data.behavior_flag,
            test_score_average=data.test_score_average
        )
        db.add(db_metric)
    
    try:
        db.commit()
        db.refresh(db_metric)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database Error: {str(e)}")

    # Call Model
    prediction = await model_client.get_risk_prediction(
        student_id=data.student_id,
        attendance=data.attendance_score,
        homework=data.homework_submission_rate,
        test_score=data.test_score_average,
        behavior=data.behavior_flag
    )

    # Save Prediction
    reasons_str = json.dumps(prediction.get("risk_reasons", []))
    
    # Check if risk prediction exists for this date/student to avoid duplicate risk entries too (optional but cleaner)
    # For now, just adding new prediction is fine as history, or we could update similarly.
    # Let's keep adding new risk predictions to track changes over time even for same week updates.
    
    db_risk = models.RiskPrediction(
        student_id=data.student_id,
        analysis_date=data.week_start_date,
        risk_score=prediction.get("risk_score", 0.0),
        risk_level=prediction.get("risk_level", "Unknown"),
        risk_reasons=reasons_str
    )
    
    try:
        db.add(db_risk)
        db.commit()
    except Exception as e:
        print(f"Warning: Failed to save risk prediction: {e}")

    return {
        "metric_id": db_metric.id,
        "student_id": data.student_id,
        "risk_score": db_risk.risk_score,
        "risk_level": db_risk.risk_level,
        "risk_reasons": prediction.get("risk_reasons", [])
    }

# 2. VIEW History (GET) - Fetches past records from DB
@app.get("/students/{student_id}/history", response_model=List[schemas.RiskHistoryItem])
def get_student_risk_history(student_id: int, db: Session = Depends(get_db)):
    """
    Returns the list of all past risk assessments for a student.
    Useful for plotting graphs on the frontend.
    """
    history = db.query(models.RiskPrediction)\
                .filter(models.RiskPrediction.student_id == student_id)\
                .order_by(models.RiskPrediction.analysis_date.desc())\
                .all()
    
    if not history:
        return []
        
    return history

# --- NEW: Get Raw Metrics (For Averages) ---
@app.get("/students/{student_id}/metrics", response_model=List[schemas.WeeklyMetricResponse])
def get_student_metrics(student_id: int, db: Session = Depends(get_db)):
    """Returns raw weekly data to calculate averages on frontend"""
    metrics = db.query(models.WeeklyMetrics)\
                .filter(models.WeeklyMetrics.student_id == student_id)\
                .order_by(models.WeeklyMetrics.week_start_date.desc())\
                .all()
    return metrics

# --- Login Endpoint ---
from pydantic import BaseModel
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    id: int
    email: str
    role: str
    full_name: str

@app.post("/login", response_model=LoginResponse)
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(models.User).filter(models.User.email == creds.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Simple password check (In production, use bcrypt.verify(creds.password, user.password_hash))
    # For now, we assume the DB stores plain text or we just compare strings
    if user.password_hash != creds.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)