from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
import enum
import datetime
from .user import db

class PartnerType(enum.Enum):
    SCHOOL = "school"
    RECRUITMENT_AGENCY = "recruitment_agency"
    TRAINING_CENTER = "training_center"
    COMMUNITY_ORGANIZATION = "community_organization"
    OTHER = "other"

class PartnerStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    POTENTIAL = "potential"
    FORMER = "former"

class Partner(db.Model):
    __tablename__ = 'partners'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    name = Column(String(200), nullable=False)
    partner_type = Column(Enum(PartnerType), nullable=False)
    status = Column(Enum(PartnerStatus), default=PartnerStatus.ACTIVE)
    
    # Contact information
    address = Column(String(255))
    city = Column(String(100))
    province = Column(String(100))
    country = Column(String(100), default="Vietnam")
    website = Column(String(255))
    primary_contact_name = Column(String(100))
    primary_contact_email = Column(String(100))
    primary_contact_phone = Column(String(20))
    
    # Partnership details
    description = Column(Text)
    specialization = Column(String(255))
    agreement_details = Column(Text)
    commission_rate = Column(Float)
    
    # Metrics for analytics
    quality_rating = Column(Float, default=0.0)  # 0-5 rating
    candidates_provided_count = Column(Integer, default=0)
    successful_placements_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # percentage
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="partner")
    
    def __repr__(self):
        return f"<Partner {self.name}>"
