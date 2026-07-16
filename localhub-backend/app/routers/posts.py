from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("", response_model=schemas.PostListResponse)
def list_posts(
    category: str | None = None,
    keyword: str | None = None,
    sort: str = Query("latest", pattern="^(latest|rating|views)$"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    location_id: str | None = None,
    db: Session = Depends(get_db),
):
    """게시글 목록 (카테고리 필터 / 검색 / 정렬 / 페이지네이션 / 장소별 리뷰 필터)."""
    total, items = crud.get_posts(db, category, keyword, sort, page, size, location_id)
    return {"total": total, "page": page, "size": size, "items": items}


@router.get("/{post_id}", response_model=schemas.PostDetail)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """상세 조회 (조회수 +1)."""
    post = crud.get_post_and_increment_view(db, post_id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "게시글을 찾을 수 없습니다.")
    return post


@router.post("", response_model=schemas.PostDetail, status_code=201)
def create_post(data: schemas.PostCreate, db: Session = Depends(get_db)):
    """게시글 작성 (제목·내용·비밀번호·평점)."""
    return crud.create_post(db, data)


@router.put("/{post_id}", response_model=schemas.PostDetail)
def update_post(
    post_id: int, data: schemas.PostUpdate, db: Session = Depends(get_db)
):
    """수정 — 비밀번호 평문 일치 확인 (RFP 의도된 설계)."""
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "게시글을 찾을 수 없습니다.")
    if post.password != data.password:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "비밀번호가 일치하지 않습니다.")
    return crud.update_post(db, post, data)


@router.post("/{post_id}/delete", status_code=204)
def delete_post(
    post_id: int, body: schemas.PasswordCheck, db: Session = Depends(get_db)
):
    """
    삭제 — 비밀번호 확인.
    DELETE 대신 POST /delete 를 쓰는 이유: DELETE 메서드는 body 전송이
    클라이언트/프록시에 따라 무시될 수 있어, 비밀번호를 안전히 보내기 위함.
    """
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "게시글을 찾을 수 없습니다.")
    if post.password != body.password:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "비밀번호가 일치하지 않습니다.")
    crud.delete_post(db, post)
