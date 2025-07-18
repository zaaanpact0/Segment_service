from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
from typing import Dict, List
from ..database import get_db
from ..models import User, Segment, UserSegment
from ..schemas import (
    SegmentDistributionRequest,
    SegmentDistributionResponse,
    UserSegmentDetail
)

router = APIRouter(
    prefix="/distribute",
    tags=["distribution"]
)


@router.post("/", response_model=SegmentDistributionResponse)
def distribute_segment(
        data: SegmentDistributionRequest,
        db: Session = Depends(get_db)
):
    """
    Распределение сегмента на указанный процент пользователей

    Параметры:
    - segment_slug: идентификатор сегмента
    - percent: процент пользователей для распределения (0-100)
    - overwrite: перезаписать существующие связи (по умолчанию False)
    """

    segment = db.query(Segment).filter(Segment.slug == data.segment_slug).first()
    if not segment:
        raise HTTPException(
            status_code=404,
            detail=f"Segment '{data.segment_slug}' not found"
        )

    if not 0 <= data.percent <= 100:
        raise HTTPException(
            status_code=400,
            detail="Percent must be between 0 and 100"
        )

    all_users = db.query(User).all()
    if not all_users:
        return {
            "message": "No users available for distribution",
            "segment_slug": data.segment_slug,
            "users_added": []
        }

    existing_users = set()
    if not data.overwrite:
        existing_users = {
            us.user_id for us in
            db.query(UserSegment).filter(UserSegment.segment_slug == data.segment_slug).all()
        }

    eligible_users = [
        user for user in all_users
        if user.id not in existing_users
    ]

    user_count = len(eligible_users)
    users_to_add = int(user_count * data.percent / 100)

    selected_users = random.sample(eligible_users, users_to_add) if users_to_add > 0 else []

    added_users = []
    for user in selected_users:
        new_link = UserSegment(
            user_id=user.id,
            segment_slug=data.segment_slug
        )
        db.add(new_link)
        added_users.append(UserSegmentDetail(
            user_id=user.id,
            segment_slug=data.segment_slug
        ))

    db.commit()

    return {
        "message": f"Segment '{data.segment_slug}' distributed to {len(added_users)} users",
        "segment_slug": data.segment_slug,
        "total_users": len(all_users),
        "eligible_users": user_count,
        "users_added": added_users,
        "percent_achieved": round((len(added_users) / len(all_users)) * 100, 2) if all_users else 0,
        "requested_percent": data.percent
    }