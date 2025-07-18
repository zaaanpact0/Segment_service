from typing import List, Optional
from pydantic import BaseModel, Field, confloat
from datetime import datetime

# --- User schemas ---
class SegmentInUser(BaseModel):
    id: int
    name: str
    slug: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    id: Optional[int] = None

class User(UserBase):
    id: int
    segments: List[SegmentInUser] = []
    created_at: datetime

    class Config:
        orm_mode = True

# --- Segment schemas ---
class UserInSegment(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        orm_mode = True

class SegmentBase(BaseModel):
    name: str
    slug: str = Field(..., regex=r'^[A-Z0-9_]+$', max_length=50)
    description: Optional[str] = Field(None, max_length=200)

class SegmentCreate(SegmentBase):
    pass

class Segment(SegmentBase):
    id: int
    users: List[UserInSegment] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Assignment schemas ---
class UserSegmentCreate(BaseModel):
    user_id: int
    segment_id: int

class UserSegmentResponse(BaseModel):
    user_id: int
    segment_id: int
    assigned_at: datetime

    class Config:
        orm_mode = True

# --- Distribution schemas ---
class SegmentDistributionRequest(BaseModel):
    segment_id: int
    percent: confloat(ge=0, le=100) = Field(..., example=30.0)
    overwrite_existing: bool = Field(False, description="Remove existing assignments if True")
    active_only: bool = Field(True, description="Distribute only among active users")

class DistributedUser(BaseModel):
    user_id: int
    user_name: str
    assigned: bool
    already_assigned: bool = False

    class Config:
        orm_mode = True

class SegmentDistributionResponse(BaseModel):
    segment_id: int
    segment_name: str
    requested_percent: float
    actual_percent: float
    total_users: int
    eligible_users: int
    newly_assigned: int
    already_assigned: int
    users: List[DistributedUser]

    class Config:
        orm_mode = True

# --- Statistics schemas ---
class SegmentStats(BaseModel):
    segment_id: int
    segment_name: str
    user_count: int
    last_assigned_at: Optional[datetime]

class UserStats(BaseModel):
    user_id: int
    user_name: str
    segment_count: int
    last_segment_added_at: Optional[datetime]