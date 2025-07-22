from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    user_segments = relationship("UserSegment", back_populates="user", cascade="all, delete-orphan")
    segments = association_proxy("user_segments", "segment")

class Segment(Base):
    __tablename__ = "segments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    user_segments = relationship("UserSegment", back_populates="segment", cascade="all, delete-orphan")
    users = association_proxy("user_segments", "user")

class UserSegment(Base):
    __tablename__ = "user_segment"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    segment_id = Column(Integer, ForeignKey("segments.id"))

    user = relationship("User", back_populates="user_segments")
    segment = relationship("Segment", back_populates="user_segments")