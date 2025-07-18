from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Segment as SegmentModel, UserSegment, User as UserModel
from ..schemas import Segment, SegmentCreate, SegmentDistribution

router = APIRouter(
    prefix="/segments",
    tags=["segments"]
)


@router.post("/", response_model=Segment)
def create_segment(segment: SegmentCreate, db: Session = Depends(get_db)):
    """Создание нового сегмента"""
    db_segment = db.query(SegmentModel).filter(SegmentModel.slug == segment.slug).first()
    if db_segment:
        raise HTTPException(status_code=400, detail="Segment already exists")

    new_segment = SegmentModel(
        slug=segment.slug,
        description=segment.description
    )
    db.add(new_segment)
    db.commit()
    db.refresh(new_segment)
    return new_segment


@router.get("/", response_model=List[Segment])
def get_all_segments(db: Session = Depends(get_db)):
    """Получение списка всех сегментов"""
    return db.query(SegmentModel).all()


@router.delete("/{slug}")
def delete_segment(slug: str, db: Session = Depends(get_db)):
    """Удаление сегмента"""
    segment = db.query(SegmentModel).filter(SegmentModel.slug == slug).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    # Удаляем все связи пользователей с этим сегментом
    db.query(UserSegment).filter(UserSegment.segment_slug == slug).delete()
    db.delete(segment)
    db.commit()
    return {"message": "Segment and its user relations deleted"}


@router.get("/{slug}/users", response_model=List[int])
def get_users_in_segment(slug: str, db: Session = Depends(get_db)):
    """Получение списка ID пользователей в сегменте"""
    segment = db.query(SegmentModel).filter(SegmentModel.slug == slug).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    return [us.user_id for us in segment.users]


@router.post("/{slug}/distribute")
def distribute_segment(
        slug: str,
        distribution: SegmentDistribution,
        db: Session = Depends(get_db)
):
    """Распределение сегмента на процент пользователей"""
    segment = db.query(SegmentModel).filter(SegmentModel.slug == slug).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    if not 0 <= distribution.percent <= 100:
        raise HTTPException(status_code=400, detail="Percent must be between 0 and 100")

    # Получаем всех пользователей
    all_users = db.query(UserModel).all()
    if not all_users:
        return {"message": "No users available for distribution"}

    user_count = len(all_users)
    users_to_add = int(user_count * distribution.percent / 100)

    selected_users = random.sample(all_users, users_to_add)

    added_count = 0
    for user in selected_users:
        existing = db.query(UserSegment).filter(
            UserSegment.user_id == user.id,
            UserSegment.segment_slug == slug
        ).first()

        if not existing:
            new_association = UserSegment(
                user_id=user.id,
                segment_slug=slug
            )
            db.add(new_association)
            added_count += 1

    db.commit()
    return {
        "message": f"Segment distributed to {added_count} users",
        "total_users": user_count,
        "users_added": added_count,
        "percent_achieved": (added_count / user_count) * 100 if user_count else 0
    }