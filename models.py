from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    segments = relationship("UserSegment", back_populates="user")

class Segment(Base):
    __tablename__ = "segments"
    slug = Column(String, primary_key=True, index=True)
    description = Column(String, nullable=True)
    users = relationship("UserSegment", back_populates="segment")

class UserSegment(Base):
    __tablename__ = "user_segments"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    segment_slug = Column(String, ForeignKey("segments.slug"), primary_key=True)
    user = relationship("User", back_populates="segments")
    segment = relationship("Segment", back_populates="users")