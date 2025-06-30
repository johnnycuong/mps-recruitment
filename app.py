from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
import enum
import datetime
from .user import db
from .candidate import CandidateStatus

class ApplicationStatus(enum.Enum):
    NEW = "new"
    SCREENING = "screening"
    INTERVIEW = "interview"
    SHORTLISTED = "shortlisted"
    CLIENT_REVIEW = "client_review"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    job_position_id = Column(Integer, ForeignKey('job_positions.id'), nullable=False)
    
    # Application details
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.NEW)
    cover_letter = Column(Text)
    expected_salary = Column(Float)
    availability_date = Column(DateTime)
    
    # Recruiter assessment
    recruiter_id = Column(Integer, ForeignKey('users.id'))
    recruiter_notes = Column(Text)
    candidate_score = Column(Float)  # 0-100 score
    
    # Tracking
    current_stage = Column(String(50), default="Applied")
    is_active = Column(Boolean, default=True)
    
    # Timestamps for workflow tracking
    applied_at = Column(DateTime, default=datetime.datetime.utcnow)
    screened_at = Column(DateTime)
    interviewed_at = Column(DateTime)
    shortlisted_at = Column(DateTime)
    client_reviewed_at = Column(DateTime)
    hired_at = Column(DateTime)
    rejected_at = Column(DateTime)
    withdrawn_at = Column(DateTime)
    
    # Metrics for analytics
    time_to_screen = Column(Integer)  # Hours from application to screening
    time_to_interview = Column(Integer)  # Hours from screening to interview
    time_to_decision = Column(Integer)  # Hours from interview to decision
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job_position = relationship("JobPosition", back_populates="applications")
    recruiter = relationship("User", foreign_keys=[recruiter_id])
    interviews = relationship("Interview", back_populates="application")
    
    def __repr__(self):
        return f"<Application {self.id} - {self.status.value}>"
    
    def update_candidate_status(self):
        """Update the candidate status based on application status"""
        if self.status == ApplicationStatus.NEW:
            self.candidate.status = CandidateStatus.NEW
        elif self.status == ApplicationStatus.SCREENING:
            self.candidate.status = CandidateStatus.SCREENING
        elif self.status == ApplicationStatus.INTERVIEW:
            self.candidate.status = CandidateStatus.INTERVIEW
        elif self.status == ApplicationStatus.SHORTLISTED:
            self.candidate.status = CandidateStatus.SHORTLISTED
        elif self.status == ApplicationStatus.CLIENT_REVIEW:
            self.candidate.status = CandidateStatus.CLIENT_REVIEW
        elif self.status == ApplicationStatus.HIRED:
            self.candidate.status = CandidateStatus.HIRED
        elif self.status == ApplicationStatus.REJECTED:
            self.candidate.status = CandidateStatus.REJECTED
        elif self.status == ApplicationStatus.WITHDRAWN:
            self.candidate.status = CandidateStatus.WITHDRAWN
