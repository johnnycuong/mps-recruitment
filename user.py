from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
import datetime

db = SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"
    MANAGER = "manager"
    CLIENT = "client"
    PARTNER = "partner"
    COLLABORATOR = "collaborator"

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="user", uselist=False)
    partner = relationship("Partner", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User {self.username}>"
