from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app import models, schemas


# ---------- Location ----------
def get_locations(
    db: Session, category: str | None = None, keyword: str | None = None,
    skip: int = 0, limit: int = 20, sort: str = "default",
):
    q = db.query(models.Location)
    if category:
        q = q.filter(models.Location.category == category)
    if keyword:
        q = q.filter(models.Location.title.contains(keyword))

    if sort in ("rating", "recent"):
        # 장소별 리뷰 집계(평균 평점/리뷰 수/최근 리뷰 시각)를 한 번만 구해서 outer join한다.
        # outer join이라 리뷰가 없는 장소도 그대로 남고, 집계값은 NULL이 된다.
        review_agg = (
            db.query(
                models.Post.location_id.label("location_id"),
                func.avg(models.Post.rating).label("avg_rating"),
                func.count(models.Post.id).label("review_count"),
                func.max(models.Post.created_at).label("last_review_at"),
            )
            .filter(models.Post.location_id.isnot(None), models.Post.rating.isnot(None))
            .group_by(models.Post.location_id)
            .subquery()
        )
        q = q.outerjoin(review_agg, models.Location.content_id == review_agg.c.location_id)
        # 리뷰 기준으로 동점(특히 리뷰가 아예 없는 장소끼리)일 때는, 카드에 사진이라도
        # 뜨는 장소를 먼저 보여준다. 그 다음에도 동점이면 content_id로 결정한다.
        has_image = models.Location.first_image.isnot(None) & (models.Location.first_image != "")
        if sort == "rating":
            # SQLite는 정렬 시 NULL을 맨 뒤로 보내므로, 리뷰 없는 장소는 자연스럽게 뒤로 밀린다.
            q = q.order_by(
                desc(review_agg.c.avg_rating),
                desc(review_agg.c.review_count),
                desc(has_image),
                models.Location.content_id,
            )
        else:  # recent — 최근에 리뷰가 달린 장소부터
            q = q.order_by(
                desc(review_agg.c.last_review_at),
                desc(has_image),
                models.Location.content_id,
            )

    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return total, items


def get_location(db: Session, content_id: str):
    return db.query(models.Location).filter(
        models.Location.content_id == content_id
    ).first()


def get_location_rating(db: Session, content_id: str):
    """장소별 평균 평점 + 리뷰 수 집계."""
    row = (
        db.query(
            func.avg(models.Post.rating).label("avg_rating"),
            func.count(models.Post.id).label("cnt"),
        )
        .filter(
            models.Post.location_id == content_id,
            models.Post.rating.isnot(None),
        )
        .one()
    )
    avg = round(row.avg_rating, 2) if row.avg_rating is not None else None
    return avg, row.cnt


# ---------- Post ----------
def get_posts(
    db: Session, category: str | None = None, keyword: str | None = None,
    sort: str = "latest", page: int = 1, size: int = 10,
    location_id: str | None = None,
):
    q = db.query(models.Post)
    if category:
        q = q.filter(models.Post.category == category)
    if keyword:
        # 제목 또는 내용 검색 (선택기능: 게시글 검색)
        q = q.filter(
            models.Post.title.contains(keyword)
            | models.Post.content.contains(keyword)
        )
    if location_id:
        # 특정 장소에 달린 리뷰만 조회 (장소 상세 모달의 리뷰 목록용)
        q = q.filter(models.Post.location_id == location_id)

    total = q.count()

    if sort == "rating":          # 평점순
        q = q.order_by(desc(models.Post.rating), desc(models.Post.created_at))
    elif sort == "views":         # 조회순
        q = q.order_by(desc(models.Post.view_count))
    else:                          # 최신순 (기본)
        q = q.order_by(desc(models.Post.created_at))

    items = q.offset((page - 1) * size).limit(size).all()
    return total, items


def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def get_post_and_increment_view(db: Session, post_id: int):
    """상세 조회 시 조회수 +1 (선택기능: 조회수)."""
    post = get_post(db, post_id)
    if post:
        post.view_count += 1
        db.commit()
        db.refresh(post)
    return post


def create_post(db: Session, data: schemas.PostCreate):
    post = models.Post(**data.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(db: Session, post: models.Post, data: schemas.PostUpdate):
    if data.title is not None:
        post.title = data.title
    if data.content is not None:
        post.content = data.content
    if data.rating is not None:
        post.rating = data.rating
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post: models.Post):
    db.delete(post)
    db.commit()


# ---------- Comment ----------
def create_comment(db: Session, post_id: int, data: schemas.CommentCreate):
    comment = models.Comment(post_id=post_id, **data.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).filter(
        models.Comment.id == comment_id
    ).first()


def delete_comment(db: Session, comment: models.Comment):
    db.delete(comment)
    db.commit()
