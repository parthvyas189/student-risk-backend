from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Float, Enum, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('admin', 'teacher', 'student'), nullable=False)
    full_name = Column(String(150))
    
    # Relationships
    students = relationship("Student", foreign_keys="[Student.user_id]", back_populates="user_account")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    roll_number = Column(String(50), unique=True)
    contact_email = Column(String(100))

    # Relationships
    user_account = relationship("User", foreign_keys=[user_id], back_populates="students")
    weekly_metrics = relationship("WeeklyMetrics", back_populates="student")
    risk_predictions = relationship("RiskPrediction", back_populates="student")

class WeeklyMetrics(Base):
    __tablename__ = "weekly_metrics"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    week_start_date = Column(Date, nullable=False)
    
    attendance_score = Column(Integer)
    homework_submission_rate = Column(Integer)
    behavior_flag = Column(Boolean, default=False)
    test_score_average = Column(Float)

    student = relationship("Student", back_populates="weekly_metrics")

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    analysis_date = Column(Date, nullable=False)
    
    risk_score = Column(Float, nullable=False)
    risk_level = Column(Enum('Low', 'Medium', 'High'), nullable=False)
    risk_reasons = Column(Text)

    student = relationship("Student", back_populates="risk_predictions")