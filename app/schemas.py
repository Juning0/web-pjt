from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ---------- Location (읽기 전용) ----------
class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content_id: str
    category: str
    title: str
    addr1: str
    tel: str
    lng: Optional[float]
    lat: Optional[float]
    first_image: str


class LocationDetailOut(LocationOut):
    """상세 조회 시 평균 평점/리뷰 수 포함."""
    avg_rating: Optional[float] = None
    review_count: int = 0


# ---------- Comment ----------
class CommentCreate(BaseModel):
    content: str = Field(min_length=1)
    password: str = Field(min_length=1)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    content: str
    created_at: datetime
    # password 는 응답에 절대 포함하지 않음


class PasswordCheck(BaseModel):
    """수정/삭제 시 비밀번호 확인용."""
    password: str = Field(min_length=1)


# ---------- Post ----------
class PostCreate(BaseModel):
    category: str
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    password: str = Field(min_length=1)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    location_id: Optional[str] = None


class PostUpdate(BaseModel):
    """비밀번호 + 수정할 내용."""
    password: str = Field(min_length=1)
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    content: Optional[str] = Field(default=None, min_length=1)
    rating: Optional[int] = Field(default=None, ge=1, le=5)


class PostListItem(BaseModel):
    """목록용 (본문 제외)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    title: str
    rating: Optional[int]
    view_count: int
    created_at: datetime


class PostDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    title: str
    content: str
    rating: Optional[int]
    view_count: int
    location_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    comments: list[CommentOut] = []


class PostListResponse(BaseModel):
    """페이지네이션 응답."""
    total: int
    page: int
    size: int
    items: list[PostListItem]
