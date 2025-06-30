from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Float, Date
from sqlalchemy.orm import relationship
import enum
import datetime
from .user import db

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class EducationLevel(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    HIGH_SCHOOL = "high_school"
    VOCATIONAL = "vocational"
    COLLEGE = "college"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    OTHER = "other"

class CandidateStatus(enum.Enum):
    NEW = "new"
    SCREENING = "screening"
    INTERVIEW = "interview"
    SHORTLISTED = "shortlisted"
    CLIENT_REVIEW = "client_review"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    BLACKLISTED = "blacklisted"

class Candidate(db.Model):
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    gender = Column(Enum(Gender))
    address = Column(String(255))
    city = Column(String(100))
    province = Column(String(100))
    country = Column(String(100), default="Vietnam")
    
    # Education and skills
    education_level = Column(Enum(EducationLevel))
    major = Column(String(100))
    university = Column(String(200))
    skills = Column(Text)
    languages = Column(String(255))
    years_of_experience = Column(Float)
    
    # Resume and documents
    resume_url = Column(String(255))
    portfolio_url = Column(String(255))
    
    # Current employment
    current_employer = Column(String(200))
    current_position = Column(String(100))
    current_salary = Column(Float)
    expected_salary = Column(Float)
    
    # Recruitment data
    status = Column(Enum(CandidateStatus), default=CandidateStatus.NEW)
    source = Column(String(100))  # Where the candidate came from
    notes = Column(Text)
    
    # Metrics for analytics
    quality_score = Column(Float)  # Calculated score based on various factors
    last_contact_date = Column(DateTime)
    
    # Timestamps for data-aging analysis
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    applications = relationship("Application", back_populates="candidate")
    interviews = relationship("Interview", back_populates="candidate")
    
    def __repr__(self):
        return f"<Candidate {self.full_name}>"
