from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
import enum
import datetime
from .user import db

class InterviewType(enum.Enum):
    PHONE = "phone"
    VIDEO = "video"
    IN_PERSON = "in_person"
    TECHNICAL = "technical"
    GROUP = "group"
    ASSESSMENT = "assessment"

class InterviewStatus(enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"

class Interview(db.Model):
    __tablename__ = 'interviews'
    
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'), nullable=False)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    
    # Interview details
    interview_type = Column(Enum(InterviewType), default=InterviewType.PHONE)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.SCHEDULED)
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    location = Column(String(255))
    meeting_link = Column(String(255))
    
    # Interviewers
    interviewer_id = Column(Integer, ForeignKey('users.id'))
    client_interviewer_id = Column(Integer, ForeignKey('users.id'))
    
    # Feedback
    technical_score = Column(Float)  # 0-5 rating
    communication_score = Column(Float)  # 0-5 rating
    culture_fit_score = Column(Float)  # 0-5 rating
    overall_score = Column(Float)  # 0-5 rating
    strengths = Column(Text)
    weaknesses = Column(Text)
    notes = Column(Text)
    recommendation = Column(String(50))  # Hire, Reject, Consider
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    application = relationship("Application", back_populates="interviews")
    candidate = relationship("Candidate", back_populates="interviews")
    interviewer = relationship("User", foreign_keys=[interviewer_id])
    client_interviewer = relationship("User", foreign_keys=[client_interviewer_id])
    
    def __repr__(self):
        return f"<Interview {self.id} - {self.status.value}>"
