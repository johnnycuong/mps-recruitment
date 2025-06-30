from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Float, Date
from sqlalchemy.orm import relationship
import enum
import datetime
from .user import db

class JobType(enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"

class JobLevel(enum.Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"

class JobStatus(enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    ON_HOLD = "on_hold"
    FILLED = "filled"

class JobPosition(db.Model):
    __tablename__ = 'job_positions'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    responsibilities = Column(Text)
    benefits = Column(Text)
    
    # Job details
    job_type = Column(Enum(JobType), default=JobType.FULL_TIME)
    job_level = Column(Enum(JobLevel))
    location = Column(String(200))
    remote_option = Column(Boolean, default=False)
    department = Column(String(100))
    
    # Compensation
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10), default="VND")
    salary_is_public = Column(Boolean, default=False)
    
    # Recruitment details
    vacancies = Column(Integer, default=1)
    status = Column(Enum(JobStatus), default=JobStatus.DRAFT)
    start_date = Column(Date)
    end_date = Column(Date)
    priority = Column(Integer, default=1)  # 1-5, 5 being highest
    
    # Metrics for analytics
    views_count = Column(Integer, default=0)
    applications_count = Column(Integer, default=0)
    time_to_fill = Column(Integer)  # Days to fill the position
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="job_positions")
    applications = relationship("Application", back_populates="job_position")
    
    def __repr__(self):
        return f"<JobPosition {self.title}>"
