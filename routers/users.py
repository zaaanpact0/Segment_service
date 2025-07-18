from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User as UserModel, UserSegment, Segment as SegmentModel
from ..schemas import (
    User,
    UserCreate,
    UserSegmentAssign,
    UserWithSegments
)

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/", response_model=User)
def create_user(
        user: UserCreate,
        db: Session = Depends(get_db)
):
    """Создание нового пользователя"""
    db_user = db.query(UserModel).filter(UserModel.id == user.id).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail=f"User with ID {user.id} already exists"
        )

    new_user = UserModel(id=user.id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=List[User])
def get_all_users(db: Session = Depends(get_db)):
    """Получение списка всех пользователей"""
    return db.query(UserModel).all()


@router.get("/{user_id}", response_model=UserWithSegments)
def get_user(
        user_id: int,
        db: Session = Depends(get_db)
):
    """Получение информации о пользователе с его сегментами"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )

    segments = db.query(SegmentModel) \
        .join(UserSegment) \
        .filter(UserSegment.user_id == user_id) \
        .all()

    return {
        "user": user,
        "segments": segments
    }


@router.post("/assign", response_model=dict)
def assign_user_to_segment(
        data: UserSegmentAssign,
        db: Session = Depends(get_db)
):
    """Добавление пользователя в сегмент"""
    user = db.query(UserModel).filter(UserModel.id == data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {data.user_id} not found"
        )

    segment = db.query(SegmentModel) \
        .filter(SegmentModel.slug == data.segment_slug) \
        .first()
    if not segment:
        raise HTTPException(
            status_code=404,
            detail=f"Segment '{data.segment_slug}' not found"
        )

    existing = db.query(UserSegment) \
        .filter(
        UserSegment.user_id == data.user_id,
        UserSegment.segment_slug == data.segment_slug
    ) \
        .first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"User already in segment '{data.segment_slug}'"
        )


    new_association = UserSegment(
        user_id=data.user_id,
        segment_slug=data.segment_slug
    )
    db.add(new_association)
    db.commit()

    return {
        "message": f"User {data.user_id} added to segment '{data.segment_slug}'",
        "user_id": data.user_id,
        "segment_slug": data.segment_slug
    }


@router.delete("/unassign", response_model=dict)
def unassign_user_from_segment(
        data: UserSegmentAssign,
        db: Session = Depends(get_db)
):
    """Удаление пользователя из сегмента"""
    relation = db.query(UserSegment) \
        .filter(
        UserSegment.user_id == data.user_id,
        UserSegment.segment_slug == data.segment_slug
    ) \
        .first()

    if not relation:
        raise HTTPException(
            status_code=404,
            detail="User is not assigned to this segment"
        )

    db.delete(relation)
    db.commit()

    return {
        "message": f"User {data.user_id} removed from segment '{data.segment_slug}'",
        "user_id": data.user_id,
        "segment_slug": data.segment_slug
    }


@router.get("/{user_id}/segments", response_model=List[str])
def get_user_segments(
        user_id: int,
        db: Session = Depends(get_db)
):
    """Получение списка сегментов пользователя"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )

    segments = db.query(SegmentModel.slug) \
        .join(UserSegment) \
        .filter(UserSegment.user_id == user_id) \
        .all()

    return [segment.slug for segment in segments]