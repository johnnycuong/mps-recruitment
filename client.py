from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
import enum
import datetime
from .user import db

class ClientType(enum.Enum):
    FDI = "fdi"
    DOMESTIC = "domestic"
    GOVERNMENT = "government"
    NGO = "ngo"
    OTHER = "other"

class ClientStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    POTENTIAL = "potential"
    FORMER = "former"

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100))
    client_type = Column(Enum(ClientType), default=ClientType.FDI)
    status = Column(Enum(ClientStatus), default=ClientStatus.ACTIVE)
    address = Column(String(255))
    city = Column(String(100))
    country = Column(String(100))
    website = Column(String(255))
    description = Column(Text)
    employee_count = Column(Integer)
    
    # Contact information
    primary_contact_name = Column(String(100))
    primary_contact_email = Column(String(100))
    primary_contact_phone = Column(String(20))
    
    # Metrics for analytics
    quality_rating = Column(Float, default=0.0)  # 0-5 rating
    response_time_avg = Column(Float)  # in hours
    hire_success_rate = Column(Float)  # percentage
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="client")
    job_positions = relationship("JobPosition", back_populates="client")
    
    def __repr__(self):
        return f"<Client {self.company_name}>"
