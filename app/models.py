from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship

from app.database import Base


class Location(Base):
    """
    공공데이터(한국관광공사 TourAPI) POI. 읽기 전용.
    seed.py 가 제공 JSON을 이 테이블에 적재한다.
    """
    __tablename__ = "locations"

    # contentid를 그대로 PK로 사용 (100% 유니크 확인됨)
    content_id = Column(String, primary_key=True, index=True)
    content_type_id = Column(String, nullable=False)     # 12, 14, 15, ...
    category = Column(String, nullable=False, index=True)  # 관광지/음식점/축제공연행사 ...

    title = Column(String, nullable=False)
    addr1 = Column(String, default="")   # 여행코스는 비어있을 수 있음
    addr2 = Column(String, default="")
    zipcode = Column(String, default="")
    tel = Column(String, default="")     # 축제 외에는 대부분 빔

    # mapx=경도(lng), mapy=위도(lat). 원본은 string이라 float로 변환해 저장
    lng = Column(Float)
    lat = Column(Float)

    first_image = Column(String, default="")   # 빈 문자열이면 이미지 없음
    first_image2 = Column(String, default="")

    created_time = Column(String, default="")   # 원본 YYYYMMDDHHmmss 보존
    modified_time = Column(String, default="")

    # 이 장소에 달린 리뷰 게시글
    posts = relationship("Post", back_populates="location")


class Post(Base):
    """
    커뮤니티 리뷰 게시글. 익명 + 수정용 비밀번호(평문, RFP 의도된 설계).
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False, index=True)  # 어떤 카테고리 게시판인지

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    # 평문 저장 — 암호화하지 않음 (RFP III-2-나: 교육 목적 의도된 설계)
    password = Column(String, nullable=False)

    rating = Column(Integer)   # 1~5, 선택 입력 (없을 수 있음)
    view_count = Column(Integer, default=0, nullable=False)

    # 어떤 장소에 대한 리뷰인지 (선택). 장소별 평균 평점 집계에 사용
    location_id = Column(
        String, ForeignKey("locations.content_id"), nullable=True, index=True
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    location = relationship("Location", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )


class Comment(Base):
    """게시글 댓글. 익명 + 수정용 비밀번호(평문)."""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(
        Integer, ForeignKey("posts.id"), nullable=False, index=True
    )
    content = Column(Text, nullable=False)
    password = Column(String, nullable=False)   # 평문 (게시글과 동일 정책)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    post = relationship("Post", back_populates="comments")


# 목록 조회 성능용 복합 인덱스 (카테고리별 최신순 조회가 잦음)
Index("ix_posts_category_created", Post.category, Post.created_at.desc())
