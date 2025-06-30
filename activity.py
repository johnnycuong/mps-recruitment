from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Float, JSON
from sqlalchemy.orm import relationship
import enum
import datetime
from .user import db

class ActivityType(enum.Enum):
    STATUS_CHANGE = "status_change"
    NOTE_ADDED = "note_added"
    DOCUMENT_ADDED = "document_added"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    EMAIL_SENT = "email_sent"
    SYSTEM_ACTION = "system_action"
    OTHER = "other"

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=True)
    application_id = Column(Integer, ForeignKey('applications.id'), nullable=True)
    job_position_id = Column(Integer, ForeignKey('job_positions.id'), nullable=True)
    
    # Activity details
    activity_type = Column(Enum(ActivityType), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(JSON)  # Store additional structured data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<Activity {self.id} - {self.activity_type.value}>"
