from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("", response_model=dict)
def list_locations(
    category: str | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    공공데이터(POI) 목록 — 읽기 전용.
    category 예: 관광지 / 음식점 / 축제공연행사 / 문화시설 / 쇼핑 / 숙박 / 레포츠 / 여행코스
    """
    total, items = crud.get_locations(
        db, category, keyword, skip=(page - 1) * size, limit=size
    )
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": [schemas.LocationOut.model_validate(i) for i in items],
    }


@router.get("/{content_id}", response_model=schemas.LocationDetailOut)
def get_location(content_id: str, db: Session = Depends(get_db)):
    """공공데이터 상세 — 장소별 평균 평점/리뷰 수 포함."""
    loc = crud.get_location(db, content_id)
    if not loc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "장소를 찾을 수 없습니다.")
    avg, cnt = crud.get_location_rating(db, content_id)
    out = schemas.LocationDetailOut.model_validate(loc)
    out.avg_rating = avg
    out.review_count = cnt
    return out
