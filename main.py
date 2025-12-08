from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, engine
import models, schemas

# This command ensures models are synced (good for dev, though we used SQL script)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Risk API")

@app.get("/")
def read_root():
    return {"message": "Student Risk Backend is Running!"}

@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Database connection successful!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- NEW: Create Student Endpoint ---
@app.post("/students/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # 1. Check if teacher exists (Quick hack: we assume teacher_id=1 exists for testing)
    # Ideally, we check foreign keys, but let's try to insert.
    
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
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)